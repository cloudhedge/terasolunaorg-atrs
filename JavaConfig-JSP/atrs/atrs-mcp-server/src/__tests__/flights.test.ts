/**
 * Tests for tools/flights.ts — flight search with API mocking.
 */

import { describe, it, expect, beforeAll, vi, beforeEach } from "vitest";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { registerFlightTools } from "../tools/flights.js";

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
  registerFlightTools(server);

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

describe("atrs_search_flights", () => {
  // ── Validation ─────────────────────────────────────────────────────────

  it("should reject unknown departure airport code", async () => {
    const result = await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "XXX",
        arrAirportCd: "SPK",
        depDate: "2026/03/15",
        boardingClassCd: "N",
      },
    });

    expect(getText(result)).toContain("Unknown departure airport 'XXX'");
    expect(getText(result)).toContain("atrs_list_airports");
    expect(mockMakeApiRequest).not.toHaveBeenCalled();
  });

  it("should reject unknown arrival airport code", async () => {
    const result = await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "HND",
        arrAirportCd: "ZZZ",
        depDate: "2026/03/15",
        boardingClassCd: "N",
      },
    });

    expect(getText(result)).toContain("Unknown arrival airport 'ZZZ'");
    expect(mockMakeApiRequest).not.toHaveBeenCalled();
  });

  // ── Empty results ──────────────────────────────────────────────────────

  it("should handle empty flight results", async () => {
    mockMakeApiRequest.mockResolvedValueOnce([]);

    const result = await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "HND",
        arrAirportCd: "SPK",
        depDate: "2026/03/15",
        boardingClassCd: "N",
      },
    });

    expect(getText(result)).toContain("No flights found");
    expect(getText(result)).toContain("HND");
    expect(getText(result)).toContain("SPK");
  });

  // ── Successful search ──────────────────────────────────────────────────

  it("should format flight results as markdown table", async () => {
    mockMakeApiRequest.mockResolvedValueOnce([
      {
        flightName: "ANA001",
        depAirportName: "Haneda",
        arrAirportName: "New Chitose",
        depTime: "08:00",
        arrTime: "09:30",
        depDate: "2026/03/15",
        boardingClassCd: "N",
        fareTypes: {
          OW: { fareTypeName: "One-way", fare: 25000, vacantNum: 120 },
          RT: { fareTypeName: "Round-trip", fare: 23750, vacantNum: 120 },
        },
      },
    ]);

    const result = await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "HND",
        arrAirportCd: "SPK",
        depDate: "2026/03/15",
        boardingClassCd: "N",
      },
    });

    const text = getText(result);
    expect(text).toContain("Flight Search Results");
    expect(text).toContain("HND -> SPK");
    expect(text).toContain("ANA001");
    expect(text).toContain("08:00 - 09:30");
    expect(text).toContain("One-way (OW)");
    expect(text).toContain("25,000");
    expect(text).toContain("120");
    expect(text).toContain("Normal");
  });

  it("should show Special class label", async () => {
    mockMakeApiRequest.mockResolvedValueOnce([
      {
        flightName: "JAL101",
        depAirportName: "Haneda",
        arrAirportName: "Itami",
        depTime: "10:00",
        arrTime: "11:15",
        depDate: "2026/03/15",
        boardingClassCd: "S",
        fareTypes: {
          SOW: { fareTypeName: "Special one-way", fare: 30000, vacantNum: 10 },
        },
      },
    ]);

    const result = await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "HND",
        arrAirportCd: "ITM",
        depDate: "2026/03/15",
        boardingClassCd: "S",
      },
    });

    expect(getText(result)).toContain("Special");
  });

  it("should display multiple flights", async () => {
    mockMakeApiRequest.mockResolvedValueOnce([
      {
        flightName: "ANA001",
        depAirportName: "Haneda",
        arrAirportName: "New Chitose",
        depTime: "08:00",
        arrTime: "09:30",
        depDate: "2026/03/15",
        boardingClassCd: "N",
        fareTypes: {
          OW: { fareTypeName: "One-way", fare: 25000, vacantNum: 50 },
        },
      },
      {
        flightName: "ANA003",
        depAirportName: "Haneda",
        arrAirportName: "New Chitose",
        depTime: "12:00",
        arrTime: "13:30",
        depDate: "2026/03/15",
        boardingClassCd: "N",
        fareTypes: {
          OW: { fareTypeName: "One-way", fare: 25000, vacantNum: 80 },
        },
      },
    ]);

    const result = await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "HND",
        arrAirportCd: "SPK",
        depDate: "2026/03/15",
        boardingClassCd: "N",
      },
    });

    const text = getText(result);
    expect(text).toContain("ANA001");
    expect(text).toContain("ANA003");
  });

  // ── API error handling ─────────────────────────────────────────────────

  it("should handle API errors gracefully", async () => {
    mockMakeApiRequest.mockRejectedValueOnce(new Error("Connection refused"));

    const result = await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "HND",
        arrAirportCd: "SPK",
        depDate: "2026/03/15",
        boardingClassCd: "N",
      },
    });

    expect(getText(result)).toContain("Error");
    expect(getText(result)).toContain("Connection refused");
  });

  // ── Default boarding class ─────────────────────────────────────────────

  it("should default to Normal boarding class", async () => {
    mockMakeApiRequest.mockResolvedValueOnce([]);

    await client.callTool({
      name: "atrs_search_flights",
      arguments: {
        flightType: "OW",
        depAirportCd: "HND",
        arrAirportCd: "SPK",
        depDate: "2026/03/15",
        // no boardingClassCd -> defaults to N
      },
    });

    expect(mockMakeApiRequest).toHaveBeenCalledWith(
      "flight",
      "GET",
      undefined,
      expect.objectContaining({ boardingClassCd: "N" })
    );
  });
});
