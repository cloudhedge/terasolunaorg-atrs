import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { loadConfig } from './config.js';
import { AtrsApiClient } from './api/client.js';
import { airports } from './data/airports.js';
import { fareTypes } from './data/fare-types.js';

/**
 * Create and configure the MCP server for ATRS
 */
export function createServer(): McpServer {
  const config = loadConfig();
  const apiClient = new AtrsApiClient(config);

  const server = new McpServer({
    name: 'atrs',
    version: '1.0.0',
  });

  // Register search_flights tool
  server.tool(
    'search_flights',
    'Search for available flights between airports',
    {
      from: z.string().describe('Departure airport code (e.g., HND, NRT)'),
      to: z.string().describe('Arrival airport code (e.g., KIX, ITM)'),
      date: z.string().describe('Departure date in yyyy/MM/dd format'),
      flightType: z.enum(['OW', 'RT']).default('OW').describe('OW=one-way, RT=round-trip'),
      seatClass: z.enum(['N', 'S']).default('N').describe('N=standard, S=premium'),
    },
    async ({ from, to, date, flightType, seatClass }) => {
      try {
        const flights = await apiClient.searchFlights({
          depAirportCd: from,
          arrAirportCd: to,
          depDate: date,
          flightType,
          boardingClassCd: seatClass,
        });

        if (flights.length === 0) {
          return {
            content: [{ type: 'text', text: 'No flights found for the specified criteria.' }],
          };
        }

        const formatted = flights.map((f) => ({
          flight: f.flightName,
          from: f.depAirportName,
          to: f.arrAirportName,
          departure: `${f.depDate} ${f.depTime}`,
          arrival: f.arrTime,
          seatClass: f.boardingClassCd === 'N' ? 'Standard' : 'Premium',
          fares: Object.entries(f.fareTypes).map(([code, fare]) => ({
            type: `${fare.fareTypeName} (${code})`,
            price: fare.fare,
            availableSeats: fare.vacantNum,
          })),
        }));

        return {
          content: [{ type: 'text', text: JSON.stringify(formatted, null, 2) }],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Error searching flights: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // Register check_reservation tool
  server.tool(
    'check_reservation',
    'Check if a reservation exists',
    {
      reservationNumber: z.string().describe('The reservation number to check'),
    },
    async ({ reservationNumber }) => {
      try {
        const exists = await apiClient.checkReservation(reservationNumber);
        return {
          content: [
            {
              type: 'text',
              text: exists
                ? `Reservation ${reservationNumber} exists.`
                : `Reservation ${reservationNumber} not found.`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Error checking reservation: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // Register reserve_ticket tool
  server.tool(
    'reserve_ticket',
    'Reserve a flight ticket for passengers',
    {
      flightName: z.string().describe('Flight name (e.g., NH001)'),
      departureDate: z.string().describe('Departure date in yyyy/MM/dd format'),
      fareType: z.string().describe('Fare type code (OW, RT, RD1, RD7, ED, LD, GD)'),
      seatClass: z.enum(['N', 'S']).default('N').describe('N=standard, S=premium'),
      flightType: z.enum(['OW', 'RT']).default('OW').describe('OW=one-way, RT=round-trip'),
      passengers: z
        .array(
          z.object({
            familyName: z.string().describe('Family name (Katakana)'),
            givenName: z.string().describe('Given name (Katakana)'),
            age: z.number().describe('Age'),
            gender: z.enum(['M', 'F']).describe('M=male, F=female'),
          })
        )
        .describe('List of passengers'),
      contact: z
        .object({
          familyName: z.string().describe('Contact family name'),
          givenName: z.string().describe('Contact given name'),
          age: z.number().describe('Contact age'),
          gender: z.enum(['M', 'F']).describe('Contact gender'),
          phone: z.string().describe('Phone number (e.g., 090-1234-5678)'),
          email: z.string().describe('Email address'),
        })
        .describe('Contact person information'),
    },
    async ({ flightName, departureDate, fareType, seatClass, flightType, passengers, contact }) => {
      try {
        // Parse phone number (090-1234-5678 → tel1, tel2, tel3)
        const phoneParts = contact.phone.replace(/[^\d]/g, '');
        const tel1 = phoneParts.slice(0, 3);
        const tel2 = phoneParts.slice(3, 7);
        const tel3 = phoneParts.slice(7, 11);

        const result = await apiClient.reserveTicket({
          repFamilyName: contact.familyName,
          repGivenName: contact.givenName,
          repAge: contact.age,
          repGender: contact.gender,
          repTel1: tel1,
          repTel2: tel2,
          repTel3: tel3,
          repMail: contact.email,
          flightType,
          selectFlightResourceList: [
            {
              depDate: departureDate,
              flightName,
              boardingClassCd: seatClass,
              fareTypeCd: fareType as any,
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
              type: 'text',
              text: JSON.stringify(
                {
                  reservationNumber: result.reserveNo,
                  paymentDeadline: result.paymentDate,
                  totalFare: result.totalFare,
                  passengers: result.passengerResourceList.length,
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
          content: [{ type: 'text', text: `Error reserving ticket: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // Register list_airports tool
  server.tool(
    'list_airports',
    'List all available airports',
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
            a.name.includes(filter) ||
            a.nameEn.toLowerCase().includes(f)
        );
      }

      const formatted = result.map((a) => ({
        code: a.code,
        name: a.nameEn,
        japanese: a.name,
      }));

      return {
        content: [{ type: 'text', text: JSON.stringify(formatted, null, 2) }],
      };
    }
  );

  // Register list_fare_types tool
  server.tool(
    'list_fare_types',
    'List all available fare types with discounts',
    {},
    async () => {
      const formatted = fareTypes.map((f) => ({
        code: f.code,
        name: f.nameEn,
        discount: `${f.discountPercent}%`,
        requirements: f.description,
      }));

      return {
        content: [{ type: 'text', text: JSON.stringify(formatted, null, 2) }],
      };
    }
  );

  // Register login tool
  server.tool(
    'login',
    'Authenticate with membership credentials',
    {
      membershipNumber: z.string().describe('10-digit membership number'),
      password: z.string().describe('Account password'),
    },
    async ({ membershipNumber, password }) => {
      try {
        apiClient.setCredentials(membershipNumber, password);
        // Verify credentials by calling auth status endpoint
        const isValid = await apiClient.checkAuthStatus();
        if (!isValid) {
          apiClient.clearCredentials();
          return {
            content: [{ type: 'text', text: 'Invalid credentials. Login failed.' }],
            isError: true,
          };
        }
        return {
          content: [{ type: 'text', text: `Logged in as ${membershipNumber}` }],
        };
      } catch (error) {
        apiClient.clearCredentials();
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Login failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // Register logout tool
  server.tool(
    'logout',
    'Clear stored credentials',
    {},
    async () => {
      apiClient.clearCredentials();
      return {
        content: [{ type: 'text', text: 'Logged out successfully.' }],
      };
    }
  );

  // Register check_auth_status tool
  server.tool(
    'check_auth_status',
    'Check current authentication status',
    {},
    async () => {
      const hasCredentials = apiClient.isAuthenticated();
      if (!hasCredentials) {
        return {
          content: [{ type: 'text', text: 'Not authenticated. Use login tool to authenticate.' }],
        };
      }
      try {
        const isValid = await apiClient.checkAuthStatus();
        return {
          content: [
            {
              type: 'text',
              text: isValid
                ? 'Authenticated and credentials are valid.'
                : 'Credentials set but may be invalid.',
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Error checking auth: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // Register check_member tool
  server.tool(
    'check_member',
    'Check if a membership number is valid',
    {
      membershipNumber: z.string().describe('10-digit membership number'),
    },
    async ({ membershipNumber }) => {
      try {
        const exists = await apiClient.checkMemberAvailable(membershipNumber);
        return {
          content: [
            {
              type: 'text',
              text: exists
                ? `Membership ${membershipNumber} is valid.`
                : `Membership ${membershipNumber} not found.`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Error checking membership: ${message}` }],
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
