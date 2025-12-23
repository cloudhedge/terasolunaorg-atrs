# Custom MCP Server Plan for ATRS

## Overview

Build a custom MCP server that provides an AI-friendly interface to the ATRS (Airline Ticket Reservation System) REST API.

```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────┐
│  AI Agent   │────▶│  Custom MCP Server  │────▶│  ATRS REST  │
│  (Claude,   │     │  - Friendly params  │     │  API        │
│   Gemini)   │     │  - City → Airport   │     │  /flight    │
│             │◀────│  - Response cleanup │◀────│  /ticket    │
└─────────────┘     └─────────────────────┘     └─────────────┘
```

---

## Goals

| Goal | Description |
|------|-------------|
| **AI-Friendly Interface** | Natural language params (city names, ISO dates) |
| **Data Translation** | City → Airport code mapping |
| **Response Simplification** | Clean, English responses for AI |
| **Workflow Tools** | Composite operations (search + book) |
| **Reference Data** | Built-in airport/fare type lookups |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Runtime | Node.js 20+ |
| Language | TypeScript |
| MCP SDK | `@modelcontextprotocol/sdk` |
| HTTP Client | `fetch` (native) |
| Transport | stdio (Claude Desktop compatible) |

---

## Project Structure

```
atrs-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts              # Entry point
│   ├── server.ts             # MCP server setup
│   ├── config.ts             # Configuration
│   ├── tools/
│   │   ├── index.ts          # Tool registry
│   │   ├── searchFlights.ts  # Flight search tool
│   │   ├── reserveTicket.ts  # Reservation tool
│   │   ├── checkReservation.ts
│   │   ├── listAirports.ts   # Reference data
│   │   └── listFareTypes.ts
│   ├── api/
│   │   ├── client.ts         # ATRS API client
│   │   ├── types.ts          # API request/response types
│   │   └── endpoints.ts      # API endpoint definitions
│   ├── mappers/
│   │   ├── airportMapper.ts  # City ↔ Airport code
│   │   ├── dateMapper.ts     # ISO ↔ API date format
│   │   └── responseMapper.ts # API → AI-friendly response
│   └── data/
│       ├── airports.ts       # Airport reference data
│       └── fareTypes.ts      # Fare type reference data
└── README.md
```

---

## MCP Tools Design

### Tool 1: `search_flights`

**Purpose:** Search for available flights with natural language input

| Aspect | Value |
|--------|-------|
| Name | `search_flights` |
| Description | Search for available flights between two cities |

**Input Schema:**
```typescript
{
  from: string,        // "Tokyo", "Osaka", "Sapporo" or airport code "HND"
  to: string,          // Destination city or airport code
  date: string,        // ISO format "2025-01-15"
  returnDate?: string, // For round-trip (ISO format)
  seatClass?: "economy" | "special"  // Default: economy
}
```

**Output:**
```typescript
{
  flights: [
    {
      flightNumber: "NTT001",
      departure: { city: "Tokyo", airport: "HND", time: "08:00" },
      arrival: { city: "Osaka", airport: "KIX", time: "09:15" },
      date: "2025-01-15",
      seatClass: "economy",
      fares: [
        { type: "One-way", price: 20600, seatsLeft: 10 },
        { type: "Round-trip", price: 19600, seatsLeft: 10 },
        { type: "Early Bird", price: 15000, seatsLeft: 5 }
      ]
    }
  ],
  searchCriteria: { from, to, date, returnDate, seatClass }
}
```

**Transformation:**
```
Input:  from="Tokyo", date="2025-01-15"
   ↓
API:    depAirportCd="HND", depDate="2025/01/15", flightType="OW"
   ↓
Output: Simplified English response
```

---

### Tool 2: `reserve_ticket`

**Purpose:** Book a flight reservation

| Aspect | Value |
|--------|-------|
| Name | `reserve_ticket` |
| Description | Reserve tickets for selected flights |

**Input Schema:**
```typescript
{
  flights: [
    {
      flightNumber: string,  // "NTT001"
      date: string,          // "2025-01-15"
      fareType: string       // "one-way", "round-trip", "early-bird"
    }
  ],
  passengers: [
    {
      firstName: string,     // Katakana or Romaji
      lastName: string,
      age: number,
      gender: "male" | "female",
      membershipNumber?: string
    }
  ],
  contact: {
    firstName: string,
    lastName: string,
    age: number,
    gender: "male" | "female",
    phone: string,           // "090-1234-5678" or "09012345678"
    email: string,
    membershipNumber?: string
  }
}
```

**Output:**
```typescript
{
  reservationNumber: "ABC123",
  paymentDeadline: "2025-01-20",
  totalFare: 41200,
  flights: [...],
  passengers: [...],
  contact: {...}
}
```

**Transformations:**
- Phone: "090-1234-5678" → repTel1="090", repTel2="1234", repTel3="5678"
- Names: Romaji → Katakana (if needed, or validate Katakana input)
- fareType: "early-bird" → FareTypeCd.ED
- gender: "male" → Gender.M

---

### Tool 3: `check_reservation`

**Purpose:** Check if a reservation exists

| Aspect | Value |
|--------|-------|
| Name | `check_reservation` |
| Description | Verify if a reservation number is valid |

**Input Schema:**
```typescript
{
  reservationNumber: string  // "ABC123"
}
```

**Output:**
```typescript
{
  exists: boolean,
  reservationNumber: string
}
```

---

### Tool 4: `list_airports`

**Purpose:** Get available airports for flight search

| Aspect | Value |
|--------|-------|
| Name | `list_airports` |
| Description | List all available airports with city names |

**Input Schema:**
```typescript
{
  region?: string  // "tokyo", "osaka", "hokkaido" (optional filter)
}
```

**Output:**
```typescript
{
  airports: [
    { code: "HND", name: "Tokyo Haneda", city: "Tokyo", region: "Kanto" },
    { code: "NRT", name: "Tokyo Narita", city: "Tokyo", region: "Kanto" },
    { code: "KIX", name: "Kansai International", city: "Osaka", region: "Kansai" },
    { code: "ITM", name: "Osaka Itami", city: "Osaka", region: "Kansai" },
    ...
  ]
}
```

---

### Tool 5: `list_fare_types`

**Purpose:** Get available fare types and their descriptions

| Aspect | Value |
|--------|-------|
| Name | `list_fare_types` |
| Description | List all fare types with descriptions and restrictions |

**Input Schema:**
```typescript
{}  // No input required
```

**Output:**
```typescript
{
  fareTypes: [
    { code: "OW", name: "One-way", description: "Standard one-way fare" },
    { code: "RT", name: "Round-trip", description: "Discounted round-trip fare" },
    { code: "ED", name: "Early Bird", description: "Book 28+ days ahead for discount" },
    { code: "LD", name: "Ladies Discount", description: "Special fare for female passengers" },
    ...
  ]
}
```

---

## Data Mappings

### Airport Code Mapping

```typescript
const CITY_TO_AIRPORT: Record<string, string> = {
  // Major cities → Primary airport
  "tokyo": "HND",
  "osaka": "KIX", 
  "sapporo": "CTS",
  "fukuoka": "FUK",
  "nagoya": "NGO",
  "okinawa": "OKA",
  "naha": "OKA",
  
  // Aliases
  "haneda": "HND",
  "narita": "NRT",
  "kansai": "KIX",
  "itami": "ITM",
  ...
};
```

### Fare Type Mapping

```typescript
const FARE_TYPE_MAP: Record<string, string> = {
  "one-way": "OW",
  "round-trip": "RT",
  "early-bird": "ED",
  "early-discount": "ED",
  "ladies": "LD",
  "ladies-discount": "LD",
  "group": "GD",
  "group-discount": "GD",
  "reserve-1": "RD1",
  "reserve-7": "RD7",
  ...
};
```

### Date Format Mapping

```typescript
// ISO → API
"2025-01-15" → "2025/01/15"

// API → ISO  
"2025/01/15" → "2025-01-15"
```

---

## Implementation Phases

### Phase 1: Project Setup (30 min)

- [ ] Initialize Node.js project
- [ ] Install dependencies (@modelcontextprotocol/sdk, typescript)
- [ ] Setup TypeScript configuration
- [ ] Create project structure

### Phase 2: API Client (1 hour)

- [ ] Create ATRS API client
- [ ] Define API types (request/response)
- [ ] Implement GET /flight endpoint
- [ ] Implement POST /ticket endpoint
- [ ] Implement GET /ticket/check endpoint
- [ ] Add error handling

### Phase 3: Data Mappers (1 hour)

- [ ] Create airport reference data (50+ airports)
- [ ] Implement city → airport code mapper
- [ ] Implement date format mapper
- [ ] Implement fare type mapper
- [ ] Implement response simplifier

### Phase 4: MCP Tools (2 hours)

- [ ] Setup MCP server with SDK
- [ ] Implement `search_flights` tool
- [ ] Implement `reserve_ticket` tool
- [ ] Implement `check_reservation` tool
- [ ] Implement `list_airports` tool
- [ ] Implement `list_fare_types` tool

### Phase 5: Testing & Integration (1 hour)

- [ ] Test with MCP Inspector
- [ ] Test with Claude Desktop
- [ ] Document usage instructions
- [ ] Create example conversations

---

## Configuration

### Environment Variables

```bash
# Required
ATRS_API_BASE_URL=http://localhost:8080/atrs

# Optional
ATRS_API_TIMEOUT=30000
LOG_LEVEL=info
```

### Claude Desktop Config

```json
{
  "mcpServers": {
    "atrs": {
      "command": "node",
      "args": ["/path/to/atrs-mcp-server/dist/index.js"],
      "env": {
        "ATRS_API_BASE_URL": "http://localhost:8080/atrs"
      }
    }
  }
}
```

---

## Example AI Conversations

### Flight Search

```
User: Find flights from Tokyo to Osaka on January 15th

AI: I'll search for flights from Tokyo to Osaka.

[Calls search_flights(from="Tokyo", to="Osaka", date="2025-01-15")]

Found 5 flights from Tokyo (HND) to Osaka (KIX) on January 15th:

1. NTT001 - Departs 08:00, Arrives 09:15
   - One-way: ¥20,600 (10 seats)
   - Round-trip: ¥19,600 (10 seats)
   - Early Bird: ¥15,000 (5 seats)

2. NTT003 - Departs 10:00, Arrives 11:15
   ...
```

### Booking

```
User: Book the 8am flight for me. I'm Tanaka Taro, male, 35 years old.
      My phone is 090-1234-5678 and email is tanaka@example.com

AI: I'll book the NTT001 flight for you.

[Calls reserve_ticket(...)]

Reservation confirmed!
- Reservation Number: ABC12345
- Flight: NTT001 Tokyo → Osaka, Jan 15th 08:00
- Passenger: Tanaka Taro
- Total: ¥20,600
- Payment Deadline: January 20th, 2025
```

---

## Error Handling

| Error | AI Response |
|-------|-------------|
| Invalid city name | "I couldn't find an airport for '{city}'. Try using an airport code like HND or KIX, or call list_airports to see available options." |
| No flights found | "No flights available for this route/date. Try a different date or route." |
| Sold out | "This flight is sold out. Here are alternative options..." |
| Invalid reservation | "Reservation {number} not found. Please check the number." |
| API unavailable | "The booking system is currently unavailable. Please try again later." |

---

## Dependencies

```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0"
  }
}
```

---

## Timeline Estimate

| Phase | Duration |
|-------|----------|
| Phase 1: Project Setup | 30 min |
| Phase 2: API Client | 1 hour |
| Phase 3: Data Mappers | 1 hour |
| Phase 4: MCP Tools | 2 hours |
| Phase 5: Testing | 1 hour |
| **Total** | **~5.5 hours** |

---

## Next Steps

1. Create the project folder structure
2. Initialize npm project and install dependencies
3. Start implementing from Phase 1

---

## References

- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Specification](https://modelcontextprotocol.io/)
- [ATRS API Documentation](./7.javaconfig-jsp-architecture.md)
