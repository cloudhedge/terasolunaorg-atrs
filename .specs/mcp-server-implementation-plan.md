# MCP Server for ATRS APIs - Implementation Plan

> **Status:** Ready for implementation
> **Approach:** Custom MCP Server (Direct Build)
> **Last Updated:** 2025-12-23

## Context Files (Read First)

```

Priority 2 - API Controllers:
├── atrs-web/.../api/flight/FlightRestController.java    # GET /flight
├── atrs-web/.../api/ticket/TicketRestController.java    # POST /ticket, GET /ticket/check
├── atrs-web/.../app/a0/AuthApiController.java           # GET /api/auth/status
├── atrs-web/.../app/a0/MemberApiController.java         # GET /api/member/available
└── atrs-web/.../app/b1/FlightsApiController.java        # GET /api/flights

Priority 3 - Domain Models:
├── atrs-domain/.../model/Reservation.java
├── atrs-domain/.../model/Flight.java
├── atrs-domain/.../model/Passenger.java
└── atrs-domain/.../model/Member.java

Priority 4 - Request/Response Types:
├── atrs-web/.../api/flight/FlightSearchQuery.java
├── atrs-web/.../api/flight/FlightResource.java
├── atrs-web/.../api/ticket/TicketReserveResource.java
└── atrs-web/.../api/ticket/PassengerResource.java
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/flight` | GET | Search available flights |
| `/ticket` | POST | Create reservation |
| `/ticket/check` | GET | Verify reservation exists |
| `/api/auth/status` | GET | Check login status |
| `/api/member/available` | GET | Check member exists |

---

## Approach Decision

**Selected: Custom MCP Server (Direct Build)**

Build MCP server directly from API inspection

Benefits:
- User-friendly parameter names ("Tokyo" → "HND")
- Simplified responses
- Better error handling
- Full control over tool schemas

---

## Phase 1: MCP Server Project Setup

**Goal:** Create Node.js project with MCP SDK

**Tasks:**
1. Create project structure:
   ```
   atrs-mcp-server/
   ├── src/
   │   ├── index.ts
   │   ├── server.ts
   │   ├── config.ts
   │   ├── tools/
   │   ├── api/
   │   ├── mappers/
   │   └── data/
   ├── package.json
   ├── tsconfig.json
   └── README.md
   ```

2. Initialize npm project with dependencies:
   ```json
   {
     "dependencies": {
       "@modelcontextprotocol/sdk": "^1.0.0",
       "zod": "^3.22.0"
     },
     "devDependencies": {
       "typescript": "^5.0.0",
       "@types/node": "^20.0.0"
     }
   }
   ```

3. Create TypeScript config for ESM output

4. Create basic server skeleton with stdio transport

**Checkpoint 1:**
```
Verify:
[ ] Project compiles with `npm run build`
[ ] Empty MCP server starts without errors
[ ] MCP Inspector connects successfully

Human approval required before Phase 2
```

---

## Phase 2: API Client & Type Definitions

**Goal:** Create typed HTTP client for ATRS APIs

**Tasks:**
1. Define TypeScript types matching API contracts:
   - `FlightSearchQuery` (input)
   - `FlightResource` (output)
   - `TicketReserveRequest/Response`

2. Create HTTP client with:
   - Base URL configuration
   - Error handling
   - Timeout support

3. Implement endpoint functions:
   - `searchFlights(query)`
   - `reserveTicket(data)`
   - `checkReservation(reserveNo)`
   - `checkAuthStatus()`
   - `checkMemberAvailable(membershipNumber)`

**Checkpoint 2:**
```
Verify:
[ ] Types match API contracts
[ ] API client compiles
[ ] Manual test: searchFlights returns data
[ ] Manual test: checkReservation returns boolean

Human approval required before Phase 3
```

---

## Phase 3: Data Mappers & Reference Data

**Goal:** Transform between user-friendly and API formats

**Tasks:**
1. Create airport code mappings:
   ```typescript
   // "Tokyo" → "HND", "Osaka" → "KIX"
   const cityToAirport: Record<string, string>
   const airportToCity: Record<string, string>
   ```

2. Create date format converter:
   ```typescript
   // "2025-01-15" ↔ "2025/01/15"
   toApiDate(iso: string): string
   fromApiDate(api: string): string
   ```

3. Create fare type mappings:
   ```typescript
   // "one-way" → "OW", "round-trip" → "RT"
   ```

4. Create phone number parser:
   ```typescript
   // "090-1234-5678" → { tel1, tel2, tel3 }
   ```

5. Create response simplifiers for cleaner MCP output

**Checkpoint 3:**
```
Verify:
[ ] All 50+ airports mapped
[ ] Date conversion round-trips correctly
[ ] Fare types cover all codes (OW, RT, ED, LD, GD, PR)
[ ] Phone parser handles various formats

Human approval required before Phase 4
```

---

## Phase 4: MCP Tools Implementation

**Goal:** Implement 5 MCP tools

**Tools to implement:**

### Tool 1: `search_flights`
```typescript
Input: {
  from: string      // City name or airport code
  to: string        // City name or airport code
  date: string      // ISO date
  returnDate?: string
  seatClass?: string
}
Output: Array of flights with fares
```

### Tool 2: `reserve_ticket`
```typescript
Input: {
  flightName: string
  departureDate: string
  fareType: string
  passengers: Array<{name, age, gender}>
  contact: {name, phone, email}
}
Output: { reservationNumber, paymentDeadline, totalFare }
```

### Tool 3: `check_reservation`
```typescript
Input: { reservationNumber: string }
Output: { exists: boolean }
```

### Tool 4: `list_airports`
```typescript
Input: { region?: string }
Output: Array of { code, city, name }
```

### Tool 5: `list_fare_types`
```typescript
Input: {}
Output: Array of { code, name, description }
```

**Checkpoint 4:**
```
Verify:
[ ] All 5 tools registered in MCP server
[ ] MCP Inspector shows tools with schemas
[ ] search_flights returns formatted results
[ ] reserve_ticket creates booking (test environment)
[ ] check_reservation returns boolean
[ ] list_airports returns reference data
[ ] list_fare_types returns reference data

Human approval required before Phase 5
```

---

## Phase 5: Integration Testing

**Goal:** Validate end-to-end with Claude Desktop

**Tasks:**
1. Configure Claude Desktop:
   ```json
   {
     "mcpServers": {
       "atrs": {
         "command": "node",
         "args": ["./atrs-mcp-server/dist/index.js"],
         "env": {
           "ATRS_API_BASE_URL": "http://localhost:8080/atrs"
         }
       }
     }
   }
   ```

2. Test scenarios:
   - "Find flights from Tokyo to Osaka on Jan 15"
   - "Book 2 passengers on NH123"
   - "Check if reservation RES12345 exists"

3. Verify error handling:
   - Invalid airport names
   - Past dates
   - Non-existent reservations

4. Add logging for debugging

**Checkpoint 5 (Final):**
```
Verify:
[ ] Claude Desktop loads MCP server
[ ] Natural language queries work
[ ] Booking flow completes end-to-end
[ ] Errors return helpful messages
[ ] Server handles restarts gracefully

IMPLEMENTATION COMPLETE
```

---

## File Changes Summary

| Phase | Files Modified/Created |
|-------|----------------------|
| 1 | New: `atrs-mcp-server/*` (project skeleton) |
| 2 | New: `src/api/client.ts`, `src/api/types.ts` |
| 3 | New: `src/mappers/*`, `src/data/*` |
| 4 | New: `src/tools/*`, `src/server.ts` |
| 5 | Claude Desktop config, `README.md` |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| ATRS auth required | Test with public endpoints first |
| Japanese characters | Ensure UTF-8 throughout |
| Date/timezone issues | Use explicit timezone handling |
| API changes | Track API contract in types.ts |

---

## Success Criteria

1. MCP server runs standalone via `npm start`
2. All 5 tools accessible from Claude Desktop
3. Flight search returns human-readable results
4. Reservation flow works end-to-end
5. Error messages are actionable

---

## Resume Instructions

To resume implementation:
1. Read this plan and context files
2. Check which phase was last completed
3. Continue from next uncompleted checkpoint
4. Get human approval before proceeding to next phase
