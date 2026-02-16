/**
 * Reference data tools: airports and fare types.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { AIRPORTS, FARE_TYPES, BOARDING_CLASSES } from "../constants.js";

const ListAirportsSchema = z
  .object({
    search: z
      .string()
      .optional()
      .describe(
        "Optional filter — matches against airport code or name (case-insensitive)"
      ),
  })
  .strict();

type ListAirportsInput = z.infer<typeof ListAirportsSchema>;

const ListFareTypesSchema = z.object({}).strict();

export function registerReferenceTools(server: McpServer): void {
  // ── List Airports ──────────────────────────────────────────────────────

  server.registerTool(
    "atrs_list_airports",
    {
      title: "List ATRS Airports",
      description: `List all 50 Japanese airports available in the ATRS system.

Args:
  - search (string, optional): Filter by code or name substring

Returns:
  Table of airport codes and names.

Use these codes for atrs_search_flights depAirportCd / arrAirportCd parameters.`,
      inputSchema: ListAirportsSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (params: ListAirportsInput) => {
      let filtered = [...AIRPORTS];

      if (params.search) {
        const q = params.search.toLowerCase();
        filtered = filtered.filter(
          (a) =>
            a.code.toLowerCase().includes(q) ||
            a.name.toLowerCase().includes(q)
        );
      }

      if (filtered.length === 0) {
        return {
          content: [
            {
              type: "text" as const,
              text: `No airports match '${params.search}'.`,
            },
          ],
        };
      }

      const lines = [
        `# ATRS Airports (${filtered.length})`,
        "",
        "| Code | Name |",
        "|------|------|",
        ...filtered.map((a) => `| ${a.code} | ${a.name} |`),
      ];

      return { content: [{ type: "text" as const, text: lines.join("\n") }] };
    }
  );

  // ── List Fare Types ────────────────────────────────────────────────────

  server.registerTool(
    "atrs_list_fare_types",
    {
      title: "List ATRS Fare Types",
      description: `List all fare types and boarding classes available in the ATRS system.

Returns:
  Table of fare type codes, names, discount rates, booking windows, minimum passengers, and notes.
  Also includes boarding class details (Normal and Special).

Use these codes for the fareTypeCd and boardingClassCd parameters when reserving tickets.`,
      inputSchema: ListFareTypesSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async () => {
      const lines = [
        "# ATRS Fare Types",
        "",
        "| Code | Name | Discount | Booking Window | Min Pax | Notes |",
        "|------|------|----------|---------------|---------|-------|",
        ...FARE_TYPES.map(
          (f) =>
            `| ${f.code} | ${f.name} | ${f.discountRate}% | ${f.bookingWindowDays} days | ${f.minPassengers} | ${f.notes} |`
        ),
        "",
        "## Boarding Classes",
        "",
        "| Code | Name | Extra Charge (JPY) |",
        "|------|------|--------------------|",
        ...BOARDING_CLASSES.map(
          (b) => `| ${b.code} | ${b.name} | ${b.extraCharge.toLocaleString()} |`
        ),
      ];

      return { content: [{ type: "text" as const, text: lines.join("\n") }] };
    }
  );
}
