/**
 * Tests for tools/reference.ts — list airports & fare types.
 *
 * These tools are pure (no API calls), so no mocking needed.
 */

import { describe, it, expect, beforeAll } from "vitest";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { registerReferenceTools } from "../tools/reference.js";

let client: Client;

beforeAll(async () => {
  const server = new McpServer({ name: "test", version: "0.0.1" });
  registerReferenceTools(server);

  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();

  const c = new Client({ name: "test-client", version: "0.0.1" });
  await Promise.all([c.connect(clientTransport), server.connect(serverTransport)]);
  client = c;
});

// ── atrs_list_airports ───────────────────────────────────────────────────

describe("atrs_list_airports", () => {
  it("should list all 50 airports when no filter", async () => {
    const result = await client.callTool({
      name: "atrs_list_airports",
      arguments: {},
    });

    const text = (result.content as Array<{ type: string; text: string }>)[0].text;
    expect(text).toContain("ATRS Airports (50)");
    expect(text).toContain("HND");
    expect(text).toContain("Haneda");
  });

  it("should filter by airport code (case-insensitive)", async () => {
    const result = await client.callTool({
      name: "atrs_list_airports",
      arguments: { search: "hnd" },
    });

    const text = (result.content as Array<{ type: string; text: string }>)[0].text;
    expect(text).toContain("ATRS Airports (1)");
    expect(text).toContain("HND");
    expect(text).toContain("Haneda");
  });

  it("should filter by name substring", async () => {
    const result = await client.callTool({
      name: "atrs_list_airports",
      arguments: { search: "sapporo" },
    });

    const text = (result.content as Array<{ type: string; text: string }>)[0].text;
    expect(text).toContain("ATRS Airports (1)");
    expect(text).toContain("SPK");
  });

  it("should return multiple matches", async () => {
    const result = await client.callTool({
      name: "atrs_list_airports",
      arguments: { search: "oka" },
    });

    const text = (result.content as Array<{ type: string; text: string }>)[0].text;
    // Should match OKA (Naha/Okinawa) and OKJ (Okayama) and OKE (Okinoerabu)
    expect(text).toContain("OKA");
    expect(text).toContain("OKJ");
  });

  it("should return 'no match' message for unknown filter", async () => {
    const result = await client.callTool({
      name: "atrs_list_airports",
      arguments: { search: "zzzzz" },
    });

    const text = (result.content as Array<{ type: string; text: string }>)[0].text;
    expect(text).toContain("No airports match");
  });
});

// ── atrs_list_fare_types ─────────────────────────────────────────────────

describe("atrs_list_fare_types", () => {
  it("should list all 10 fare types", async () => {
    const result = await client.callTool({
      name: "atrs_list_fare_types",
      arguments: {},
    });

    const text = (result.content as Array<{ type: string; text: string }>)[0].text;
    expect(text).toContain("ATRS Fare Types");
    // Spot-check some fare types
    expect(text).toContain("OW");
    expect(text).toContain("One-way");
    expect(text).toContain("RT");
    expect(text).toContain("Round-trip");
    expect(text).toContain("GD");
    expect(text).toContain("Group discount");
    expect(text).toContain("LD");
    expect(text).toContain("Ladies discount");
  });

  it("should include boarding classes section", async () => {
    const result = await client.callTool({
      name: "atrs_list_fare_types",
      arguments: {},
    });

    const text = (result.content as Array<{ type: string; text: string }>)[0].text;
    expect(text).toContain("Boarding Classes");
    expect(text).toContain("Normal");
    expect(text).toContain("Special");
    expect(text).toContain("5,000");
  });
});
