/**
 * Tests for tools/tickets.ts — reserve ticket & check reservation.
 */

import { describe, it, expect, beforeAll, vi, beforeEach } from "vitest";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { registerTicketTools } from "../tools/tickets.js";

// Mock the api-client module
vi.mock("../api-client.js", async (importOriginal) => {
  const original = await importOriginal<typeof import("../api-client.js")>();
  return {
    ...original,
    makeApiRequest: vi.fn(),
  };
});

import { makeApiRequest } from "../api-client.js";
const mockMakeApiRequest = vi.mocked(makeApiRequest);

let client: Client;

beforeAll(async () => {
  const server = new McpServer({ name: "test", version: "0.0.1" });
  registerTicketTools(server);

  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();

  const c = new Client({ name: "test-client", version: "0.0.1" });
  await Promise.all([c.connect(clientTransport), server.connect(serverTransport)]);
  client = c;
});

beforeEach(() => {
  vi.clearAllMocks();
});

/** Helper to extract text content from a tool result. */
function getText(result: Awaited<ReturnType<typeof client.callTool>>): string {
  return (result.content as Array<{ type: string; text: string }>)[0].text;
}

/** Valid reservation input for reuse. */
const VALID_RESERVATION = {
  repFamilyName: "ヤマダ",
  repGivenName: "タロウ",
  repAge: 30,
  repGender: "M" as const,
  repTel1: "03",
  repTel2: "1234",
  repTel3: "5678",
  repMail: "yamada@example.com",
  flightType: "OW" as const,
  selectFlightResourceList: [
    {
      depDate: "2026/03/15",
      flightName: "ANA001",
      boardingClassCd: "N" as const,
      fareTypeCd: "OW" as const,
    },
  ],
  passengerResourceList: [
    {
      familyName: "ヤマダ",
      givenName: "タロウ",
      age: 30,
      gender: "M" as const,
    },
  ],
};

// ── atrs_reserve_ticket ──────────────────────────────────────────────────

describe("atrs_reserve_ticket", () => {
  it("should return reservation confirmation on success", async () => {
    mockMakeApiRequest.mockResolvedValueOnce({
      reserveNo: "R00000001",
      totalFare: 25000,
      paymentDate: "2026/03/15",
      repFamilyName: "ヤマダ",
      repGivenName: "タロウ",
    });

    const result = await client.callTool({
      name: "atrs_reserve_ticket",
      arguments: VALID_RESERVATION,
    });

    const text = getText(result);
    expect(text).toContain("Reservation Confirmed");
    expect(text).toContain("R00000001");
    expect(text).toContain("25,000");
    expect(text).toContain("2026/03/15");
    expect(text).toContain("ヤマダ タロウ");
  });

  it("should send correct payload to API", async () => {
    mockMakeApiRequest.mockResolvedValueOnce({
      reserveNo: "R00000002",
      totalFare: 50000,
      paymentDate: "2026/03/15",
      repFamilyName: "ヤマダ",
      repGivenName: "タロウ",
    });

    await client.callTool({
      name: "atrs_reserve_ticket",
      arguments: VALID_RESERVATION,
    });

    expect(mockMakeApiRequest).toHaveBeenCalledWith(
      "ticket",
      "POST",
      expect.objectContaining({
        repFamilyName: "ヤマダ",
        repGivenName: "タロウ",
        repAge: 30,
        flightType: "OW",
      })
    );
  });

  it("should handle API errors gracefully", async () => {
    mockMakeApiRequest.mockRejectedValueOnce(new Error("No vacancy"));

    const result = await client.callTool({
      name: "atrs_reserve_ticket",
      arguments: VALID_RESERVATION,
    });

    expect(getText(result)).toContain("Error");
    expect(getText(result)).toContain("No vacancy");
  });

  it("should support round-trip with 2 flights", async () => {
    const rtReservation = {
      ...VALID_RESERVATION,
      flightType: "RT" as const,
      selectFlightResourceList: [
        {
          depDate: "2026/03/15",
          flightName: "ANA001",
          boardingClassCd: "N" as const,
          fareTypeCd: "RT" as const,
        },
        {
          depDate: "2026/03/17",
          flightName: "ANA002",
          boardingClassCd: "N" as const,
          fareTypeCd: "RT" as const,
        },
      ],
    };

    mockMakeApiRequest.mockResolvedValueOnce({
      reserveNo: "R00000003",
      totalFare: 47500,
      paymentDate: "2026/03/15",
      repFamilyName: "ヤマダ",
      repGivenName: "タロウ",
    });

    const result = await client.callTool({
      name: "atrs_reserve_ticket",
      arguments: rtReservation,
    });

    const text = getText(result);
    expect(text).toContain("Reservation Confirmed");
    expect(text).toContain("R00000003");
    expect(text).toContain("47,500");
  });

  it("should support multiple passengers", async () => {
    const groupReservation = {
      ...VALID_RESERVATION,
      passengerResourceList: [
        { familyName: "ヤマダ", givenName: "タロウ", age: 30, gender: "M" as const },
        { familyName: "ヤマダ", givenName: "ハナコ", age: 28, gender: "F" as const },
        { familyName: "ヤマダ", givenName: "ケン", age: 5, gender: "M" as const },
      ],
    };

    mockMakeApiRequest.mockResolvedValueOnce({
      reserveNo: "R00000004",
      totalFare: 65000,
      paymentDate: "2026/03/15",
      repFamilyName: "ヤマダ",
      repGivenName: "タロウ",
    });

    const result = await client.callTool({
      name: "atrs_reserve_ticket",
      arguments: groupReservation,
    });

    expect(getText(result)).toContain("65,000");
  });
});

// ── atrs_check_reservation ───────────────────────────────────────────────

describe("atrs_check_reservation", () => {
  it("should confirm existing reservation", async () => {
    mockMakeApiRequest.mockResolvedValueOnce(true);

    const result = await client.callTool({
      name: "atrs_check_reservation",
      arguments: { reserveNo: "R00000001" },
    });

    const text = getText(result);
    expect(text).toContain("R00000001");
    expect(text).toContain("exists and is valid");
  });

  it("should report non-existing reservation", async () => {
    mockMakeApiRequest.mockResolvedValueOnce(false);

    const result = await client.callTool({
      name: "atrs_check_reservation",
      arguments: { reserveNo: "R99999999" },
    });

    const text = getText(result);
    expect(text).toContain("R99999999");
    expect(text).toContain("was not found");
  });

  it("should pass reserveNo as query param", async () => {
    mockMakeApiRequest.mockResolvedValueOnce(true);

    await client.callTool({
      name: "atrs_check_reservation",
      arguments: { reserveNo: "R12345" },
    });

    expect(mockMakeApiRequest).toHaveBeenCalledWith(
      "ticket/check",
      "GET",
      undefined,
      { reserveNo: "R12345" }
    );
  });

  it("should handle API errors gracefully", async () => {
    mockMakeApiRequest.mockRejectedValueOnce(new Error("DB unavailable"));

    const result = await client.callTool({
      name: "atrs_check_reservation",
      arguments: { reserveNo: "R00000001" },
    });

    expect(getText(result)).toContain("Error");
    expect(getText(result)).toContain("DB unavailable");
  });
});
