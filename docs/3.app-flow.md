# ATRS Application Flows

This document describes the user flows and features available in the Airline Ticket Reservation System (ATRS).

## Application Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ATRS HOMEPAGE                           │
│                  http://localhost:8080/atrs/                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │  Flight Search   │   │   Register   │   │      Login      │  │
│  └────────┬─────────┘   └──────┬───────┘   └────────┬────────┘  │
│           │                    │                    │           │
│           ▼                    ▼                    ▼           │
│    Search Results        Registration Form      Login Form      │
│           │                    │                    │           │
│           ▼                    │                    │           │
│    Select Flight(s)            │                    │           │
│           │                    │                    │           │
│           ▼                    │                    │           │
│    ┌──────────────┐            │                    │           │
│    │ Login Modal  │◄───────────┴────────────────────┘           │
│    └──────┬───────┘                                             │
│           │                                                     │
│     ┌─────┴─────┐                                               │
│     ▼           ▼                                               │
│  Login &    Guest                                               │
│  Reserve    Reserve                                             │
│     │           │                                               │
│     └─────┬─────┘                                               │
│           ▼                                                     │
│    Passenger Details                                            │
│           │                                                     │
│           ▼                                                     │
│    Booking Confirmation                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Flight Search

**URL:** `/atrs/` (Homepage) → `/atrs/ticket/search`

### Search Form Fields

| Field | Options | Description |
|-------|---------|-------------|
| Flight Type | Round-trip / One-way | Select trip type |
| Departure Airport | 50+ airports | Japanese domestic airports |
| Arrival Airport | 50+ airports | Japanese domestic airports |
| Departure Date | Date picker | Outbound travel date |
| Return Date | Date picker | Return date (round-trip only) |
| Seat Class | Economy / Special | Standard or premium seating |

### Search Results

- Displays available flights with:
  - Flight number (e.g., NTT001, NTT031)
  - Departure/Arrival times
  - Route information
  - Pricing
  - Seat availability indicators
- Pagination: 10 flights per page
- Radio buttons to select flights

### Seat Availability Indicators

| Indicator | Meaning |
|-----------|---------|
| (no label) | Seats available |
| "X seats left" | Limited availability (shows count) |
| "Sold out" | No seats available (disabled) |

---

## 2. Booking Flow

### Step 1: Flight Selection
- Select outbound flight (required)
- Select return flight (round-trip only)
- Click "Reserve Selected Flight"

### Step 2: Login/Guest Modal
Two options presented:

| Option | Description |
|--------|-------------|
| **Login & Reserve** | For registered members - enter Member ID + Password |
| **Reserve as Guest** | No registration required - proceed directly to booking |

### Step 3: Passenger Details Form

**Passenger Information** (up to 6 passengers):

| Field | Format | Required |
|-------|--------|----------|
| Name | Katakana (Last + First) | Yes |
| Age | Number | Yes |
| Gender | Male / Female | Yes |
| Member ID | 10 digits | No |

**Representative (Contact) Information:**

| Field | Format | Required |
|-------|--------|----------|
| Name | Katakana (Last + First) | Yes |
| Age | Number | Yes |
| Gender | Male / Female | Yes |
| Member ID | 10 digits | No |
| Phone | XXX-XXXX-XXXX | Yes |
| Email | email@example.com | Yes |

**Form Actions:**
- "Add Passenger" - Add additional passengers
- "Copy from Passenger 1" - Auto-fill representative info
- "Return to Seat List" - Go back to search results
- "Confirm Reservation" - Proceed to confirmation

### Step 4: Booking Confirmation
- Review booking details
- Complete payment
- Receive confirmation

---

## 3. Member Registration

**URL:** `/atrs/member/register`

### Registration Form Fields

| Field | Description | Validation |
|-------|-------------|------------|
| Full Name | Kanji characters | Required |
| Name (Katakana) | Katakana reading | Required |
| Gender | Male / Female | Required |
| Date of Birth | YYYY/MM/DD | Required |
| Phone Number | XXX-XXXX-XXXX format | Required |
| Postal Code | XXX-XXXX format | Required |
| Address | Full address | Required |
| Email | Valid email | Required + Confirmation |
| Credit Card Type | VISA / MasterCard / JCB / DNS / Amex | Required |
| Credit Card Number | Card number | Required |
| Card Expiry | Month / Year | Required |
| Password | Account password | Required + Confirmation |

---

## 4. Member Login

**URL:** `/atrs/login`

### Login Form

| Field | Description |
|-------|-------------|
| Member ID | Registered member number |
| Password | Account password |

### Post-Login Features (for logged-in members)
- View booking history
- Update member information
- Faster checkout with saved details

---

## Key Application Features

### Airports
- 50+ Japanese domestic airports supported
- Major hubs: Tokyo (Haneda/Narita), Osaka (Itami/Kansai/Kobe), Sapporo, Nagoya, Fukuoka, Okinawa

### Pricing (Example: Tokyo-Osaka route)
| Trip Type | Price |
|-----------|-------|
| Round-trip | ¥19,600 |
| One-way | ¥20,600 |

### Booking Constraints
- **Date Range:** 3-month booking window (e.g., Dec 15 - Mar 15)
- **Passengers:** Up to 6 per booking
- **Seat Classes:** Economy and Special/Business

### Technical Details
- **Framework:** Spring MVC with TERASOLUNA
- **Server:** Apache Tomcat 10.1.34
- **Language:** Japanese UI (application is in Japanese)

---

## URL Reference

| Page | URL Path |
|------|----------|
| Homepage | `/atrs/` |
| Flight Search | `/atrs/ticket/search` |
| Login | `/atrs/login` |
| Member Registration | `/atrs/member/register` |
