# ATRS MCP Integration Specification

## Overview

Enable AI agents to interact with ATRS (Airline Ticket Reservation System) via Model Context Protocol (MCP) by generating an MCP server from OpenAPI specification.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  ATRS Java  │────▶│  SpringDoc  │────▶│  OpenAPI    │────▶│  MCP Server │
│  REST APIs  │     │  (auto-gen) │     │  Spec       │     │  (generated)│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## Approach

**Strategy:** OpenAPI-to-MCP generation (zero custom code)

| Phase | Action | Output |
|-------|--------|--------|
| 1 | Add SpringDoc dependency | Auto-generated OpenAPI spec |
| 2 | Configure SpringDoc | Customized API documentation |
| 3 | Generate MCP server | Working MCP server |
| 4 | Test with AI agent | Validated integration |

---

## Phase 1: Add SpringDoc Dependency

### File: `atrs-web/pom.xml`

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

### Expected Endpoints (after restart)

| URL | Purpose |
|-----|---------|
| `/atrs/v3/api-docs` | OpenAPI JSON spec |
| `/atrs/v3/api-docs.yaml` | OpenAPI YAML spec |
| `/atrs/swagger-ui.html` | Interactive API docs |

---

## Phase 2: SpringDoc Configuration

### File: `atrs-env/src/main/resources/application.properties`

```properties
# SpringDoc Configuration
springdoc.api-docs.path=/v3/api-docs
springdoc.swagger-ui.path=/swagger-ui.html
springdoc.swagger-ui.operationsSorter=method
springdoc.default-produces-media-type=application/json
```

### Optional: OpenAPI Metadata Config

```java
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI atrsOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("ATRS - Airline Ticket Reservation System API")
                .description("API for flight search, ticket booking, and member management")
                .version("1.0.0"))
            .externalDocs(new ExternalDocumentation()
                .description("ATRS Documentation")
                .url("https://github.com/your-repo/atrs"));
    }
}
```

---

## Phase 3: Generate MCP Server

### Option A: openapi-mcp (Go) - Recommended for Quick Start

```bash
# Install
brew install jedisct1/tap/openapi-mcp

# Generate and run MCP server
openapi-mcp http://localhost:8080/atrs/v3/api-docs
```

### Option B: openapi-mcp-generator (Node.js) - More Configurable

```bash
# Install
npm install -g @anthropic/openapi-mcp-generator

# Generate MCP server
openapi-mcp-generator \
  --spec http://localhost:8080/atrs/v3/api-docs \
  --output ./atrs-mcp \
  --transport stdio
```

### Option C: Save OpenAPI spec locally first

```bash
# Download spec
curl http://localhost:8080/atrs/v3/api-docs > .specs/openapi.json

# Generate from local file
openapi-mcp .specs/openapi.json
```

---

## Phase 4: Claude Desktop Integration

### File: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "atrs": {
      "command": "openapi-mcp",
      "args": ["http://localhost:8080/atrs/v3/api-docs"]
    }
  }
}
```

---

## Expected MCP Tools

Based on ATRS REST API analysis:

| MCP Tool | Source Endpoint | Purpose |
|----------|-----------------|---------|
| `searchFlight` | GET /flight | Search available flights |
| `reserveTicket` | POST /ticket | Create reservation |
| `checkReservation` | GET /ticket/check | Verify reservation exists |
| `checkAuthStatus` | GET /api/auth/status | Check login status |
| `checkMemberAvailable` | GET /api/member/available | Validate membership number |

---

## Optional Enhancements

### A. Add OpenAPI Annotations (Better AI Understanding)

```java
// FlightRestController.java
@Operation(
    summary = "Search available flights",
    description = "Find flights by route, date, and boarding class"
)
@ApiResponses({
    @ApiResponse(responseCode = "200", description = "Flights found"),
    @ApiResponse(responseCode = "400", description = "Invalid search criteria")
})
@GetMapping
public List<FlightResource> searchFlight(
    @Parameter(description = "Departure airport code", example = "HND")
    @RequestParam String depAirportCd,

    @Parameter(description = "Arrival airport code", example = "KIX")
    @RequestParam String arrAirportCd,

    @Parameter(description = "Departure date", example = "2025/01/15")
    @RequestParam String depDate
) { ... }
```

### B. Add Static Reference Data Tools

Create additional endpoints for AI to discover valid values:

```java
@RestController
@RequestMapping("api/reference")
public class ReferenceDataController {

    @GetMapping("/airports")
    public List<Airport> getAirports() { ... }

    @GetMapping("/fare-types")
    public List<FareType> getFareTypes() { ... }

    @GetMapping("/boarding-classes")
    public List<BoardingClass> getBoardingClasses() { ... }
}
```

---

## Testing Checklist

- [ ] ATRS server starts successfully
- [ ] `/v3/api-docs` returns valid OpenAPI JSON
- [ ] `/swagger-ui.html` loads interactive docs
- [ ] MCP server starts without errors
- [ ] AI agent can list available tools
- [ ] AI agent can search flights
- [ ] AI agent can make reservations

---

## Files to Modify

| File | Change |
|------|--------|
| `atrs-web/pom.xml` | Add SpringDoc dependency |
| `atrs-env/.../application.properties` | Add SpringDoc config |
| (Optional) `OpenApiConfig.java` | API metadata |
| (Optional) REST controllers | @Operation annotations |

---

## Dependencies

### Required
- PostgreSQL running (db=atrs, user=postgres, pass=postgres)
- ATRS server running on port 8080

### MCP Generator (choose one)
- `openapi-mcp` (Go): `brew install jedisct1/tap/openapi-mcp`
- `openapi-mcp-generator` (Node): `npm install -g @anthropic/openapi-mcp-generator`

---

## Timeline

| Step | Duration |
|------|----------|
| Add SpringDoc dependency | 5 min |
| Configure & restart | 5 min |
| Generate MCP server | 5 min |
| Test with AI agent | 10 min |
| **Total (basic)** | **~25 min** |
| Add annotations (optional) | 1-2 hrs |

---

## References

- [SpringDoc OpenAPI](https://springdoc.org/)
- [openapi-mcp (Go)](https://github.com/jedisct1/openapi-mcp)
- [openapi-mcp-generator (Node)](https://github.com/harsha-iiiv/openapi-mcp-generator)
- [MCP Specification](https://modelcontextprotocol.io/)
