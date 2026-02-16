/**
 * Ticket reservation and check tools for ATRS MCP server.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { makeApiRequest, handleApiError } from "../api-client.js";

// ── Schemas ──────────────────────────────────────────────────────────────

const SelectFlightSchema = z.object({
  depDate: z
    .string()
    .regex(/^\d{4}\/\d{2}\/\d{2}$/, "Date must be yyyy/MM/dd")
    .describe("Departure date yyyy/MM/dd"),
  flightName: z.string().describe("Flight name (e.g. ANA001)"),
  boardingClassCd: z.enum(["N", "S"]).describe("N = Normal, S = Special"),
  fareTypeCd: z
    .enum(["OW", "RT", "RD1", "RD7", "ED", "LD", "GD", "SOW", "SRT", "SRD"])
    .describe("Fare type code"),
});

const PassengerSchema = z.object({
  familyName: z
    .string()
    .max(10)
    .describe("Passenger family name (Katakana)"),
  givenName: z
    .string()
    .max(10)
    .describe("Passenger given name (Katakana)"),
  age: z.number().int().min(0).describe("Passenger age"),
  gender: z.enum(["M", "F"]).describe("M = Male, F = Female"),
  membershipNumber: z
    .string()
    .length(10)
    .optional()
    .describe("10-digit ATRS membership number (optional)"),
});

const ReserveTicketSchema = z
  .object({
    repFamilyName: z
      .string()
      .max(10)
      .describe("Representative family name (Katakana)"),
    repGivenName: z
      .string()
      .max(10)
      .describe("Representative given name (Katakana)"),
    repAge: z
      .number()
      .int()
      .min(18)
      .describe("Representative age (must be 18+)"),
    repGender: z.enum(["M", "F"]).describe("Representative gender"),
    repMembershipNumber: z
      .string()
      .length(10)
      .optional()
      .describe("Representative membership number (optional)"),
    repTel1: z.string().min(2).max(5).describe("Phone area code (2-5 digits)"),
    repTel2: z
      .string()
      .min(1)
      .max(4)
      .describe("Phone middle digits (1-4 digits)"),
    repTel3: z.string().length(4).describe("Phone last 4 digits"),
    repMail: z.string().email().max(256).describe("Representative email"),
    flightType: z
      .enum(["OW", "RT"])
      .describe("OW (one-way) or RT (round-trip)"),
    selectFlightResourceList: z
      .array(SelectFlightSchema)
      .min(1)
      .max(2)
      .describe("Selected flight(s). 1 for one-way, 2 for round-trip."),
    passengerResourceList: z
      .array(PassengerSchema)
      .min(1)
      .describe("List of passengers"),
  })
  .strict();

type ReserveTicketInput = z.infer<typeof ReserveTicketSchema>;

const CheckReservationSchema = z
  .object({
    reserveNo: z
      .string()
      .describe("Reservation number to verify"),
  })
  .strict();

type CheckReservationInput = z.infer<typeof CheckReservationSchema>;

// ── Response types ───────────────────────────────────────────────────────

interface ReservationResponse {
  reserveNo: string;
  paymentDate: string;
  totalFare: number;
  repFamilyName: string;
  repGivenName: string;
  [key: string]: unknown;
}

// ── Registration ─────────────────────────────────────────────────────────

export function registerTicketTools(server: McpServer): void {
  // ── Reserve Ticket ─────────────────────────────────────────────────────

  server.registerTool(
    "atrs_reserve_ticket",
    {
      title: "Reserve ATRS Ticket",
      description: `Reserve airline tickets in the ATRS system.

Creates a reservation with representative info, flight selection, and passenger list.

Args:
  - repFamilyName/repGivenName: Rep name in Katakana (max 10 chars each)
  - repAge: Must be 18+
  - repGender: M or F
  - repTel1/repTel2/repTel3: Phone number parts
  - repMail: Email address
  - flightType: OW (one-way) or RT (round-trip)
  - selectFlightResourceList: 1 flight for OW, 2 for RT. Each needs depDate, flightName, boardingClassCd, fareTypeCd
  - passengerResourceList: Passenger details (familyName, givenName, age, gender)

Returns:
  Reservation confirmation with reserveNo, totalFare, paymentDate.

Business rules:
  - Ladies discount (LD): women passengers only
  - Group discount (GD): minimum 3 passengers
  - Children (<12): 60% of adult fare
  - Round-trip: min 120 min between outward arrival and return departure

Use atrs_search_flights first to find available flights.`,
      inputSchema: ReserveTicketSchema,
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        idempotentHint: false,
        openWorldHint: false,
      },
    },
    async (params: ReserveTicketInput) => {
      try {
        const result = await makeApiRequest<ReservationResponse>(
          "ticket",
          "POST",
          params
        );

        const lines = [
          "# Reservation Confirmed",
          "",
          `| Field | Value |`,
          `|-------|-------|`,
          `| Reservation No | **${result.reserveNo}** |`,
          `| Total Fare | ${result.totalFare.toLocaleString()} JPY |`,
          `| Payment Date | ${result.paymentDate} |`,
          `| Representative | ${result.repFamilyName} ${result.repGivenName} |`,
        ];

        return {
          content: [{ type: "text" as const, text: lines.join("\n") }],
        };
      } catch (error) {
        return {
          content: [{ type: "text" as const, text: handleApiError(error) }],
        };
      }
    }
  );

  // ── Check Reservation ──────────────────────────────────────────────────

  server.registerTool(
    "atrs_check_reservation",
    {
      title: "Check ATRS Reservation",
      description: `Verify whether a reservation exists in the ATRS system.

Args:
  - reserveNo (string): The reservation number to check

Returns:
  Confirmation of whether the reservation exists.`,
      inputSchema: CheckReservationSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (params: CheckReservationInput) => {
      try {
        const exists = await makeApiRequest<boolean>(
          "ticket/check",
          "GET",
          undefined,
          { reserveNo: params.reserveNo }
        );

        const text = exists
          ? `Reservation **${params.reserveNo}** exists and is valid.`
          : `Reservation **${params.reserveNo}** was not found.`;

        return { content: [{ type: "text" as const, text }] };
      } catch (error) {
        return {
          content: [{ type: "text" as const, text: handleApiError(error) }],
        };
      }
    }
  );
}
