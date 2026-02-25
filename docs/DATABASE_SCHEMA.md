# ATRS — Database Schema Documentation

**Document ID:** ATRS-DB-001  
**FedRAMP Control Mapping:** SA-5, SC-28  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Entity-Relationship Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  AIRPORT     │     │  ROUTE       │     │  PLANE       │
│──────────────│     │──────────────│     │──────────────│
│ AIRPORT_CD   │◀────│ DEP_AIRPORT  │     │ CRAFT_TYPE   │
│ AIRPORT_NAME │     │ ARR_AIRPORT  │     │ N_SEAT_NUM   │
│ DISPLAY_ORDER│     │ ROUTE_NO     │     │ S_SEAT_NUM   │
└──────────────┘     │ FLIGHT_TIME  │     └──────┬───────┘
                     │ BASIC_FARE   │            │
                     └──────┬───────┘            │
                            │                    │
                     ┌──────▼───────────────────▼┐
                     │  FLIGHT_MASTER             │
                     │────────────────────────────│
                     │ FLIGHT_NAME                │
                     │ ROUTE_NO → ROUTE           │
                     │ DEPARTURE_TIME             │
                     │ ARRIVAL_TIME               │
                     │ CRAFT_TYPE → PLANE         │
                     └──────────┬─────────────────┘
                                │
┌────────────────┐   ┌─────────▼──────────┐   ┌────────────────┐
│ BOARDING_CLASS │   │  FLIGHT            │   │  FARE_TYPE     │
│────────────────│   │────────────────────│   │────────────────│
│ BOARDING_CD    │◀──│ DEPARTURE_DATE     │──▶│ FARE_TYPE_CD   │
│ CLASS_NAME     │   │ FLIGHT_NAME        │   │ FARE_TYPE_NAME │
│ EXTRA_CHARGE   │   │ BOARDING_CLASS_CD  │   │ DISCOUNT_RATE  │
└────────────────┘   │ FARE_TYPE_CD       │   │ RSRV_START_DAY │
                     │ VACANT_NUM         │   │ RSRV_END_DAY   │
                     └─────────┬──────────┘   │ PASSENGER_MIN  │
                               │              └────────────────┘
                     ┌─────────▼──────────┐
                     │  RESERVE_FLIGHT    │
                     │────────────────────│
                     │ RESERVE_FLIGHT_NO  │
                     │ RESERVE_NO → RES.  │──┐
                     │ DEPARTURE_DATE     │  │
                     │ FLIGHT_NAME        │  │
                     │ BOARDING_CLASS_CD  │  │
                     │ FARE_TYPE_CD       │  │
                     └─────────┬──────────┘  │
                               │             │
                     ┌─────────▼──────┐  ┌──▼─────────────┐
                     │  PASSENGER     │  │  RESERVATION   │
                     │────────────────│  │────────────────│
                     │ PASSENGER_NO   │  │ RESERVE_NO     │
                     │ RESERVE_FLT_NO │  │ RESERVE_DATE   │
                     │ FAMILY_NAME    │  │ TOTAL_FARE     │
                     │ GIVEN_NAME     │  │ REP_FAMILY_NAME│
                     │ AGE            │  │ REP_GIVEN_NAME │
                     │ GENDER         │  │ REP_AGE        │
                     │ CUSTOMER_NO?   │  │ REP_GENDER     │
                     └────────────────┘  │ REP_TEL        │
                                         │ REP_MAIL       │
┌────────────────┐                       │ REP_CUSTOMER?  │
│  CREDIT_TYPE   │                       └────────────────┘
│────────────────│
│ CREDIT_TYPE_CD │◀──┐
│ CREDIT_FIRM    │   │
└────────────────┘   │
                     │
              ┌──────┴─────────┐     ┌──────────────────┐
              │  MEMBER        │     │  MEMBER_LOGIN    │
              │────────────────│     │──────────────────│
              │ CUSTOMER_NO    │◀───▶│ CUSTOMER_NO      │
              │ KANJI_FAMILY   │     │ PASSWORD ⚠️      │
              │ KANJI_GIVEN    │     │ LAST_PASSWORD ⚠️  │
              │ KANA_FAMILY    │     │ LOGIN_DATE_TIME  │
              │ KANA_GIVEN     │     │ LOGIN_FLG        │
              │ BIRTHDAY       │     └──────────────────┘
              │ GENDER         │
              │ TEL            │     ┌──────────────────┐
              │ ZIP_CODE       │     │  PEAK_TIME       │
              │ ADDRESS        │     │──────────────────│
              │ MAIL           │     │ PEAK_TIME_CD     │
              │ CREDIT_NO ⚠️   │     │ PEAK_START_DATE  │
              │ CREDIT_TYPE_CD │     │ PEAK_END_DATE    │
              │ CREDIT_TERM ⚠️  │     │ MULT_RATIO       │
              └────────────────┘     └──────────────────┘

⚠️ = Contains sensitive data (PII/PCI/Credential)
```

---

## 2. Table Definitions

### 2.1 MEMBER — Member Accounts

| Column | Type | Nullable | PII/PCI | Description |
|:-------|:-----|:---------|:--------|:------------|
| `CUSTOMER_NO` | VARCHAR(10) | NOT NULL | Identifier | Primary key, sequence-generated |
| `KANJI_FAMILY_NAME` | VARCHAR(10) | NOT NULL | **PII** | Family name (Kanji) |
| `KANJI_GIVEN_NAME` | VARCHAR(10) | NOT NULL | **PII** | Given name (Kanji) |
| `KANA_FAMILY_NAME` | VARCHAR(10) | NOT NULL | **PII** | Family name (Katakana) |
| `KANA_GIVEN_NAME` | VARCHAR(10) | NOT NULL | **PII** | Given name (Katakana) |
| `BIRTHDAY` | DATE | NOT NULL | **PII** | Date of birth |
| `GENDER` | VARCHAR(1) | NOT NULL | **PII** | M or F |
| `TEL` | VARCHAR(13) | NOT NULL | **PII** | Phone number |
| `ZIP_CODE` | VARCHAR(7) | NOT NULL | **PII** | Postal code |
| `ADDRESS` | VARCHAR(60) | NOT NULL | **PII** | Street address |
| `MAIL` | VARCHAR(256) | NOT NULL | **PII** | Email address |
| `CREDIT_NO` | VARCHAR(16) | NOT NULL | **PCI CHD** | Credit card number |
| `CREDIT_TYPE_CD` | VARCHAR(3) | NOT NULL | — | FK → CREDIT_TYPE |
| `CREDIT_TERM` | VARCHAR(5) | NOT NULL | **PCI CHD** | Card expiry (MM/YY) |

### 2.2 MEMBER_LOGIN — Authentication Credentials

| Column | Type | Nullable | Sensitivity | Description |
|:-------|:-----|:---------|:-----------|:------------|
| `CUSTOMER_NO` | VARCHAR(10) | NOT NULL | Identifier | PK + FK → MEMBER |
| `PASSWORD` | VARCHAR(124) | NOT NULL | **Credential** | Hashed password (PBKDF2/BCrypt) |
| `LAST_PASSWORD` | VARCHAR(124) | Nullable | **Credential** | Previous password hash |
| `LOGIN_DATE_TIME` | TIMESTAMP | Nullable | — | Last login timestamp |
| `LOGIN_FLG` | BOOLEAN | NOT NULL | — | Currently logged in flag |

### 2.3 RESERVATION — Booking Records

| Column | Type | Nullable | PII | Description |
|:-------|:-----|:---------|:----|:------------|
| `RESERVE_NO` | VARCHAR(10) | NOT NULL | — | Primary key |
| `RESERVE_DATE` | DATE | NOT NULL | — | Booking date |
| `TOTAL_FARE` | INT | NOT NULL | — | Total cost |
| `REP_FAMILY_NAME` | VARCHAR(10) | NOT NULL | **PII** | Representative family name |
| `REP_GIVEN_NAME` | VARCHAR(10) | NOT NULL | **PII** | Representative given name |
| `REP_AGE` | INT | NOT NULL | **PII** | Representative age |
| `REP_GENDER` | VARCHAR(1) | NOT NULL | **PII** | Representative gender |
| `REP_TEL` | VARCHAR(13) | NOT NULL | **PII** | Representative phone |
| `REP_MAIL` | VARCHAR(256) | NOT NULL | **PII** | Representative email |
| `REP_CUSTOMER_NO` | VARCHAR(10) | Nullable | — | FK → MEMBER (if member) |

### 2.4 PASSENGER — Passenger Records

| Column | Type | Nullable | PII | Description |
|:-------|:-----|:---------|:----|:------------|
| `PASSENGER_NO` | INT | NOT NULL | — | Primary key |
| `RESERVE_FLIGHT_NO` | INT | NOT NULL | — | FK → RESERVE_FLIGHT |
| `FAMILY_NAME` | VARCHAR(10) | NOT NULL | **PII** | Passenger family name |
| `GIVEN_NAME` | VARCHAR(10) | NOT NULL | **PII** | Passenger given name |
| `AGE` | INT | NOT NULL | **PII** | Passenger age |
| `GENDER` | VARCHAR(1) | NOT NULL | **PII** | Passenger gender |
| `CUSTOMER_NO` | VARCHAR(10) | Nullable | — | FK → MEMBER (if member) |

### 2.5 FLIGHT — Flight Availability

| Column | Type | Nullable | Description |
|:-------|:-----|:---------|:------------|
| `DEPARTURE_DATE` | DATE | NOT NULL | PK component |
| `FLIGHT_NAME` | VARCHAR(6) | NOT NULL | PK + FK → FLIGHT_MASTER |
| `BOARDING_CLASS_CD` | VARCHAR(1) | NOT NULL | PK + FK → BOARDING_CLASS |
| `FARE_TYPE_CD` | VARCHAR(4) | NOT NULL | PK + FK → FARE_TYPE |
| `VACANT_NUM` | INT | NOT NULL | Available seats |

### 2.6 Reference Tables

**AIRPORT**

| Column | Type | Description |
|:-------|:-----|:------------|
| `AIRPORT_CD` | VARCHAR(3) | Airport code (PK) |
| `AIRPORT_NAME` | VARCHAR(15) | Display name |
| `DISPLAY_ORDER` | INT | UI ordering (UNIQUE) |

**ROUTE** — `ROUTE_NO` (PK), `DEP_AIRPORT_CD` FK, `ARR_AIRPORT_CD` FK, `FLIGHT_TIME`, `BASIC_FARE`

**FLIGHT_MASTER** — `FLIGHT_NAME` (PK), `ROUTE_NO` FK, `DEPARTURE_TIME`, `ARRIVAL_TIME`, `CRAFT_TYPE` FK

**PLANE** — `CRAFT_TYPE` (PK), `N_SEAT_NUM`, `S_SEAT_NUM`

**BOARDING_CLASS** — `BOARDING_CLASS_CD` (PK), `BOARDING_CLASS_NAME`, `EXTRA_CHARGE`, `DISPLAY_ORDER`

**FARE_TYPE** — `FARE_TYPE_CD` (PK), `FARE_TYPE_NAME`, `DISCOUNT_RATE`, `RSRV_AVAILABLE_START_DAY_NUM`, `RSRV_AVAILABLE_END_DAY_NUM`, `PASSENGER_MIN_NUM`, `DISPLAY_ORDER`

**CREDIT_TYPE** — `CREDIT_TYPE_CD` (PK), `CREDIT_FIRM`, `DISPLAY_ORDER`

**PEAK_TIME** — Composite PK (`PEAK_TIME_CD`, `PEAK_START_DATE`, `PEAK_END_DATE`), `MULTIPLICATION_RATIO`

---

## 3. Sequences

| Sequence | Used By | Range |
|:---------|:--------|:------|
| `SQ_MEMBER_1` | MEMBER.CUSTOMER_NO | 1 — 9,999,999,999 (CYCLE) |
| `SQ_RESERVATION_1` | RESERVATION.RESERVE_NO | 1 — 9,999,999,999 (CYCLE) |
| `SQ_RESERVE_FLIGHT_1` | RESERVE_FLIGHT.RESERVE_FLIGHT_NO | 1 — 999,999,999,999 (CYCLE) |
| `SQ_PASSENGER_1` | PASSENGER.PASSENGER_NO | 1 — 9,999,999,999,999 (CYCLE) |

---

## 4. Foreign Key Relationships

| Source Table | Source Column(s) | Target Table | Target Column(s) |
|:-------------|:----------------|:-------------|:-----------------|
| MEMBER_LOGIN | CUSTOMER_NO | MEMBER | CUSTOMER_NO |
| MEMBER | CREDIT_TYPE_CD | CREDIT_TYPE | CREDIT_TYPE_CD |
| FLIGHT_MASTER | ROUTE_NO | ROUTE | ROUTE_NO |
| FLIGHT_MASTER | CRAFT_TYPE | PLANE | CRAFT_TYPE |
| FLIGHT | FLIGHT_NAME | FLIGHT_MASTER | FLIGHT_NAME |
| FLIGHT | BOARDING_CLASS_CD | BOARDING_CLASS | BOARDING_CLASS_CD |
| FLIGHT | FARE_TYPE_CD | FARE_TYPE | FARE_TYPE_CD |
| RESERVE_FLIGHT | RESERVE_NO | RESERVATION | RESERVE_NO |
| RESERVE_FLIGHT | (DEP_DATE,FLT,BC,FT) | FLIGHT | (Composite PK) |
| RESERVATION | REP_CUSTOMER_NO | MEMBER | CUSTOMER_NO |
| ROUTE | DEP_AIRPORT_CD | AIRPORT | AIRPORT_CD |
| ROUTE | ARR_AIRPORT_CD | AIRPORT | AIRPORT_CD |
| PASSENGER | RESERVE_FLIGHT_NO | RESERVE_FLIGHT | RESERVE_FLIGHT_NO |
| PASSENGER | CUSTOMER_NO | MEMBER | CUSTOMER_NO |

---

## 5. Indexes

| Index | Table | Column(s) | Type |
|:------|:------|:----------|:-----|
| PK_* | All tables | Primary key columns | B-tree (Primary) |
| UK_ROUTE_1 | ROUTE | (DEP_AIRPORT_CD, ARR_AIRPORT_CD) | Unique |
| IX_ROUTE_1 | ROUTE | DEP_AIRPORT_CD | B-tree |
| UK_*_DISPLAY_ORDER | Multiple | DISPLAY_ORDER | Unique |

---

## 6. Security Considerations

### 6.1 Columns Requiring Encryption at Rest

| Table | Column | Data Type | FedRAMP Requirement |
|:------|:-------|:----------|:-------------------|
| MEMBER | CREDIT_NO | VARCHAR(16) | **Must encrypt** (PCI DSS) |
| MEMBER | CREDIT_TERM | VARCHAR(5) | **Must encrypt** (PCI DSS) |
| MEMBER_LOGIN | PASSWORD | VARCHAR(124) | Hashed (already protected) |
| MEMBER_LOGIN | LAST_PASSWORD | VARCHAR(124) | Hashed (already protected) |

### 6.2 Database Access Control

| Role | Permissions | Tables |
|:-----|:-----------|:-------|
| `atrs_svc` (application) | SELECT, INSERT, UPDATE | All tables |
| `atrs_readonly` (reporting) | SELECT only | Non-sensitive tables |
| `atrs_dba` (administration) | ALL | All tables (restricted personnel) |

### 6.3 Audit Recommendations

- Enable PostgreSQL `pgaudit` extension for FedRAMP compliance
- Log all DDL operations
- Log all DML on `MEMBER`, `MEMBER_LOGIN`, `RESERVATION`, `PASSENGER`
- Forward database audit logs to SIEM
