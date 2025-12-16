# openapi-mcp-generator

**Repository:** https://github.com/harsha-iiiv/openapi-mcp-generator

A CLI tool that converts OpenAPI specifications into MCP servers, enabling AI agents to interact with REST APIs.

---

## Overview

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  OpenAPI Spec   │─────▶│  openapi-mcp-   │─────▶│  MCP Server     │
│  (JSON/YAML)    │      │  generator      │      │  (TypeScript)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

| Attribute | Value |
|-----------|-------|
| Language | Node.js / TypeScript |
| License | MIT |
| Status | Active |
| Requires | Node.js v20+ |

---

## Installation

```bash
npm install -g openapi-mcp-generator
```

---

## Usage

### Basic Generation

```bash
# From URL
openapi-mcp-generator \
  --input http://localhost:8080/atrs/v3/api-docs \
  --output ./atrs-mcp

# From local file
openapi-mcp-generator \
  --input ./openapi.json \
  --output ./atrs-mcp
```

### With Options

```bash
openapi-mcp-generator \
  --input http://localhost:8080/atrs/v3/api-docs \
  --output ./atrs-mcp \
  --server-name "atrs" \
  --transport stdio \
  --base-url http://localhost:8080/atrs
```

---

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | OpenAPI spec URL or file path | Required |
| `--output` | Output directory | Required |
| `--server-name` | Name for the MCP server | From spec |
| `--transport` | stdio, web, streamable-http | stdio |
| `--port` | Port for web/HTTP transport | 3000 |
| `--base-url` | Override API base URL | From spec |

---

## Transport Options

```
┌─────────────────────────────────────────────────────────────────────┐
│                       TRANSPORT MODES                               │
├─────────────────────┬───────────────────────┬───────────────────────┤
│       stdio         │         web (SSE)     │   streamable-http     │
├─────────────────────┼───────────────────────┼───────────────────────┤
│ Local integration   │ Browser test client   │ Production deploy     │
│ Claude Desktop      │ Bidirectional comms   │ Load balancer ready   │
│ Cursor, IDEs        │ Development/debug     │ Session management    │
└─────────────────────┴───────────────────────┴───────────────────────┘
```

---

## Generated Project Structure

```
atrs-mcp/
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── src/
│   ├── index.ts          # Entry point
│   ├── server.ts         # MCP server setup
│   ├── tools/            # Generated tool handlers
│   │   ├── searchFlight.ts
│   │   ├── reserveTicket.ts
│   │   └── ...
│   └── schemas/          # Zod validation schemas
│       ├── FlightResource.ts
│       ├── TicketReserveResource.ts
│       └── ...
└── README.md
```

---

## Authentication

Configure via environment variables:

```bash
# API Key
export API_KEY_MAIN=your_api_key

# Bearer Token
export BEARER_TOKEN_OAUTH=your_token

# Basic Auth
export BASIC_AUTH_ADMIN=username:password

# OAuth2
export OAUTH_CLIENT_ID_SCHEME=client_id
export OAUTH_CLIENT_SECRET_SCHEME=client_secret
```

Pattern: `{AUTH_TYPE}_{SCHEME_NAME}`

---

## Endpoint Filtering with x-mcp Extension

Control which endpoints become MCP tools:

```yaml
# Root level default
x-mcp:
  include: true

paths:
  /internal/debug:
    x-mcp:
      include: false  # Exclude this endpoint

  /flight:
    get:
      x-mcp:
        include: true
        toolName: "search_flights"
        description: "Search for available flights"
```

### Precedence

```
Operation level  >  Path level  >  Root level
```

---

## Running the Generated Server

```bash
# Navigate to generated project
cd atrs-mcp

# Install dependencies
npm install

# Run in stdio mode (for Claude Desktop)
npm start

# Run in web mode (for browser testing)
npm run start:web
```

---

## Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "atrs": {
      "command": "node",
      "args": ["/path/to/atrs-mcp/dist/index.js"],
      "env": {
        "API_KEY_MAIN": "your_api_key"
      }
    }
  }
}
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **OpenAPI 3.0+ Support** | Full spec compatibility |
| **Proxy Mode** | Routes calls to original API with validation |
| **Zod Schemas** | Auto-generated runtime validation |
| **TypeScript** | Fully typed generated code |
| **Customizable** | Modify generated code as needed |

---

## For ATRS Integration

### Step 1: Add SpringDoc to ATRS

```xml
<!-- atrs-web/pom.xml -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

### Step 2: Start ATRS

```bash
cd JavaConfig-JSP/atrs
mvn cargo:run -pl atrs-web
```

### Step 3: Generate MCP Server

```bash
openapi-mcp-generator \
  --input http://localhost:8080/atrs/v3/api-docs \
  --output ./atrs-mcp \
  --server-name "atrs" \
  --transport stdio
```

### Step 4: Run MCP Server

```bash
cd atrs-mcp
npm install
npm start
```

---

## References

- [GitHub Repository](https://github.com/harsha-iiiv/openapi-mcp-generator)
- [MCP Specification](https://modelcontextprotocol.io/)
- [SpringDoc OpenAPI](https://springdoc.org/)
