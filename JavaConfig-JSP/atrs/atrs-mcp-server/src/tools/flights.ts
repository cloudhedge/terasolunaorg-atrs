/**
 * Flight search tool for ATRS MCP server.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { makeApiRequest, handleApiError } from "../api-client.js";
import { AIRPORT_CODES, CHARACTER_LIMIT } from "../constants.js";

/** Zod schema matching the ATRS FlightSearchQuery parameters. */
const SearchFlightsSchema = z
  .object({
    flightType: z
      .enum(["OW", "RT"])
      .describe("Flight type: OW (one-way) or RT (round-trip)"),
    depAirportCd: z
      .string()
      .length(3)
      .describe("Departure airport code (3-letter, e.g. HND)"),
    arrAirportCd: z
      .string()
      .length(3)
      .describe("Arrival airport code (3-letter, e.g. SPK)"),
    depDate: z
      .string()
      .regex(/^\d{4}\/\d{2}\/\d{2}$/, "Date must be yyyy/MM/dd format")
      .describe("Departure date in yyyy/MM/dd format"),
    boardingClassCd: z
      .enum(["N", "S"])
      .default("N")
      .describe("Boarding class: N (Normal) or S (Special, +5000 yen)"),
  })
  .strict()
  .refine((d) => d.depAirportCd !== d.arrAirportCd, {
    message: "Departure and arrival airports must be different",
  });

type SearchFlightsInput = z.infer<typeof SearchFlightsSchema>;

/** Shape returned by ATRS GET /flight endpoint. */
interface FareTypeResource {
  fareTypeName: string;
  fare: number;
  vacantNum: number;
}

interface FlightResource {
  flightName: string;
  depAirportName: string;
  arrAirportName: string;
  depTime: string;
  arrTime: string;
  depDate: string;
  boardingClassCd: string;
  fareTypes: Record<string, FareTypeResource>;
}

export function registerFlightTools(server: McpServer): void {
  server.registerTool(
    "atrs_search_flights",
    {
      title: "Search ATRS Flights",
      description: `Search for available flights in the Airline Ticket Reservation System.

Returns flight schedules with vacancy counts and fares per fare-type.

Args:
  - flightType (OW | RT): One-way or round-trip
  - depAirportCd (string): 3-letter departure airport code (e.g. HND, NRT, SPK)
  - arrAirportCd (string): 3-letter arrival airport code
  - depDate (string): Departure date in yyyy/MM/dd format (within 90 days)
  - boardingClassCd (N | S): Normal or Special class (default: N)

Returns:
  List of flights with per-fare-type pricing and seat availability.

Note: Departure and arrival airports must be different. Dates beyond 90 days from today are not searchable.`,
      inputSchema: SearchFlightsSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (params: SearchFlightsInput) => {
      try {
        // Validate airport codes against known set
        if (!AIRPORT_CODES.has(params.depAirportCd)) {
          return {
            content: [
              {
                type: "text" as const,
                text: `Error: Unknown departure airport '${params.depAirportCd}'. Use atrs_list_airports to see valid codes.`,
              },
            ],
          };
        }
        if (!AIRPORT_CODES.has(params.arrAirportCd)) {
          return {
            content: [
              {
                type: "text" as const,
                text: `Error: Unknown arrival airport '${params.arrAirportCd}'. Use atrs_list_airports to see valid codes.`,
              },
            ],
          };
        }

        const flights = await makeApiRequest<FlightResource[]>("flight", "GET", undefined, {
          flightType: params.flightType,
          depAirportCd: params.depAirportCd,
          arrAirportCd: params.arrAirportCd,
          depDate: params.depDate,
          boardingClassCd: params.boardingClassCd,
        });

        if (!flights || flights.length === 0) {
          return {
            content: [
              {
                type: "text" as const,
                text: `No flights found from ${params.depAirportCd} to ${params.arrAirportCd} on ${params.depDate} (class: ${params.boardingClassCd}).`,
              },
            ],
          };
        }

        // Build markdown table
        const lines: string[] = [
          `# Flight Search Results`,
          `**${params.depAirportCd} -> ${params.arrAirportCd}** | ${params.depDate} | Class: ${params.boardingClassCd === "N" ? "Normal" : "Special"}`,
          "",
        ];

        for (const f of flights) {
          lines.push(`## ${f.flightName}  (${f.depTime} - ${f.arrTime})`);
          lines.push("");
          lines.push("| Fare Type | Price (JPY) | Seats Available |");
          lines.push("|-----------|------------|-----------------|");
          for (const [code, ft] of Object.entries(f.fareTypes)) {
            lines.push(
              `| ${ft.fareTypeName} (${code}) | ${ft.fare.toLocaleString()} | ${ft.vacantNum} |`
            );
          }
          lines.push("");
        }

        let text = lines.join("\n");
        if (text.length > CHARACTER_LIMIT) {
          text =
            text.slice(0, CHARACTER_LIMIT) +
            "\n\n... (truncated — narrow search to see all results)";
        }

        return { content: [{ type: "text" as const, text }] };
      } catch (error) {
        return {
          content: [{ type: "text" as const, text: handleApiError(error) }],
        };
      }
    }
  );
}
