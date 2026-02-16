#!/usr/bin/env node
/**
 * ATRS MCP Server
 *
 * MCP server for the Airline Ticket Reservation System (ATRS).
 * Provides tools to search flights, reserve tickets, check reservations,
 * and browse reference data (airports, fare types).
 *
 * Transport: stdio (default) or streamable HTTP (set TRANSPORT=http).
 * API base: ATRS_API_URL env var (default http://localhost:8080/atrs/api/v1).
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerFlightTools } from "./tools/flights.js";
import { registerTicketTools } from "./tools/tickets.js";
import { registerReferenceTools } from "./tools/reference.js";
import { API_BASE_URL } from "./constants.js";

// ── Server instance ──────────────────────────────────────────────────────

const server = new McpServer({
  name: "atrs-mcp-server",
  version: "1.0.0",
});

// ── Register all tool groups ─────────────────────────────────────────────

registerFlightTools(server);
registerTicketTools(server);
registerReferenceTools(server);

// ── Transport ────────────────────────────────────────────────────────────

async function runStdio(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`ATRS MCP server running via stdio (API: ${API_BASE_URL})`);
}

runStdio().catch((error) => {
  console.error("Fatal error starting ATRS MCP server:", error);
  process.exit(1);
});
