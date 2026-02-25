# ATRS — FedRAMP System Security Plan (SSP)

**Document ID:** ATRS-SSP-001  
**Information System Name:** Airline Ticket Reservation System (ATRS)  
**FIPS 199 Categorization:** Moderate  
**FedRAMP Authorization Level:** Moderate  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Information System Description

### 1.1 System Function & Purpose

The Airline Ticket Reservation System (ATRS) is a web-based application that enables users to search for airline flights, make ticket reservations, manage member accounts, and generate reservation history reports. The system processes Personally Identifiable Information (PII) including names, contact details, and payment card data.

### 1.2 Information Types Processed

| Information Type | NIST SP 800-60 Category | Confidentiality | Integrity | Availability |
|:-----------------|:----------------------|:----------------|:----------|:-------------|
| Member PII (name, address, phone, email) | C.2.8.12 — General Information | Moderate | Moderate | Moderate |
| Payment Card Information (credit card number, type, expiry) | D.26.1 — Financial Management | Moderate | Moderate | Low |
| Authentication Credentials (passwords) | D.16.1 — Security Management | High | High | Moderate |
| Flight & Reservation Records | D.18.1 — Transportation | Low | Moderate | Moderate |

### 1.3 FIPS 199 Security Categorization

**Overall Categorization: MODERATE**

| Security Objective | Level | Rationale |
|:-------------------|:------|:----------|
| Confidentiality | Moderate | PII and payment card data require protection |
| Integrity | Moderate | Reservation and financial data must be accurate |
| Availability | Moderate | System supports operational business functions |

---

## 2. System Environment

### 2.1 Hardware Inventory

| Component | Description | Quantity | Location |
|:----------|:------------|:---------|:---------|
| Application Server | Tomcat 10.x on Linux | 2+ (HA) | Data Center / Cloud |
| Database Server | PostgreSQL 14+ on Linux | 2 (Primary/Replica) | Data Center / Cloud |
| Message Broker | Apache Artemis on Linux | 2 (HA Pair) | Data Center / Cloud |
| Load Balancer | TLS-terminating LB | 1+ | Network Edge |
| WAF | Web Application Firewall | 1 | DMZ |

### 2.2 Software Inventory

| Software | Version | Purpose | Patch Responsibility |
|:---------|:--------|:--------|:--------------------|
| Java JDK | 17 or 21 (LTS) | Application Runtime | Platform Team |
| Apache Tomcat | 10.x | Servlet Container | Platform Team |
| PostgreSQL | 14+ | Relational Database | DBA Team |
| Apache Artemis | Latest Stable | JMS Message Broker | Platform Team |
| TERASOLUNA GFW | 5.10.0.RELEASE | Application Framework | Application Team |
| Spring Security | 6.x | Auth & Access Control | Application Team |
| Logback | Managed by parent | Logging Framework | Application Team |

### 2.3 Network Architecture

| Zone | Components | Protection |
|:-----|:-----------|:-----------|
| **DMZ** | WAF, Load Balancer | DDoS protection, TLS termination, IP allowlisting |
| **Application Tier** | Tomcat instances | Security groups, no direct internet access |
| **Data Tier** | PostgreSQL, Artemis | Private subnet, encrypted connections |
| **Management** | SSH bastion, SIEM | MFA-required access, audit logging |

---

## 3. Security Control Implementation

### 3.1 ACCESS CONTROL (AC)

#### AC-1: Access Control Policy and Procedures
ATRS implements a role-based access control (RBAC) model enforced through Spring Security. Access control policies are defined in `spring-security.xml` (XML variant) or `SecurityConfig.java` (Java variant) and reviewed annually.

#### AC-2: Account Management
- Member accounts created via self-registration (`MemberRegisterService`)
- Account data stored in `MEMBER` and `MEMBER_LOGIN` tables
- Login state tracked via `LOGIN_FLG` and `LOGIN_DATE_TIME`
- Administrative account management procedures documented in operational runbooks

#### AC-3: Access Enforcement
Spring Security `<sec:intercept-url>` rules enforce access control:
- `/member/update` — requires `ROLE_MEMBER`
- `/HistoryReport/**` — requires `ROLE_MEMBER`
- `/api/v1/**` — HTTP Basic authentication
- `/**` — public access (search, home page)

#### AC-4: Information Flow Enforcement
- Web tier → Service tier → Repository tier (unidirectional flow)
- JMS messaging for asynchronous operations (report generation)
- Database connections pooled and managed centrally

#### AC-7: Unsuccessful Logon Attempts
- Authentication failures handled by `AtrsAuthenticationFailureHandler`
- Failed login attempts logged with user ID via MDC
- Account lockout policies configurable at the application level

#### AC-8: System Use Notification
Login page displays system use notification banner before authentication.

#### AC-11: Session Lock / AC-12: Session Termination
- HTTP sessions with configurable timeout
- Explicit logout via `/auth/dologout` with session invalidation
- JSESSIONID cookie deleted on logout

#### AC-17: Remote Access
All remote access requires TLS encryption. Administrative access requires MFA via bastion hosts.

### 3.2 AUDIT AND ACCOUNTABILITY (AU)

#### AU-2: Audit Events
ATRS logs the following auditable events:
- Authentication success/failure (`AtrsAuthenticationSuccessHandler`, `AtrsAuthenticationFailureHandler`)
- Logout events (`AtrsLogoutSuccessHandler`)
- Access log entries (`AccessLogFilter`)
- Business exceptions (`ExceptionLogger`)
- Repository-level data access (trace-level logging)

#### AU-3: Content of Audit Records
Log format includes: `date | thread | user | X-Track | level | logger | message`
- Timestamp: ISO 8601 (`yyyy-MM-dd HH:mm:ss`)
- User ID: Via `UserIdMDCPutFilter` (Spring Security integration)
- Tracking: `X-Track` header for request correlation

#### AU-4: Audit Storage Capacity
- Application logs: `atrs-application.log` with 7-day rolling retention
- Monitoring logs: `atrs-monitoring.log` with 7-day rolling retention
- Production: Forward to centralized SIEM for long-term retention (90+ days)

#### AU-6: Audit Review, Analysis, and Reporting
- Monitoring log captures ERROR-level events from `ExceptionLogger.Monitoring`
- Integration with SIEM for automated alerting and correlation
- Weekly manual review of security-relevant events

### 3.3 IDENTIFICATION AND AUTHENTICATION (IA)

#### IA-2: Identification and Authentication (Organizational Users)
- Member authentication via membership number + password
- `AtrsUserDetailsService` loads credentials from `MEMBER_LOGIN` table
- Multi-factor authentication required for administrative access (infrastructure level)

#### IA-5: Authenticator Management
- Password encoding: PBKDF2 with 310,000 iterations (SHA-256) — Spring Security 5.8 defaults
- BCrypt supported as legacy fallback
- `DelegatingPasswordEncoder` manages algorithm migration
- Last password stored for password history enforcement

#### IA-6: Authenticator Feedback
Password fields obscured in UI. Error messages do not reveal which credential element failed.

### 3.4 CONFIGURATION MANAGEMENT (CM)

#### CM-2: Baseline Configuration
- Application version: 1.11.0.RELEASE
- Framework: TERASOLUNA GFW 5.10.0.RELEASE
- All dependency versions locked via Maven `<dependencyManagement>`
- Database schema versioned via SQL migration scripts

#### CM-6: Configuration Settings
| Parameter | Default | Security Implication |
|:----------|:--------|:--------------------|
| `database.url` | `jdbc:postgresql://localhost:5432/atrs` | Must use TLS in production |
| `database.username` | `postgres` | Must use dedicated service account |
| `database.password` | `postgres` | Must use secrets management |
| `cp.maxActive` | 96 | Connection pool DoS protection |
| `jms.mq.host` | `localhost` | Must be internal network only |

#### CM-7: Least Functionality
- Static resources served without security context (`security="none"`)
- API endpoints isolated with stateless session management
- CSRF disabled only on stateless API endpoints
- Unused services and ports should be disabled in production

### 3.5 SYSTEM AND COMMUNICATIONS PROTECTION (SC)

#### SC-8: Transmission Confidentiality and Integrity
- TLS 1.2+ required for all browser-to-server communication
- Database connections should use `sslmode=verify-full`
- JMS broker connections should use TLS

#### SC-12: Cryptographic Key Establishment and Management
- PBKDF2 key derivation for password storage
- TLS certificates managed via organizational PKI
- Java Cryptography Architecture (JCA) provides FIPS-capable providers

#### SC-13: Cryptographic Protection
- Password hashing: PBKDF2 (310,000 iterations, SHA-256)
- Transport encryption: TLS 1.2/1.3
- FIPS 140-2 compliance achievable via JCE FIPS provider configuration

#### SC-23: Session Authenticity
- CSRF token protection on all form submissions
- `InvalidCsrfTokenException` redirects to dedicated error page
- Session fixation protection via Spring Security defaults

#### SC-28: Protection of Information at Rest
- Database encryption: PostgreSQL TDE or filesystem-level encryption
- Report files: Encrypted storage volume
- Credential storage: One-way hash (PBKDF2/BCrypt)

### 3.6 SYSTEM AND INFORMATION INTEGRITY (SI)

#### SI-2: Flaw Remediation
- Dependency vulnerability scanning via Maven plugins (OWASP Dependency-Check)
- Framework updates tracked against TERASOLUNA release schedule
- PostgreSQL driver and runtime patched per vendor advisories

#### SI-3: Malicious Code Protection
- Input validation via Bean Validation (JSR 380) annotations
- Custom validators for all user input forms
- MyBatis parameterized queries prevent SQL injection
- View-layer output encoding prevents XSS

#### SI-10: Information Input Validation
All user input validated through multiple layers:

| Validator | Scope | Validation |
|:----------|:------|:-----------|
| `TicketSearchValidator` | Flight search | Date ranges, airport codes |
| `TicketReserveValidator` | Reservations | Passenger data, flight selection |
| `MemberRegisterValidator` | Registration | All member fields, credit card |
| `MemberUpdateValidator` | Profile updates | Changed field validation |
| `ReservationFlightValidator` | Flight selection | Flight availability, class |
| Bean Validation annotations | All forms | @NotNull, @Size, @Pattern, custom |

Custom validation annotations:
- `@FixedLength` — Exact character length
- `@FullWidth` / `@FullWidthKatakana` — Character set validation
- `@HalfWidth` / `@HalfWidthNumber` — Alphanumeric validation

### 3.7 CONTINGENCY PLANNING (CP)

#### CP-9: Information System Backup
- Database: PostgreSQL WAL archiving + periodic full backups
- Application: WAR artifacts stored in artifact repository
- Configuration: Version-controlled in Git
- Reports: Backed up from `/atrs/reports/reservation`

#### CP-10: Information System Recovery and Reconstitution
- RTO: Defined per organizational SLA
- RPO: Defined per database backup frequency
- Recovery procedures documented in operational runbooks

### 3.8 INCIDENT RESPONSE (IR)

#### IR-4: Incident Handling
- `ExceptionLogger.Monitoring` captures all ERROR-level events
- SIEM integration for real-time alerting
- Incident response procedures per organizational IR plan
- See [Incident Response Plan](INCIDENT_RESPONSE.md)

### 3.9 RISK ASSESSMENT (RA)

#### RA-5: Vulnerability Scanning
- Static Application Security Testing (SAST) in CI/CD pipeline
- Dynamic Application Security Testing (DAST) in staging environment
- Dependency vulnerability scanning (OWASP Dependency-Check, Snyk)
- Infrastructure vulnerability scanning (Nessus, Qualys)

---

## 4. Interconnections

| External System | Direction | Data | Protocol | Authorization |
|:----------------|:----------|:-----|:---------|:-------------|
| User Browser | Inbound | HTTP requests/responses | HTTPS (TLS 1.2+) | Form-based / HTTP Basic |
| PostgreSQL | Bidirectional | SQL queries/results | JDBC over TLS | Username/password |
| Apache Artemis | Bidirectional | JMS messages | AMQP/OpenWire over TLS | Broker credentials |
| SIEM | Outbound | Log data | Syslog/HTTPS | API key |
| NTP Server | Outbound | Time sync | NTP | N/A |

---

## 5. Continuous Monitoring Strategy

| Activity | Frequency | Responsible Party |
|:---------|:----------|:------------------|
| Vulnerability scanning | Monthly | Security Team |
| Penetration testing | Annual | Third-party assessor |
| Configuration audit | Quarterly | Operations Team |
| Access review | Quarterly | Security Team |
| Log review | Weekly (automated daily) | SOC |
| Patch assessment | Monthly | Platform Team |
| SBOM review | Quarterly | Application Team |
| Incident response drill | Annual | IR Team |

---

## 6. Plan of Action and Milestones (POA&M)

| ID | Finding | Risk Level | Remediation | Target Date | Status |
|:---|:--------|:-----------|:------------|:------------|:-------|
| POA-001 | Hardcoded DB credentials in properties files | High | Migrate to secrets management (Vault/AWS SM) | TBD | Open |
| POA-002 | No TLS configured for local database connection | High | Enable `sslmode=verify-full` in production | TBD | Open |
| POA-003 | REST API uses HTTP Basic without rate limiting | Medium | Implement API rate limiting and OAuth 2.0 | TBD | Open |
| POA-004 | Multiple configuration variants increase attack surface | Medium | Standardize on single variant for production | TBD | Open |
| POA-005 | No automated SBOM generation in CI/CD | Low | Integrate CycloneDX Maven plugin | TBD | Open |
| POA-006 | Log retention only 7 days locally | Medium | Forward to SIEM with 90+ day retention | TBD | Open |
| POA-007 | Missing account lockout after failed attempts | High | Implement progressive lockout in AuthLoginService | TBD | Open |
| POA-008 | JMS broker credentials not externalized | Medium | Move to secrets management | TBD | Open |

---

## 7. Approvals

| Role | Name | Signature | Date |
|:-----|:-----|:----------|:-----|
| System Owner | | | |
| Information System Security Officer (ISSO) | | | |
| Authorizing Official (AO) | | | |

---

*This document is a template aligned with FedRAMP Moderate baseline requirements. All [TBD] items must be completed with organization-specific details prior to authorization package submission.*
