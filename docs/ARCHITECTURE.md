# ATRS — System Architecture & Design Document

**Document ID:** ATRS-ARCH-001  
**Classification:** Controlled Unclassified Information (CUI)  
**FedRAMP Control Mapping:** SA-4, SA-5, CM-6, PL-2, PL-8  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. System Overview

The **Airline Ticket Reservation System (ATRS)** is a Java-based enterprise web application that enables airline ticket searching, booking, member registration, and reservation history management. It is built on the **TERASOLUNA Server Framework for Java (5.x)**, a customized framework based on the Macchinetta platform by NTT DATA.

### 1.1 System Purpose

ATRS provides the following core capabilities:

| Capability | Module ID | Description |
|:-----------|:----------|:------------|
| Authentication & Authorization | A0, A1, A2 | Member login/logout with role-based access |
| Flight Search | B1 | Search for available flights by route, date, and class |
| Ticket Reservation | B2 | Book flights with passenger and payment details |
| Member Registration | C1 | New member account creation with credit card enrollment |
| Member Profile Management | C2 | Update member personal and payment information |
| Reservation History Reporting | D1 | Generate and download reservation history (async via JMS) |

### 1.2 System Boundary

```
┌───────────────────────── ATRS Authorization Boundary ──────────────────────────┐
│                                                                                 │
│  ┌────────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │  Web Browser    │───▶│  Tomcat 10.x     │───▶│  PostgreSQL 14+             │ │
│  │  (End User)     │    │  (App Server)    │    │  (Database)                 │ │
│  └────────────────┘    │                  │    └─────────────────────────────┘ │
│                         │  ┌─────────────┐│    ┌─────────────────────────────┐ │
│                         │  │ Spring MVC   ││    │  Apache Artemis              │ │
│                         │  │ Spring Sec   ││───▶│  (JMS Message Broker)       │ │
│                         │  │ MyBatis      ││    └─────────────────────────────┘ │
│                         │  └─────────────┘│    ┌─────────────────────────────┐ │
│                         └──────────────────┘    │  File System                 │ │
│                                                  │  (/atrs/reports/reservation)│ │
│                                                  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architectural Variants

ATRS ships in four configuration variants to demonstrate framework flexibility:

| Variant | Configuration Style | View Technology | Directory |
|:--------|:-------------------|:----------------|:----------|
| **XMLConfig-JSP** | Spring XML | JSP/JSTL | `XMLConfig-JSP/` |
| **XMLConfig-Thymeleaf** | Spring XML | Thymeleaf | `XMLConfig-Thymeleaf/` |
| **JavaConfig-JSP** | Java `@Configuration` | JSP/JSTL | `JavaConfig-JSP/` |
| **JavaConfig-Thymeleaf** | Java `@Configuration` | Thymeleaf | `JavaConfig-Thymeleaf/` |

> **FedRAMP Note:** For production deployments seeking FedRAMP authorization, a **single variant** must be selected and locked via CM baseline (see [Configuration Management](fedramp/CONFIGURATION_MANAGEMENT.md)).

---

## 3. Layered Architecture

### 3.1 Module Structure

Each variant consists of four Maven modules:

```
atrs (Parent POM)
├── atrs-web         # Presentation layer — WAR packaging
│   ├── Controllers  (app/a0, a1, b0, b1, b2, c0, c1, c2, d1)
│   ├── REST API     (api/flight, api/ticket)
│   ├── Forms        (Input validation via Bean Validation)
│   ├── Views        (JSP or Thymeleaf templates)
│   └── Security     (Authentication filters & handlers)
│
├── atrs-domain      # Business logic & data access — JAR packaging
│   ├── Models       (Airport, Flight, Member, Reservation, etc.)
│   ├── Services     (TicketSearch, TicketReserve, MemberRegister, etc.)
│   ├── Repositories (MyBatis mappers for all entities)
│   └── Common       (Codelist, Validation, Utilities)
│
├── atrs-env         # Environment configuration — JAR packaging
│   ├── DataSource   (JDBC connection pool)
│   ├── JMS          (Artemis connection factory)
│   └── Logging      (Logback configuration)
│
└── atrs-initdb      # Database initialization — POM packaging
    └── SQL scripts  (DDL + DML for PostgreSQL)
```

### 3.2 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        atrs-web                              │
│                                                              │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │ Controllers   │  │ REST APIs     │  │ Security Filters │ │
│  │ (MVC)         │  │ (api/v1/*)    │  │ (Spring Sec)     │ │
│  └──────┬───────┘  └──────┬────────┘  └────────┬─────────┘ │
│         │                  │                     │           │
│  ┌──────▼──────────────────▼─────────────────────▼─────────┐ │
│  │            Service Layer (atrs-domain)                    │ │
│  │  ┌────────────┐ ┌──────────────┐ ┌────────────────────┐ │ │
│  │  │TicketSearch│ │TicketReserve │ │ MemberRegister     │ │ │
│  │  │Service     │ │Service       │ │ /UpdateService     │ │ │
│  │  └─────┬──────┘ └──────┬───────┘ └────────┬───────────┘ │ │
│  │        │                │                   │             │ │
│  │  ┌─────▼────────────────▼───────────────────▼───────────┐│ │
│  │  │            Repository Layer (MyBatis)                 ││ │
│  │  │ FlightRepo │ ReservationRepo │ MemberRepo │ RouteRepo││ │
│  │  └──────────────────────┬────────────────────────────────┘│ │
│  └─────────────────────────┼─────────────────────────────────┘ │
└────────────────────────────┼───────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  PostgreSQL DB  │
                    │  (atrs schema)  │
                    └─────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Version | FedRAMP Relevance |
|:------|:-----------|:--------|:------------------|
| **Runtime** | Java (JDK) | 17 or 21 | FIPS 140-2 crypto providers available |
| **Framework** | TERASOLUNA GFW Parent | 5.10.0.RELEASE | Built on Spring Framework 6.x |
| **Web Container** | Apache Tomcat | 10.x | Jakarta Servlet 6.0 |
| **Persistence** | MyBatis | (managed by parent) | Parameterized queries prevent SQLi |
| **Database** | PostgreSQL | 14+ (Driver 42.7.4) | Supports TLS, row-level security |
| **Messaging** | Apache Artemis | (managed by parent) | JMS 3.0 (Jakarta Messaging) |
| **Object Mapping** | MapStruct | (managed by parent) | Compile-time code generation |
| **Security** | Spring Security | 6.x | CSRF, session fixation, auth framework |
| **Logging** | Logback + SLF4J | (managed by parent) | Structured audit logging support |
| **Build** | Apache Maven | 3.x | Reproducible builds, SBOM generation |

---

## 5. Data Flow Diagrams

### 5.1 Flight Search (DFD-L1)

```
  ┌──────────┐    Search Criteria     ┌───────────────────┐
  │  User     │ ──────────────────▶   │ TicketSearch       │
  │ (Browser) │                        │ Controller (B1)    │
  │           │ ◀────────────────────  │                    │
  └──────────┘    Flight Results       └─────────┬─────────┘
                                                  │
                                        ┌─────────▼─────────┐
                                        │ TicketSearch       │
                                        │ Service            │
                                        └─────────┬─────────┘
                                                  │
                                        ┌─────────▼─────────┐
                                        │ FlightRepository   │ ──▶ PostgreSQL
                                        └───────────────────┘
```

### 5.2 Ticket Reservation (DFD-L1)

```
  ┌──────────┐   Passenger + Flight   ┌───────────────────┐
  │  User     │ ──────────────────▶   │ TicketReserve      │
  │ (Auth'd)  │                        │ Controller (B2)    │
  │           │ ◀────────────────────  │                    │
  └──────────┘   Reservation No.       └─────────┬─────────┘
                                                  │
                                        ┌─────────▼─────────┐
                                        │ TicketReserve      │
                                        │ Service            │
                                        └──┬─────────────┬──┘
                                           │             │
                                 ┌─────────▼──┐  ┌──────▼────────┐
                                 │Reservation  │  │ Flight         │
                                 │Repository   │  │ Repository     │
                                 └─────────────┘  └───────────────┘
                                           │             │
                                        PostgreSQL DB (Transactional)
```

### 5.3 Authentication Flow

```
  ┌──────────┐   membershipNumber    ┌───────────────────────────┐
  │  User     │ ─────────────────▶  │ AtrsUsernamePassword       │
  │ (Browser) │   + password         │ AuthenticationFilter       │
  └──────────┘                       └────────────┬──────────────┘
                                                  │
                                     ┌────────────▼──────────────┐
                                     │ AuthenticationManager      │
                                     │ (Spring Security)          │
                                     └────────────┬──────────────┘
                                                  │
                                     ┌────────────▼──────────────┐
                                     │ AtrsUserDetailsService     │
                                     │ (loads from MEMBER_LOGIN)  │
                                     └────────────┬──────────────┘
                                                  │
                                     ┌────────────▼──────────────┐
                                     │ Pbkdf2PasswordEncoder      │
                                     │ (password verification)    │
                                     └───────────────────────────┘
```

---

## 6. Security Architecture

### 6.1 Authentication

- **Mechanism:** Form-based login via custom `AtrsUsernamePasswordAuthenticationFilter`
- **Credential Storage:** Pbkdf2 (default) with BCrypt fallback via `DelegatingPasswordEncoder`
- **Session Management:** HTTP session with JSESSIONID cookie; invalidated on logout
- **API Authentication:** HTTP Basic for REST API endpoints (`/api/v1/**`)

### 6.2 Authorization

| URL Pattern | Required Role | Description |
|:------------|:-------------|:------------|
| `/resources/**` | None (public) | Static assets |
| `/api/v1/**` | permitAll | REST API (HTTP Basic) |
| `/member/update` | ROLE_MEMBER | Profile updates |
| `/HistoryReport/**` | ROLE_MEMBER | Report downloads |
| `/**` | permitAll | Public pages |

### 6.3 CSRF Protection

- CSRF tokens enforced on all non-API form submissions
- API endpoints (`/api/v1/**`) exempt with stateless sessions
- Invalid CSRF tokens redirect to dedicated error page

### 6.4 Password Policy

- Encoder: PBKDF2 with Spring Security 5.8 defaults (310,000 iterations, SHA-256)
- Fallback: BCrypt for legacy password hashes
- Last password tracked in `MEMBER_LOGIN.LAST_PASSWORD` column

---

## 7. External Interfaces

### 7.1 Database Interface

| Property | Value |
|:---------|:------|
| DBMS | PostgreSQL 14+ |
| JDBC URL | `jdbc:postgresql://<host>:5432/atrs` |
| Driver | `org.postgresql.Driver` (42.7.4) |
| Connection Pool | Max Active: 96, Max Idle: 16, Max Wait: 60s |

### 7.2 JMS Interface

| Property | Value |
|:---------|:------|
| Broker | Apache Artemis |
| Host | Configurable (`jms.mq.host`) |
| Port | 61616 (default) |
| Use Case | Asynchronous reservation history report generation |

### 7.3 File System Interface

| Property | Value |
|:---------|:------|
| Report Path | `/atrs/reports/reservation` |
| Use Case | Generated reservation history PDF/CSV files |

---

## 8. Deployment Architecture

### 8.1 Single-Node Deployment (Development)

```
┌──────────────────────────────────────────┐
│  Host Machine                             │
│  ┌──────────────────────────────────────┐│
│  │  Tomcat 10.x                         ││
│  │  ┌─────────────────────────────────┐ ││
│  │  │  atrs.war                        │ ││
│  │  │  (Web App + Domain + Env)        │ ││
│  │  └─────────────────────────────────┘ ││
│  └──────────────────────────────────────┘│
│  ┌───────────────┐  ┌──────────────────┐ │
│  │ PostgreSQL    │  │ Apache Artemis   │ │
│  │ (Port 5432)   │  │ (Port 61616)     │ │
│  └───────────────┘  └──────────────────┘ │
└──────────────────────────────────────────┘
```

### 8.2 FedRAMP-Compliant Production Deployment

```
┌──────────────────── VPC / Private Cloud ────────────────────────┐
│                                                                   │
│  ┌───────────┐     ┌──────────────────┐     ┌────────────────┐  │
│  │  WAF /     │────▶│  Load Balancer   │────▶│ App Server     │  │
│  │  CDN       │     │  (TLS Term.)     │     │ Cluster        │  │
│  └───────────┘     └──────────────────┘     │ (Tomcat ×N)    │  │
│                                               └───────┬────────┘  │
│                                                       │           │
│  ┌───────────────────────┐    ┌───────────────────────┤           │
│  │  SIEM / Log           │    │                       │           │
│  │  Aggregator           │    │  ┌────────────────────▼────────┐ │
│  └───────────────────────┘    │  │ PostgreSQL HA              │  │
│                                │  │ (Primary + Replica)        │  │
│                                │  └────────────────────────────┘  │
│                                │  ┌────────────────────────────┐  │
│                                │  │ Apache Artemis Cluster     │  │
│                                │  └────────────────────────────┘  │
│                                │  ┌────────────────────────────┐  │
│                                └──│ Encrypted Storage (Reports)│  │
│                                   └────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

---

## 9. Component Inventory (SBOM Summary)

| Component | Group ID | Version | License |
|:----------|:---------|:--------|:--------|
| TERASOLUNA GFW Parent | org.terasoluna.gfw | 5.10.0.RELEASE | Apache 2.0 |
| PostgreSQL JDBC Driver | org.postgresql | 42.7.4 | BSD-2 |
| MapStruct | org.mapstruct | (managed) | Apache 2.0 |
| Spring Security | org.springframework.security | 6.x (managed) | Apache 2.0 |
| Spring Framework | org.springframework | 6.x (managed) | Apache 2.0 |
| Logback | ch.qos.logback | (managed) | EPL 1.0 / LGPL 2.1 |
| Apache Artemis Client | org.apache.activemq | (managed) | Apache 2.0 |

> Full SBOM should be generated via `mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom` for FedRAMP submissions.

---

## 10. FedRAMP Control Traceability

| Control | Implementation Reference |
|:--------|:------------------------|
| **SA-4** | This document (Section 9 — SBOM) |
| **SA-5** | This document + [API Reference](API_REFERENCE.md) + [Database Schema](DATABASE_SCHEMA.md) |
| **CM-6** | Section 7 (Configuration parameters) |
| **PL-2** | Section 1 (System overview and boundary) |
| **PL-8** | Sections 3–5 (Architecture, components, data flows) |
| **SC-7** | Section 8.2 (Boundary protection in production) |
