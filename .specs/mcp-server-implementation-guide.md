# ATRS MCP Server Implementation Guide

## Overview

This guide provides complete instructions for building a custom MCP (Model Context Protocol) server for the ATRS (Airline Ticket Reservation System) Java Spring application. The MCP server enables AI agents like Claude to interact with the ATRS REST API.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude/Agent   │────▶│   MCP Server    │────▶│   ATRS REST API │
│  (MCP Client)   │◀────│  (Node.js/TS)   │◀────│  /api/v1/*      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Table of Contents

1. [Folder Structure](#1-folder-structure)
2. [Package Configuration](#2-package-configuration)
3. [TypeScript Configuration](#3-typescript-configuration)
4. [Source Files](#4-source-files)
5. [API Reference](#5-api-reference)
6. [MCP Tools](#6-mcp-tools)
7. [Configuration & Deployment](#7-configuration--deployment)
8. [Testing](#8-testing)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Folder Structure

```
atrs-mcp-server/
├── .gitignore
├── package.json
├── tsconfig.json
├── README.md
└── src/
    ├── index.ts              # Entry point (stdio transport)
    ├── server.ts             # MCP server with all tools registered
    ├── config.ts             # Environment configuration
    ├── api/
    │   ├── client.ts         # HTTP client for ATRS REST APIs
    │   └── types.ts          # TypeScript interfaces for API
    └── data/
        ├── airports.ts       # Static airport reference data (53 airports)
        └── fare-types.ts     # Fare type reference data (10 types)
```

---

## 2. Package Configuration

### package.json

```json
{
  "name": "atrs-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for ATRS flight reservation APIs",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "atrs-mcp-server": "dist/index.js"
  },
  "files": [
    "dist"
  ],
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsc --watch",
    "prepublishOnly": "npm run build"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.3.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### .gitignore

```
node_modules/
dist/
*.log
.env
```

---

## 3. TypeScript Configuration

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 4. Source Files

### 4.1 src/index.ts

Entry point that starts the MCP server.

```typescript
#!/usr/bin/env node
import { startServer } from './server.js';

startServer().catch((error) => {
  console.error('Failed to start ATRS MCP Server:', error);
  process.exit(1);
});
```

---

### 4.2 src/config.ts

Configuration loader with auto-login support.

```typescript
/**
 * Configuration for ATRS MCP Server
 */
export interface Config {
  /** Base URL for ATRS API (e.g., http://localhost:8080/atrs) */
  apiBaseUrl: string;
  /** Request timeout in milliseconds */
  timeout: number;
  /** Optional credentials for auto-login */
  credentials?: {
    membershipNumber: string;
    password: string;
  };
}

/**
 * Load configuration from environment variables
 */
export function loadConfig(): Config {
  const apiBaseUrl = process.env.ATRS_API_BASE_URL || 'http://localhost:8080/atrs';
  const timeout = parseInt(process.env.ATRS_TIMEOUT || '30000', 10);

  // Optional auto-login credentials
  const membershipNumber = process.env.ATRS_USER;
  const password = process.env.ATRS_PASSWORD;
  const credentials =
    membershipNumber && password ? { membershipNumber, password } : undefined;

  return {
    apiBaseUrl,
    timeout,
    credentials,
  };
}
```

---

### 4.3 src/api/types.ts

TypeScript interfaces matching ATRS REST API contracts.

```typescript
/**
 * ATRS API Type Definitions
 * Based on Java classes in jp.co.ntt.atrs.api.* and jp.co.ntt.atrs.domain.model.*
 */

// ============ Enums ============
export type FlightType = 'RT' | 'OW'; // RT=Round-trip, OW=One-way
export type BoardingClassCd = 'N' | 'S'; // N=Normal, S=Special
export type Gender = 'F' | 'M'; // F=Female, M=Male
export type FareTypeCd =
  | 'OW'
  | 'RT'
  | 'RD1'
  | 'RD7'
  | 'ED'
  | 'LD'
  | 'GD'
  | 'SOW'
  | 'SRT'
  | 'SRD';

// ============ Request Types ============

/**
 * Flight search query parameters
 * Endpoint: GET /api/v1/flight
 */
export interface FlightSearchQuery {
  flightType: FlightType;
  depAirportCd: string; // 3-letter code
  arrAirportCd: string; // 3-letter code
  depDate: string; // format: yyyy/MM/dd
  boardingClassCd: BoardingClassCd;
}

/**
 * Passenger information for booking
 */
export interface PassengerResource {
  familyName: string; // Full-width Katakana, 1-10 chars
  givenName: string; // Full-width Katakana, 1-10 chars
  age: number;
  gender: Gender;
  membershipNumber?: string; // 10 digits
}

/**
 * Selected flight for booking
 */
export interface SelectFlightResource {
  depDate: string; // format: yyyy/MM/dd
  flightName: string; // e.g., "NTT001"
  boardingClassCd: BoardingClassCd;
  fareTypeCd: FareTypeCd;
}

/**
 * Ticket reservation request
 * Endpoint: POST /api/v1/ticket
 */
export interface TicketReserveRequest {
  // Contact/Representative info
  repFamilyName: string; // Full-width Katakana, 1-10 chars
  repGivenName: string; // Full-width Katakana, 1-10 chars
  repAge: number;
  repGender: Gender;
  repMembershipNumber?: string; // 10 digits
  repTel1: string; // 2-5 digits (area code)
  repTel2: string; // 1-4 digits
  repTel3: string; // exactly 4 digits
  repMail: string; // email format, max 256 chars

  // Flight info
  flightType: FlightType;
  selectFlightResourceList: SelectFlightResource[];
  passengerResourceList: PassengerResource[];
}

// ============ Response Types ============

/**
 * Fare type information in flight search response
 */
export interface FareTypeResource {
  fareTypeName: string; // e.g., "片道運賃"
  fare: string; // Price as string, e.g., "20600"
  vacantNum: number; // Available seats
}

/**
 * Flight information in search response
 */
export interface FlightResource {
  flightName: string; // e.g., "NTT001"
  depAirportName: string; // e.g., "東京(羽田)"
  arrAirportName: string; // e.g., "大阪(伊丹)"
  depTime: string; // e.g., "08:00"
  arrTime: string; // e.g., "09:15"
  depDate: string; // e.g., "2025/12/26"
  boardingClassCd: BoardingClassCd;
  fareTypes: Record<string, FareTypeResource>; // Key is FareTypeCd
}

/**
 * Ticket reservation response
 */
export interface TicketReserveResponse {
  reserveNo: string; // e.g., "ABC12345"
  paymentDate: string; // Payment deadline date
  totalFare: number; // Total fare in yen
}

/**
 * API error response
 */
export interface ApiError {
  code: string; // e.g., "e.ar.b1.2001"
  message: string | null;
}
```

---

### 4.4 src/api/client.ts

HTTP client with Basic Auth support.

```typescript
import type { Config } from '../config.js';
import type {
  FlightSearchQuery,
  FlightResource,
  TicketReserveRequest,
  TicketReserveResponse,
  ApiError,
} from './types.js';

/**
 * HTTP client for ATRS REST APIs
 * Base URL: /api/v1/*
 */
export class AtrsApiClient {
  private baseUrl: string;
  private timeout: number;
  private authHeader?: string;

  constructor(config: Config) {
    this.baseUrl = config.apiBaseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = config.timeout;

    // Auto-login if credentials provided
    if (config.credentials) {
      this.setCredentials(
        config.credentials.membershipNumber,
        config.credentials.password
      );
    }
  }

  /**
   * Set Basic Auth credentials for all subsequent requests
   */
  setCredentials(membershipNumber: string, password: string): void {
    const encoded = Buffer.from(`${membershipNumber}:${password}`).toString(
      'base64'
    );
    this.authHeader = `Basic ${encoded}`;
  }

  /**
   * Clear stored credentials
   */
  clearCredentials(): void {
    this.authHeader = undefined;
  }

  /**
   * Check if credentials are set
   */
  isAuthenticated(): boolean {
    return this.authHeader !== undefined;
  }

  /**
   * Search for available flights
   * GET /api/v1/flight
   */
  async searchFlights(query: FlightSearchQuery): Promise<FlightResource[]> {
    const params = new URLSearchParams({
      flightType: query.flightType,
      depAirportCd: query.depAirportCd,
      arrAirportCd: query.arrAirportCd,
      depDate: query.depDate,
      boardingClassCd: query.boardingClassCd,
    });

    const response = await this.fetch(`/api/v1/flight?${params.toString()}`);

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(`Flight search failed: ${error.code} - ${error.message}`);
    }

    return response.json();
  }

  /**
   * Reserve a ticket
   * POST /api/v1/ticket
   */
  async reserveTicket(
    request: TicketReserveRequest
  ): Promise<TicketReserveResponse> {
    const response = await this.fetch('/api/v1/ticket', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(`Reservation failed: ${error.code} - ${error.message}`);
    }

    return response.json();
  }

  /**
   * Check if a reservation exists
   * GET /api/v1/ticket/check?reserveNo=X
   */
  async checkReservation(reserveNo: string): Promise<boolean> {
    const params = new URLSearchParams({ reserveNo });
    const response = await this.fetch(
      `/api/v1/ticket/check?${params.toString()}`
    );

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(
        `Reservation check failed: ${error.code} - ${error.message}`
      );
    }

    return response.json();
  }

  /**
   * Check authentication status
   * Returns true if credentials are set (REST API uses Basic Auth per-request)
   */
  async checkAuthStatus(): Promise<boolean> {
    return this.isAuthenticated();
  }

  /**
   * Check if a membership number is valid
   * GET /api/member/available?membershipNumber=X
   */
  async checkMember(membershipNumber: string): Promise<boolean> {
    const params = new URLSearchParams({ membershipNumber });
    const response = await this.fetch(
      `/api/member/available?${params.toString()}`
    );
    return response.status === 200;
  }

  /**
   * Internal fetch with timeout, base URL, and auth header
   */
  private async fetch(
    path: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    // Merge headers with auth header if set
    const headers = new Headers(options.headers);
    if (this.authHeader) {
      headers.set('Authorization', this.authHeader);
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });
      return response;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Parse error response
   */
  private async parseError(response: Response): Promise<ApiError> {
    try {
      return await response.json();
    } catch {
      return {
        code: `HTTP_${response.status}`,
        message: response.statusText,
      };
    }
  }
}
```

---

### 4.5 src/data/airports.ts

Complete airport reference data (53 airports).

```typescript
/**
 * Airport reference data sourced from:
 * JavaConfig-JSP/atrs/atrs-initdb/src/sqls/integration-test-postgres/00200_insert_fixed_value.sql
 */
export interface Airport {
  code: string;
  name: string; // Japanese name from DB
  nameEn: string; // English name for AI
  displayOrder: number;
}

export const airports: Airport[] = [
  // Major airports (displayOrder 1-9)
  { code: 'HND', name: '東京(羽田)', nameEn: 'Tokyo Haneda', displayOrder: 1 },
  { code: 'NRT', name: '東京(成田)', nameEn: 'Tokyo Narita', displayOrder: 2 },
  { code: 'ITM', name: '大阪(伊丹)', nameEn: 'Osaka Itami', displayOrder: 3 },
  { code: 'KIX', name: '大阪(関西)', nameEn: 'Osaka Kansai', displayOrder: 4 },
  { code: 'UKB', name: '大阪(神戸)', nameEn: 'Osaka Kobe', displayOrder: 5 },
  { code: 'SPK', name: '札幌(千歳)', nameEn: 'Sapporo Chitose', displayOrder: 6 },
  { code: 'NGO', name: '名古屋(中部)', nameEn: 'Nagoya Chubu', displayOrder: 7 },
  { code: 'FUK', name: '福岡', nameEn: 'Fukuoka', displayOrder: 8 },
  { code: 'OKA', name: '沖縄', nameEn: 'Okinawa', displayOrder: 9 },

  // Regional airports (displayOrder 100+)
  { code: 'OKD', name: '札幌(丘珠)', nameEn: 'Sapporo Okadama', displayOrder: 100 },
  { code: 'RIS', name: '利尻', nameEn: 'Rishiri', displayOrder: 101 },
  { code: 'WKJ', name: '稚内', nameEn: 'Wakkanai', displayOrder: 102 },
  { code: 'MBE', name: 'オホーツク紋別', nameEn: 'Okhotsk Monbetsu', displayOrder: 103 },
  { code: 'MMB', name: '女満別', nameEn: 'Memambetsu', displayOrder: 104 },
  { code: 'AKJ', name: '旭川', nameEn: 'Asahikawa', displayOrder: 105 },
  { code: 'SHB', name: '根室中標津', nameEn: 'Nemuro Nakashibetsu', displayOrder: 106 },
  { code: 'KUH', name: '釧路', nameEn: 'Kushiro', displayOrder: 107 },
  { code: 'HKD', name: '函館', nameEn: 'Hakodate', displayOrder: 108 },
  { code: 'ONJ', name: '大館能代', nameEn: 'Odate Noshiro', displayOrder: 109 },
  { code: 'AXT', name: '秋田', nameEn: 'Akita', displayOrder: 110 },
  { code: 'SYO', name: '庄内', nameEn: 'Shonai', displayOrder: 111 },
  { code: 'SDJ', name: '仙台', nameEn: 'Sendai', displayOrder: 112 },
  { code: 'FKS', name: '福島', nameEn: 'Fukushima', displayOrder: 113 },
  { code: 'OIM', name: '大島', nameEn: 'Oshima', displayOrder: 114 },
  { code: 'MYE', name: '三宅島', nameEn: 'Miyakejima', displayOrder: 115 },
  { code: 'HAC', name: '八丈島', nameEn: 'Hachijojima', displayOrder: 116 },
  { code: 'KIJ', name: '新潟', nameEn: 'Niigata', displayOrder: 117 },
  { code: 'TOY', name: '富山', nameEn: 'Toyama', displayOrder: 118 },
  { code: 'KMQ', name: '小松', nameEn: 'Komatsu', displayOrder: 119 },
  { code: 'NTQ', name: '能登', nameEn: 'Noto', displayOrder: 120 },
  { code: 'OKJ', name: '岡山', nameEn: 'Okayama', displayOrder: 121 },
  { code: 'HIJ', name: '広島', nameEn: 'Hiroshima', displayOrder: 122 },
  { code: 'UBJ', name: '山口宇部', nameEn: 'Yamaguchi Ube', displayOrder: 123 },
  { code: 'TTJ', name: '鳥取', nameEn: 'Tottori', displayOrder: 124 },
  { code: 'YGJ', name: '米子', nameEn: 'Yonago', displayOrder: 125 },
  { code: 'IWJ', name: '萩・石見', nameEn: 'Hagi Iwami', displayOrder: 126 },
  { code: 'TAK', name: '高松', nameEn: 'Takamatsu', displayOrder: 127 },
  { code: 'TKS', name: '徳島', nameEn: 'Tokushima', displayOrder: 128 },
  { code: 'MYJ', name: '松山', nameEn: 'Matsuyama', displayOrder: 129 },
  { code: 'KCZ', name: '高知', nameEn: 'Kochi', displayOrder: 130 },
  { code: 'KKJ', name: '北九州', nameEn: 'Kitakyushu', displayOrder: 131 },
  { code: 'HSG', name: '佐賀', nameEn: 'Saga', displayOrder: 132 },
  { code: 'OIT', name: '大分', nameEn: 'Oita', displayOrder: 133 },
  { code: 'KMJ', name: '熊本', nameEn: 'Kumamoto', displayOrder: 134 },
  { code: 'NGS', name: '長崎', nameEn: 'Nagasaki', displayOrder: 135 },
  { code: 'TSJ', name: '対馬', nameEn: 'Tsushima', displayOrder: 136 },
  { code: 'FUJ', name: '五島福江', nameEn: 'Goto Fukue', displayOrder: 137 },
  { code: 'KMI', name: '宮崎', nameEn: 'Miyazaki', displayOrder: 138 },
  { code: 'KOJ', name: '鹿児島', nameEn: 'Kagoshima', displayOrder: 139 },
  { code: 'MMY', name: '宮古', nameEn: 'Miyako', displayOrder: 140 },
  { code: 'ISG', name: '石垣', nameEn: 'Ishigaki', displayOrder: 141 },
];

/**
 * Find airport by code or name (English or Japanese)
 */
export function findAirport(query: string): Airport | undefined {
  const q = query.toLowerCase().trim();
  return airports.find(
    (a) =>
      a.code.toLowerCase() === q ||
      a.nameEn.toLowerCase().includes(q) ||
      a.name.includes(query)
  );
}

/**
 * Get airport code from city name or code
 */
export function getAirportCode(cityOrCode: string): string | undefined {
  const airport = findAirport(cityOrCode);
  return airport?.code;
}
```

---

### 4.6 src/data/fare-types.ts

Complete fare type reference data (10 types).

```typescript
/**
 * Fare type reference data sourced from:
 * JavaConfig-JSP/atrs/atrs-initdb/src/sqls/integration-test-postgres/00200_insert_fixed_value.sql
 */
export interface FareType {
  code: string;
  name: string; // Japanese name from DB
  nameEn: string; // English name for AI
  discountRate: number; // Percentage discount
  rsrvAvailableStartDayNum: number; // Days before departure to start booking
  rsrvAvailableEndDayNum: number; // Days before departure to end booking
  passengerMinNum: number; // Minimum passengers required
  displayOrder: number;
  seatClass: 'N' | 'S'; // N=Normal, S=Special
}

export const fareTypes: FareType[] = [
  // Normal seat fare types (displayOrder 1-7)
  {
    code: 'OW',
    name: '片道運賃',
    nameEn: 'One-way',
    discountRate: 0,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 1,
    seatClass: 'N',
  },
  {
    code: 'RT',
    name: '往復運賃',
    nameEn: 'Round-trip',
    discountRate: 5,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 2,
    seatClass: 'N',
  },
  {
    code: 'RD1',
    name: '予約割1',
    nameEn: 'Advance 1-day',
    discountRate: 10,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 1,
    displayOrder: 3,
    seatClass: 'N',
  },
  {
    code: 'RD7',
    name: '予約割7',
    nameEn: 'Advance 7-day',
    discountRate: 20,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 7,
    passengerMinNum: 1,
    displayOrder: 4,
    seatClass: 'N',
  },
  {
    code: 'ED',
    name: '早期割',
    nameEn: 'Early Bird',
    discountRate: 30,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 30,
    passengerMinNum: 1,
    displayOrder: 5,
    seatClass: 'N',
  },
  {
    code: 'LD',
    name: 'レディース割',
    nameEn: 'Ladies Discount',
    discountRate: 30,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 1,
    displayOrder: 6,
    seatClass: 'N',
  },
  {
    code: 'GD',
    name: 'グループ割',
    nameEn: 'Group Discount',
    discountRate: 30,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 3,
    displayOrder: 7,
    seatClass: 'N',
  },
  // Special seat fare types (displayOrder 100+)
  {
    code: 'SOW',
    name: '特別片道運賃',
    nameEn: 'Special One-way',
    discountRate: 0,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 100,
    seatClass: 'S',
  },
  {
    code: 'SRT',
    name: '特別往復運賃',
    nameEn: 'Special Round-trip',
    discountRate: 5,
    rsrvAvailableStartDayNum: 90,
    rsrvAvailableEndDayNum: 0,
    passengerMinNum: 1,
    displayOrder: 101,
    seatClass: 'S',
  },
  {
    code: 'SRD',
    name: '特別予約割',
    nameEn: 'Special Advance',
    discountRate: 10,
    rsrvAvailableStartDayNum: 60,
    rsrvAvailableEndDayNum: 1,
    passengerMinNum: 1,
    displayOrder: 102,
    seatClass: 'S',
  },
];

/**
 * Find fare type by code or name
 */
export function findFareType(query: string): FareType | undefined {
  const q = query.toLowerCase().trim();
  return fareTypes.find(
    (f) =>
      f.code.toLowerCase() === q ||
      f.nameEn.toLowerCase().includes(q) ||
      f.name.includes(query)
  );
}
```

---

### 4.7 src/server.ts

MCP server with all tools registered.

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { loadConfig } from './config.js';
import { AtrsApiClient } from './api/client.js';
import { airports, findAirport } from './data/airports.js';
import { fareTypes, findFareType } from './data/fare-types.js';
import type { FareTypeCd } from './api/types.js';

/**
 * Create and configure the MCP server for ATRS
 */
export function createServer(): McpServer {
  const config = loadConfig();
  const apiClient = new AtrsApiClient(config);

  const server = new McpServer({
    name: 'atrs-mcp-server',
    version: '1.0.0',
  });

  // ========== Tool 1: search_flights ==========
  server.registerTool(
    'search_flights',
    {
      description:
        'Search for available flights between airports. Returns flight options with fares and seat availability.',
      inputSchema: {
        from: z.string().describe('Departure airport code (e.g., HND, NRT) or city name (e.g., Tokyo)'),
        to: z.string().describe('Arrival airport code (e.g., KIX, ITM) or city name (e.g., Osaka)'),
        date: z.string().describe('Departure date in yyyy/MM/dd format (e.g., 2025/01/15)'),
        flightType: z
          .enum(['OW', 'RT'])
          .default('OW')
          .describe('OW=one-way, RT=round-trip'),
        seatClass: z
          .enum(['N', 'S'])
          .default('N')
          .describe('N=normal/economy, S=special/premium'),
      },
    },
    async ({ from, to, date, flightType = 'OW', seatClass = 'N' }) => {
      try {
        // Resolve airport codes from city names
        const depAirport = findAirport(from);
        const arrAirport = findAirport(to);

        if (!depAirport) {
          return {
            content: [
              {
                type: 'text',
                text: `Unknown departure airport: "${from}". Use list_airports to see valid options.`,
              },
            ],
            isError: true,
          };
        }
        if (!arrAirport) {
          return {
            content: [
              {
                type: 'text',
                text: `Unknown arrival airport: "${to}". Use list_airports to see valid options.`,
              },
            ],
            isError: true,
          };
        }

        const flights = await apiClient.searchFlights({
          depAirportCd: depAirport.code,
          arrAirportCd: arrAirport.code,
          depDate: date,
          flightType: flightType,
          boardingClassCd: seatClass,
        });

        if (flights.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: `No flights found from ${depAirport.nameEn} to ${arrAirport.nameEn} on ${date}.`,
              },
            ],
          };
        }

        // Format results for AI
        const formatted = flights.map((f) => ({
          flight: f.flightName,
          route: `${f.depAirportName} → ${f.arrAirportName}`,
          departure: f.depTime,
          arrival: f.arrTime,
          date: f.depDate,
          seatClass: f.boardingClassCd === 'N' ? 'Economy' : 'Premium',
          fares: Object.entries(f.fareTypes).map(([code, fare]) => ({
            type: fare.fareTypeName,
            code,
            price: `¥${fare.fare}`,
            seatsAvailable: fare.vacantNum,
          })),
        }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(formatted, null, 2),
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Flight search failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 2: check_reservation ==========
  server.registerTool(
    'check_reservation',
    {
      description: 'Check if a reservation number exists in the system',
      inputSchema: {
        reservationNumber: z.string().describe('The reservation number to check'),
      },
    },
    async ({ reservationNumber }) => {
      try {
        const exists = await apiClient.checkReservation(reservationNumber);
        return {
          content: [
            {
              type: 'text',
              text: exists
                ? `Reservation ${reservationNumber} exists and is valid.`
                : `Reservation ${reservationNumber} not found.`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Reservation check failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 3: reserve_ticket ==========
  server.registerTool(
    'reserve_ticket',
    {
      description:
        'Reserve a flight ticket for passengers. Names should be in Katakana (Japanese) or the LLM should convert English names to Katakana.',
      inputSchema: {
        flightName: z.string().describe('Flight name (e.g., NTT001)'),
        departureDate: z.string().describe('Departure date in yyyy/MM/dd format'),
        fareType: z
          .string()
          .describe('Fare type code: OW, RT, RD1, RD7, ED, LD, GD, SOW, SRT, SRD'),
        seatClass: z
          .enum(['N', 'S'])
          .default('N')
          .describe('N=normal/economy, S=special/premium'),
        flightType: z
          .enum(['OW', 'RT'])
          .default('OW')
          .describe('OW=one-way, RT=round-trip'),
        passengers: z
          .array(
            z.object({
              familyName: z.string().describe('Family name in Katakana (e.g., タナカ)'),
              givenName: z.string().describe('Given name in Katakana (e.g., タロウ)'),
              age: z.number().describe('Age'),
              gender: z.enum(['M', 'F']).describe('M=male, F=female'),
            })
          )
          .describe('List of passengers'),
        contact: z
          .object({
            familyName: z.string().describe('Contact family name in Katakana'),
            givenName: z.string().describe('Contact given name in Katakana'),
            age: z.number().describe('Contact age'),
            gender: z.enum(['M', 'F']).describe('Contact gender'),
            phone: z.string().describe('Phone number (e.g., 090-1234-5678)'),
            email: z.string().describe('Email address'),
          })
          .describe('Contact person information'),
      },
    },
    async ({
      flightName,
      departureDate,
      fareType,
      seatClass = 'N',
      flightType = 'OW',
      passengers,
      contact,
    }) => {
      try {
        // Parse phone number: 090-1234-5678 → repTel1=090, repTel2=1234, repTel3=5678
        const phoneParts = contact.phone.replace(/[^\d]/g, '');
        let repTel1: string, repTel2: string, repTel3: string;

        if (phoneParts.length === 11) {
          // Mobile: 090-1234-5678
          repTel1 = phoneParts.slice(0, 3);
          repTel2 = phoneParts.slice(3, 7);
          repTel3 = phoneParts.slice(7, 11);
        } else if (phoneParts.length === 10) {
          // Landline: 03-1234-5678
          repTel1 = phoneParts.slice(0, 2);
          repTel2 = phoneParts.slice(2, 6);
          repTel3 = phoneParts.slice(6, 10);
        } else {
          return {
            content: [
              {
                type: 'text',
                text: `Invalid phone format: "${contact.phone}". Use format like 090-1234-5678.`,
              },
            ],
            isError: true,
          };
        }

        const result = await apiClient.reserveTicket({
          repFamilyName: contact.familyName,
          repGivenName: contact.givenName,
          repAge: contact.age,
          repGender: contact.gender,
          repTel1,
          repTel2,
          repTel3,
          repMail: contact.email,
          flightType: flightType,
          selectFlightResourceList: [
            {
              depDate: departureDate,
              flightName: flightName,
              boardingClassCd: seatClass,
              fareTypeCd: fareType as FareTypeCd,
            },
          ],
          passengerResourceList: passengers.map((p) => ({
            familyName: p.familyName,
            givenName: p.givenName,
            age: p.age,
            gender: p.gender,
          })),
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  reservationNumber: result.reserveNo,
                  paymentDeadline: result.paymentDate,
                  totalFare: `¥${result.totalFare}`,
                  message: 'Reservation successful!',
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Reservation failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 4: list_airports ==========
  server.registerTool(
    'list_airports',
    {
      description: 'List all available airports with codes and names',
      inputSchema: {
        filter: z.string().optional().describe('Optional filter by name or region'),
      },
    },
    async ({ filter }) => {
      let result = airports;
      if (filter) {
        const f = filter.toLowerCase();
        result = airports.filter(
          (a) =>
            a.code.toLowerCase().includes(f) ||
            a.nameEn.toLowerCase().includes(f) ||
            a.name.includes(filter)
        );
      }

      const formatted = result.map((a) => ({
        code: a.code,
        name: a.nameEn,
        nameJp: a.name,
      }));

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(formatted, null, 2),
          },
        ],
      };
    }
  );

  // ========== Tool 5: list_fare_types ==========
  server.registerTool(
    'list_fare_types',
    {
      description: 'List all available fare types with discounts and requirements',
      inputSchema: {},
    },
    async () => {
      const formatted = fareTypes.map((f) => ({
        code: f.code,
        name: f.nameEn,
        nameJp: f.name,
        discount: `${f.discountRate}%`,
        bookingWindow: `${f.rsrvAvailableEndDayNum}-${f.rsrvAvailableStartDayNum} days before departure`,
        minPassengers: f.passengerMinNum,
        seatClass: f.seatClass === 'N' ? 'Economy' : 'Premium',
      }));

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(formatted, null, 2),
          },
        ],
      };
    }
  );

  // ========== Tool 6: login ==========
  server.registerTool(
    'login',
    {
      description: 'Authenticate with ATRS membership credentials',
      inputSchema: {
        membershipNumber: z.string().describe('10-digit membership number'),
        password: z.string().describe('Account password'),
      },
    },
    async ({ membershipNumber, password }) => {
      try {
        apiClient.setCredentials(membershipNumber, password);
        const isValid = await apiClient.checkAuthStatus();
        if (!isValid) {
          apiClient.clearCredentials();
          return {
            content: [{ type: 'text', text: 'Invalid credentials. Login failed.' }],
            isError: true,
          };
        }
        return {
          content: [{ type: 'text', text: `Logged in as ${membershipNumber}` }],
        };
      } catch (error) {
        apiClient.clearCredentials();
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Login failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 7: logout ==========
  server.registerTool(
    'logout',
    {
      description: 'Clear stored credentials',
      inputSchema: {},
    },
    async () => {
      apiClient.clearCredentials();
      return {
        content: [{ type: 'text', text: 'Logged out successfully.' }],
      };
    }
  );

  // ========== Tool 8: check_auth_status ==========
  server.registerTool(
    'check_auth_status',
    {
      description: 'Check current authentication status',
      inputSchema: {},
    },
    async () => {
      const hasCredentials = apiClient.isAuthenticated();
      if (!hasCredentials) {
        return {
          content: [
            { type: 'text', text: 'Not authenticated. Use login tool to authenticate.' },
          ],
        };
      }
      try {
        const isValid = await apiClient.checkAuthStatus();
        return {
          content: [
            {
              type: 'text',
              text: isValid
                ? 'Authenticated and credentials are valid.'
                : 'Credentials set but may be invalid.',
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Auth check failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  // ========== Tool 9: check_member ==========
  server.registerTool(
    'check_member',
    {
      description: 'Check if a membership number is valid/exists',
      inputSchema: {
        membershipNumber: z.string().describe('10-digit membership number'),
      },
    },
    async ({ membershipNumber }) => {
      try {
        const exists = await apiClient.checkMember(membershipNumber);
        return {
          content: [
            {
              type: 'text',
              text: exists
                ? `Membership ${membershipNumber} is valid.`
                : `Membership ${membershipNumber} not found.`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{ type: 'text', text: `Member check failed: ${message}` }],
          isError: true,
        };
      }
    }
  );

  return server;
}

/**
 * Start the MCP server with stdio transport
 */
export async function startServer(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);
  console.error('ATRS MCP Server started');
}
```

---

## 5. API Reference

### REST API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/flight` | GET | Search available flights | Optional |
| `/api/v1/ticket` | POST | Reserve a ticket | Optional |
| `/api/v1/ticket/check` | GET | Check if reservation exists | Optional |
| `/api/member/available` | GET | Check if membership exists | Optional |

### Authentication

- REST API uses HTTP Basic Auth
- Auth is optional (endpoints use `permitAll()`)
- Credentials: `membershipNumber:password` base64 encoded
- Session: Stateless

### Date Format

- API expects: `yyyy/MM/dd` (e.g., `2025/01/15`)
- NOT ISO format

### Passenger Names

- **IMPORTANT**: API requires Full-width Katakana for names
- MCP server should accept both English and Katakana
- If English names are provided, the LLM (Claude) should convert them to Katakana before making the API call
- Example: "Tanaka Taro" → "タナカ タロウ"

---

## 6. MCP Tools

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `search_flights` | Search available flights | from, to, date |
| `check_reservation` | Check if reservation exists | reservationNumber |
| `reserve_ticket` | Reserve a flight ticket | flightName, departureDate, fareType, passengers, contact |
| `list_airports` | List available airports | (none) |
| `list_fare_types` | List fare types with discounts | (none) |
| `login` | Authenticate with credentials | membershipNumber, password |
| `logout` | Clear stored credentials | (none) |
| `check_auth_status` | Check authentication status | (none) |
| `check_member` | Check if membership exists | membershipNumber |

---

## 7. Configuration & Deployment

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ATRS_API_BASE_URL` | `http://localhost:8080/atrs` | ATRS server URL |
| `ATRS_TIMEOUT` | `30000` | Request timeout (ms) |
| `ATRS_USER` | (none) | Auto-login membership number |
| `ATRS_PASSWORD` | (none) | Auto-login password |

### Claude Desktop Configuration

File: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "atrs": {
      "command": "/path/to/node/v20/bin/node",
      "args": ["/path/to/atrs-mcp-server/dist/index.js"],
      "env": {
        "ATRS_API_BASE_URL": "http://localhost:8080/atrs",
        "ATRS_USER": "0000000001",
        "ATRS_PASSWORD": "aaaaa11111"
      }
    }
  }
}
```

**IMPORTANT**: Use full path to Node.js v18+ because MCP SDK requires it.

### OpenCode Configuration

File: `~/.config/opencode/config.json`

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

## 8. Testing

### Build and Test Commands

```bash
# Install dependencies
cd atrs-mcp-server
npm install

# Build TypeScript
npm run build

# Test MCP protocol - list tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node dist/index.js

# Test search_flights
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_flights","arguments":{"from":"HND","to":"ITM","date":"2025/12/26"}}}' | ATRS_API_BASE_URL=http://localhost:8080/atrs node dist/index.js

# Test list_airports
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_airports","arguments":{}}}' | node dist/index.js
```

### Test Credentials

From database seed:

| Member # | Password | Name |
|----------|----------|------|
| 0000000001 | aaaaa11111 | 電電 花子 |
| 0000000002 | aaaaa11111 | 電電 太郎 |

### Test Routes

Database has flight data for these routes:
- HND (Tokyo Haneda) ↔ ITM (Osaka Itami)

---

## 9. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on API calls | Wrong endpoint path | Use `/api/v1/flight` not `/flight` |
| Node version error | MCP SDK needs Node 18+ | Use full path to modern Node in config |
| Zod defaults not applied | MCP SDK limitation | Use JS default params `{ param = 'default' }` |
| No flights found | Test data limited | Use HND↔ITM route with future dates |
| Invalid date | Wrong format | Use `yyyy/MM/dd` not ISO format |
| Name validation error | Not Katakana | Convert English names to Katakana |

### Checking Logs

Claude Desktop logs:
```bash
tail -f ~/Library/Logs/Claude/mcp-server-atrs.log
```

---

## Appendix: Boarding Classes

| Code | Japanese | English | Extra Charge |
|------|----------|---------|--------------|
| N | 一般席 | Normal/Economy | ¥0 |
| S | 特別席 | Special/Premium | ¥5,000 |

---

## Implementation Checklist

- [ ] Create folder structure
- [ ] Initialize npm project (`npm init`)
- [ ] Install dependencies (`npm install`)
- [ ] Create all source files
- [ ] Build TypeScript (`npm run build`)
- [ ] Test with MCP protocol
- [ ] Configure Claude Desktop
- [ ] Test end-to-end with ATRS running

---

## References

- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Specification](https://modelcontextprotocol.io/)
- ATRS Source: `JavaConfig-JSP/atrs/`
- Session files: `.chat-sessions/`
