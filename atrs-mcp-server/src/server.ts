import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { loadConfig } from './config.js';
import { AtrsApiClient } from './api/client.js';

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
