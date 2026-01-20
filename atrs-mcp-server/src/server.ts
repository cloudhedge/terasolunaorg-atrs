import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { loadConfig } from './config.js';
import { AtrsApiClient } from './api/client.js';
import { airports, findAirport } from './data/airports.js';
import { fareTypes } from './data/fare-types.js';
import type { FareTypeCd } from './api/types.js';

/**
 * Create and configure the MCP server for ATRS
 */
export function createServer(): McpServer {
  const config = loadConfig();
  const apiClient = new AtrsApiClient(config);

  const server = new McpServer({
    name: 'atrs-mcp-server',
    version: '1.0.0',
  });

  // ========== Tool 1: search_flights ==========
  server.tool(
    'search_flights',
    'Search for available flights between airports. Returns flight options with fares and seat availability.',
    {
      from: z.string().describe('Departure airport code (e.g., HND, NRT) or city name (e.g., Tokyo)'),
      to: z.string().describe('Arrival airport code (e.g., KIX, ITM) or city name (e.g., Osaka)'),
      date: z.string().describe('Departure date in yyyy/MM/dd format (e.g., 2025/01/15)'),
      flightType: z
        .enum(['OW', 'RT'])
        .default('OW')
        .describe('OW=one-way, RT=round-trip'),
      seatClass: z
        .enum(['N', 'S'])
        .default('N')
        .describe('N=normal/economy, S=special/premium'),
    },
    async ({ from, to, date, flightType = 'OW', seatClass = 'N' }) => {
      try {
        // Resolve airport codes from city names
        const depAirport = findAirport(from);
        const arrAirport = findAirport(to);

        if (!depAirport) {
          return {
            content: [
              {
                type: 'text' as const,
                text: `Unknown departure airport: "${from}". Use list_airports to see valid options.`,
              },
            ],
            isError: true,
          };
        }
        if (!arrAirport) {
          return {
            content: [
              {
                type: 'text' as const,
                text: `Unknown arrival airport: "${to}". Use list_airports to see valid options.`,
              },
            ],
            isError: true,
          };
        }

        const flights = await apiClient.searchFlights({
          depAirportCd: depAirport.code,
          arrAirportCd: arrAirport.code,
          depDate: date,
          flightType: flightType,
          boardingClassCd: seatClass,
        });

        if (flights.length === 0) {
          return {
            content: [
              {
                type: 'text' as const,
                text: `No flights found from ${depAirport.nameEn} to ${arrAirport.nameEn} on ${date}.`,
              },
            ],
          };
        }

        // Format results for AI
        const formatted = flights.map((f) => ({
          flight: f.flightName,
          route: `${f.depAirportName} → ${f.arrAirportName}`,
          departure: f.depTime,
          arrival: f.arrTime,
          date: f.depDate,
          seatClass: f.boardingClassCd === 'N' ? 'Economy' : 'Premium',
          fares: Object.entries(f.fareTypes).map(([code, fare]) => ({
            type: fare.fareTypeName,
            code,
            price: `¥${fare.fare}`,
            seatsAvailable: fare.vacantNum,
          })),
        }));

        return {
          content: [
            {
              type: 'text' as const,
              text: JSON.stringify(formatted, null, 2),
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text' as const, text: `Flight search failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 2: check_reservation ==========
  server.tool(
    'check_reservation',
    'Check if a reservation number exists in the system',
    {
      reservationNumber: z.string().describe('The reservation number to check'),
    },
    async ({ reservationNumber }) => {
      try {
        const exists = await apiClient.checkReservation(reservationNumber);
        return {
          content: [
            {
              type: 'text' as const,
              text: exists
                ? `Reservation ${reservationNumber} exists and is valid.`
                : `Reservation ${reservationNumber} not found.`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text' as const, text: `Reservation check failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 3: reserve_ticket ==========
  server.tool(
    'reserve_ticket',
    'Reserve a flight ticket for passengers. Names should be in Katakana (Japanese) or the LLM should convert English names to Katakana.',
    {
      flightName: z.string().describe('Flight name (e.g., NTT001)'),
      departureDate: z.string().describe('Departure date in yyyy/MM/dd format'),
      fareType: z
        .string()
        .describe('Fare type code: OW, RT, RD1, RD7, ED, LD, GD, SOW, SRT, SRD'),
      seatClass: z
        .enum(['N', 'S'])
        .default('N')
        .describe('N=normal/economy, S=special/premium'),
      flightType: z
        .enum(['OW', 'RT'])
        .default('OW')
        .describe('OW=one-way, RT=round-trip'),
      passengers: z
        .array(
          z.object({
            familyName: z.string().describe('Family name in Katakana (e.g., タナカ)'),
            givenName: z.string().describe('Given name in Katakana (e.g., タロウ)'),
            age: z.number().describe('Age'),
            gender: z.enum(['M', 'F']).describe('M=male, F=female'),
          })
        )
        .describe('List of passengers'),
      contact: z
        .object({
          familyName: z.string().describe('Contact family name in Katakana'),
          givenName: z.string().describe('Contact given name in Katakana'),
          age: z.number().describe('Contact age'),
          gender: z.enum(['M', 'F']).describe('Contact gender'),
          phone: z.string().describe('Phone number (e.g., 090-1234-5678)'),
          email: z.string().describe('Email address'),
        })
        .describe('Contact person information'),
    },
    async ({
      flightName,
      departureDate,
      fareType,
      seatClass = 'N',
      flightType = 'OW',
      passengers,
      contact,
    }) => {
      try {
        // Parse phone number: 090-1234-5678 → repTel1=090, repTel2=1234, repTel3=5678
        const phoneParts = contact.phone.replace(/[^\d]/g, '');
        let repTel1: string, repTel2: string, repTel3: string;

        if (phoneParts.length === 11) {
          // Mobile: 090-1234-5678
          repTel1 = phoneParts.slice(0, 3);
          repTel2 = phoneParts.slice(3, 7);
          repTel3 = phoneParts.slice(7, 11);
        } else if (phoneParts.length === 10) {
          // Landline: 03-1234-5678
          repTel1 = phoneParts.slice(0, 2);
          repTel2 = phoneParts.slice(2, 6);
          repTel3 = phoneParts.slice(6, 10);
        } else {
          return {
            content: [
              {
                type: 'text' as const,
                text: `Invalid phone format: "${contact.phone}". Use format like 090-1234-5678.`,
              },
            ],
            isError: true,
          };
        }

        const result = await apiClient.reserveTicket({
          repFamilyName: contact.familyName,
          repGivenName: contact.givenName,
          repAge: contact.age,
          repGender: contact.gender,
          repTel1,
          repTel2,
          repTel3,
          repMail: contact.email,
          flightType: flightType,
          selectFlightResourceList: [
            {
              depDate: departureDate,
              flightName: flightName,
              boardingClassCd: seatClass,
              fareTypeCd: fareType as FareTypeCd,
            },
          ],
          passengerResourceList: passengers.map((p) => ({
            familyName: p.familyName,
            givenName: p.givenName,
            age: p.age,
            gender: p.gender,
          })),
        });

        return {
          content: [
            {
              type: 'text' as const,
              text: JSON.stringify(
                {
                  reservationNumber: result.reserveNo,
                  paymentDeadline: result.paymentDate,
                  totalFare: `¥${result.totalFare}`,
                  message: 'Reservation successful!',
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text' as const, text: `Reservation failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 4: list_airports ==========
  server.tool(
    'list_airports',
    'List all available airports with codes and names',
    {
      filter: z.string().optional().describe('Optional filter by name or region'),
    },
    async ({ filter }) => {
      let result = airports;
      if (filter) {
        const f = filter.toLowerCase();
        result = airports.filter(
          (a) =>
            a.code.toLowerCase().includes(f) ||
            a.nameEn.toLowerCase().includes(f) ||
            a.name.includes(filter)
        );
      }

      const formatted = result.map((a) => ({
        code: a.code,
        name: a.nameEn,
        nameJp: a.name,
      }));

      return {
        content: [
          {
            type: 'text' as const,
            text: JSON.stringify(formatted, null, 2),
          },
        ],
      };
    }
  );

  // ========== Tool 5: list_fare_types ==========
  server.tool(
    'list_fare_types',
    'List all available fare types with discounts and requirements',
    {},
    async () => {
      const formatted = fareTypes.map((f) => ({
        code: f.code,
        name: f.nameEn,
        nameJp: f.name,
        discount: `${f.discountRate}%`,
        bookingWindow: `${f.rsrvAvailableEndDayNum}-${f.rsrvAvailableStartDayNum} days before departure`,
        minPassengers: f.passengerMinNum,
        seatClass: f.seatClass === 'N' ? 'Economy' : 'Premium',
      }));

      return {
        content: [
          {
            type: 'text' as const,
            text: JSON.stringify(formatted, null, 2),
          },
        ],
      };
    }
  );

  // ========== Tool 6: login ==========
  server.tool(
    'login',
    'Authenticate with ATRS membership credentials',
    {
      membershipNumber: z.string().describe('10-digit membership number'),
      password: z.string().describe('Account password'),
    },
    async ({ membershipNumber, password }) => {
      try {
        apiClient.setCredentials(membershipNumber, password);
        const isValid = await apiClient.checkAuthStatus();
        if (!isValid) {
          apiClient.clearCredentials();
          return {
            content: [{ type: 'text' as const, text: 'Invalid credentials. Login failed.' }],
            isError: true,
          };
        }
        return {
          content: [{ type: 'text' as const, text: `Logged in as ${membershipNumber}` }],
        };
      } catch (error) {
        apiClient.clearCredentials();
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text' as const, text: `Login failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 7: logout ==========
  server.tool(
    'logout',
    'Clear stored credentials',
    {},
    async () => {
      apiClient.clearCredentials();
      return {
        content: [{ type: 'text' as const, text: 'Logged out successfully.' }],
      };
    }
  );

  // ========== Tool 8: check_auth_status ==========
  server.tool(
    'check_auth_status',
    'Check current authentication status',
    {},
    async () => {
      const hasCredentials = apiClient.isAuthenticated();
      if (!hasCredentials) {
        return {
          content: [
            { type: 'text' as const, text: 'Not authenticated. Use login tool to authenticate.' },
          ],
        };
      }
      try {
        const isValid = await apiClient.checkAuthStatus();
        return {
          content: [
            {
              type: 'text' as const,
              text: isValid
                ? 'Authenticated and credentials are valid.'
                : 'Credentials set but may be invalid.',
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text' as const, text: `Auth check failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 9: check_member ==========
  server.tool(
    'check_member',
    'Check if a membership number is valid/exists',
    {
      membershipNumber: z.string().describe('10-digit membership number'),
    },
    async ({ membershipNumber }) => {
      try {
        const exists = await apiClient.checkMember(membershipNumber);
        return {
          content: [
            {
              type: 'text' as const,
              text: exists
                ? `Membership ${membershipNumber} is valid.`
                : `Membership ${membershipNumber} not found.`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text' as const, text: `Member check failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  return server;
}

/**
 * Start the MCP server with stdio transport
 */
export async function startServer(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);
  console.error('ATRS MCP Server started');
}
