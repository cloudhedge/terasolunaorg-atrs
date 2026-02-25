# ATRS — REST API Reference

**Document ID:** ATRS-API-001  
**FedRAMP Control Mapping:** SA-5  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Overview

ATRS exposes a RESTful API under the `/api/v1/` path prefix for programmatic access to flight search and ticket reservation functionality.

### 1.1 Base URL

```
https://<host>:<port>/atrs/api/v1
```

### 1.2 Authentication

| Method | Details |
|:-------|:--------|
| **Type** | HTTP Basic Authentication |
| **Credentials** | Membership number + password |
| **Session** | Stateless (no server-side session) |
| **CSRF** | Disabled (stateless context) |

### 1.3 Common Headers

| Header | Value | Required |
|:-------|:------|:---------|
| `Authorization` | `Basic <base64(membershipNumber:password)>` | Yes (for authenticated endpoints) |
| `Content-Type` | `application/json` | Yes (for POST/PUT) |
| `Accept` | `application/json` | Recommended |

### 1.4 Error Response Format

```json
{
  "code": "e.ar.fw.8001",
  "message": "Description of the error",
  "details": [
    {
      "code": "field.error.code",
      "message": "Specific field error message",
      "target": "fieldName"
    }
  ]
}
```

---

## 2. Flight API

### 2.1 Search Flights

Search for available flights based on criteria.

**Endpoint:** `GET /api/v1/flights`

**Controller:** `FlightRestController`

**Query Parameters:**

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `depAirportCd` | String(3) | Yes | Departure airport code |
| `arrAirportCd` | String(3) | Yes | Arrival airport code |
| `depDate` | String (yyyy-MM-dd) | Yes | Departure date |
| `boardingClassCd` | String(1) | No | Boarding class code (N=Normal, S=Special) |

**Response:** `200 OK`

```json
[
  {
    "flightName": "NTT001",
    "departureTime": "0800",
    "arrivalTime": "1000",
    "depAirportCd": "HND",
    "arrAirportCd": "CTS",
    "fareTypes": [
      {
        "fareTypeCd": "RT",
        "fareTypeName": "Regular",
        "fare": 25000,
        "vacantNum": 120
      }
    ]
  }
]
```

**Validation:** `FlightValidator`

**Error Codes:**

| Code | HTTP Status | Description |
|:-----|:-----------|:------------|
| `e.ar.b1.0001` | 400 | Invalid search criteria |
| `e.ar.b1.0002` | 404 | No flights found |

---

## 3. Ticket API

### 3.1 Reserve Ticket

Create a ticket reservation.

**Endpoint:** `POST /api/v1/tickets`

**Controller:** `TicketRestController`

**Authentication:** Required (HTTP Basic)

**Request Body:**

```json
{
  "selectFlights": [
    {
      "departureDate": "2026-03-15",
      "flightName": "NTT001",
      "boardingClassCd": "N",
      "fareTypeCd": "RT"
    }
  ],
  "passengers": [
    {
      "familyName": "田中",
      "givenName": "太郎",
      "age": 30,
      "gender": "M",
      "customerNo": "0000000001"
    }
  ],
  "repFamilyName": "田中",
  "repGivenName": "太郎",
  "repAge": 30,
  "repGender": "M",
  "repTel": "090-1234-5678",
  "repMail": "tanaka@example.com"
}
```

**Validation:** `TicketReserveValidator`, `ReservationFlightValidator`

**Response:** `201 Created`

```json
{
  "reserveNo": "0000000001",
  "totalFare": 25000,
  "reserveDate": "2026-02-24"
}
```

**Error Codes:**

| Code | HTTP Status | Description |
|:-----|:-----------|:------------|
| `e.ar.b2.0001` | 400 | Invalid reservation data |
| `e.ar.b2.0002` | 409 | Insufficient vacant seats |
| `e.ar.b2.0003` | 400 | Invalid flight selection |

---

## 4. Web MVC Controllers (Internal API)

These controllers serve the web UI and are not part of the public REST API.

### 4.1 Authentication

| Endpoint | Method | Controller | Purpose |
|:---------|:-------|:-----------|:--------|
| `/auth/login` | GET | `AuthLoginController` | Display login form |
| `/auth/dologin` | POST | Spring Security Filter | Process login |
| `/auth/dologout` | POST | Spring Security | Process logout |

### 4.2 Flight Search

| Endpoint | Method | Controller | Purpose |
|:---------|:-------|:-----------|:--------|
| `/` | GET | `IndexController` | Home page with search form |
| `/ticket/search` | POST | `TicketSearchController` | Execute flight search |

### 4.3 Ticket Reservation

| Endpoint | Method | Controller | Purpose |
|:---------|:-------|:-----------|:--------|
| `/ticket/reserve` | POST | `TicketReserveController` | Select flights for reservation |
| `/ticket/reserve?confirm` | POST | `TicketReserveController` | Confirm reservation |
| `/ticket/reserve?complete` | POST | `TicketReserveController` | Complete reservation |

### 4.4 Member Management

| Endpoint | Method | Controller | Auth |
|:---------|:-------|:-----------|:-----|
| `/member/register` | GET/POST | `MemberRegisterController` | Public |
| `/member/update` | GET/POST | `MemberUpdateController` | ROLE_MEMBER |

### 4.5 Reports

| Endpoint | Method | Controller | Auth |
|:---------|:-------|:-----------|:-----|
| `/HistoryReport/download` | GET | `ReservationHistoryReportController` | ROLE_MEMBER |

---

## 5. Data Models

### 5.1 FlightResource

| Field | Type | Description |
|:------|:-----|:------------|
| `flightName` | String | Flight identifier (e.g., "NTT001") |
| `departureTime` | String | Departure time (HHMM) |
| `arrivalTime` | String | Arrival time (HHMM) |
| `depAirportCd` | String | Departure airport code |
| `arrAirportCd` | String | Arrival airport code |
| `fareTypes` | FareTypeResource[] | Available fare types |

### 5.2 FareTypeResource

| Field | Type | Description |
|:------|:-----|:------------|
| `fareTypeCd` | String | Fare type code |
| `fareTypeName` | String | Fare type name |
| `fare` | Integer | Calculated fare amount |
| `vacantNum` | Integer | Available seats |

### 5.3 PassengerResource

| Field | Type | Description |
|:------|:-----|:------------|
| `familyName` | String | Passenger family name |
| `givenName` | String | Passenger given name |
| `age` | Integer | Passenger age |
| `gender` | String | Gender (M/F) |
| `customerNo` | String | Member number (optional) |

---

## 6. Rate Limiting & Security

| Control | Current | FedRAMP Recommendation |
|:--------|:--------|:----------------------|
| Rate limiting | Not implemented | 100 requests/min per IP |
| Request size limit | Tomcat default | 10 MB max |
| API versioning | `/api/v1/` | Maintain backward compatibility |
| Input validation | Multi-layer | All parameters validated |
| Authentication | HTTP Basic | Migrate to OAuth 2.0 |
