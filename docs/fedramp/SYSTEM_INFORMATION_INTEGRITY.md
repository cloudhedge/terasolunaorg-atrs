# ATRS — System and Information Integrity

**Document ID:** ATRS-SI-001  
**FedRAMP Control Family:** System and Information Integrity (SI)  
**NIST SP 800-53 Rev. 5 Controls:** SI-1 through SI-16  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Flaw Remediation (SI-2)

### 1.1 Patch Management Schedule

| Component | Scan Frequency | Patch Window | Responsible |
|:----------|:-------------|:-------------|:------------|
| Java JDK (17/21 LTS) | Monthly | 30 days (critical: 72 hours) | Platform Team |
| Apache Tomcat 10.x | Monthly | 30 days (critical: 72 hours) | Platform Team |
| PostgreSQL 14+ | Monthly | 30 days (critical: 72 hours) | DBA Team |
| TERASOLUNA/Spring Dependencies | Quarterly | 60 days | Application Team |
| PostgreSQL JDBC Driver (42.7.4) | Quarterly | 60 days | Application Team |
| Operating System | Monthly | 30 days (critical: 72 hours) | Infrastructure Team |

### 1.2 Vulnerability Scanning

```bash
# Dependency vulnerability check
mvn org.owasp:dependency-check-maven:check

# Generate SBOM for tracking
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom

# List all dependencies for audit
mvn dependency:tree
```

---

## 2. Malicious Code Protection (SI-3)

### 2.1 Application-Level Protections

| Attack Vector | Protection | Implementation |
|:-------------|:-----------|:---------------|
| SQL Injection | Parameterized queries | MyBatis XML-mapped SQL with `#{}` parameters |
| Cross-Site Scripting (XSS) | Output encoding | JSP: `<c:out>`; Thymeleaf: auto-escaping |
| Cross-Site Request Forgery | CSRF tokens | Spring Security CSRF filter |
| Path Traversal | Input validation | Bean Validation constraints |
| Deserialization | Framework defaults | Spring MVC Jackson configuration |
| File Upload | Not applicable | ATRS does not accept file uploads |

### 2.2 Infrastructure-Level Protections

| Protection | Tool | Scope |
|:-----------|:-----|:------|
| Antivirus/Anti-malware | Host-based AV agent | All servers |
| Web Application Firewall | WAF (ModSecurity/AWS WAF) | All inbound HTTP traffic |
| Intrusion Detection | Network IDS/IPS | Network perimeter |
| File Integrity Monitoring | OSSEC/Tripwire | Application and configuration files |

---

## 3. Information Input Validation (SI-10)

### 3.1 Validation Architecture

```
User Input → [Client Validation] → [Controller Validation] → [Service Validation] → [Repository]
              (Parsley.js)         (Bean Validation +         (Business Rules)      (MyBatis
               Defense-in-depth     Custom Validators)                                Parameterized)
```

### 3.2 Controller-Level Validators

| Validator Class | Module | Validated Data |
|:---------------|:-------|:---------------|
| `TicketSearchValidator` | B1 | Departure/arrival airports, dates, boarding class |
| `FlightSearchCriteriaValidator` | B1 | Search criteria completeness and ranges |
| `TicketReserveValidator` | B2 | Passenger count, flight selection, payment |
| `ReservationFlightValidator` | B0 | Flight availability, class, fare type |
| `MemberRegisterValidator` | C1 | All registration fields, password policy |
| `MemberUpdateValidator` | C2 | Changed fields, password confirmation |
| `MemberValidator` | C0 | Common member field rules |
| `FlightValidator` | API | REST API flight search parameters |
| `TicketReserveValidator` (API) | API | REST API reservation payload |

### 3.3 Bean Validation Annotations

| Annotation | Package | Purpose |
|:-----------|:--------|:--------|
| `@NotNull` / `@NotBlank` | jakarta.validation | Required field enforcement |
| `@Size(min, max)` | jakarta.validation | Length constraints |
| `@Pattern(regexp)` | jakarta.validation | Format enforcement |
| `@FixedLength` | Custom (ATRS) | Exact length validation (e.g., customer number) |
| `@FullWidth` | Custom (ATRS) | Full-width character validation |
| `@FullWidthKatakana` | Custom (ATRS) | Katakana character set validation |
| `@HalfWidth` | Custom (ATRS) | Half-width character validation |
| `@HalfWidthNumber` | Custom (ATRS) | Numeric-only validation |

### 3.4 Database-Level Constraints

| Constraint Type | Tables | Purpose |
|:---------------|:-------|:--------|
| `PRIMARY KEY` | All tables | Entity uniqueness |
| `FOREIGN KEY` | All relationship tables | Referential integrity |
| `NOT NULL` | Most columns | Data completeness |
| `UNIQUE` | ROUTE, display ordering | Prevent duplicates |
| `VARCHAR(n)` | All string columns | Length enforcement |

---

## 4. Error Handling (SI-11)

### 4.1 Exception Mapping

| Exception Type | Error Code | User-Facing Message | Logged Detail |
|:--------------|:-----------|:--------------------|:-------------|
| `BusinessException` | `e.ar.fw.8001` | Business-friendly message | Full exception + stack trace |
| `InvalidFlightException` | Domain-specific | "Invalid flight selection" | Flight details |
| `FlightNotFoundException` | Domain-specific | "No flights found" | Search criteria |
| `BadRequestException` | HTTP 400 | "Invalid request" | Request parameters |
| Unhandled Exception | `e.ar.fw.9999` | Generic error page | Full exception + stack trace |
| `InvalidCsrfTokenException` | HTTP 403 | CSRF error page | Request details |

### 4.2 Error Page Configuration

- Custom error pages configured in `web.xml`
- No stack traces or internal details exposed to users
- Error codes logged for correlation with monitoring
- `ExceptionLogger` captures all exceptions with X-Track correlation

### 4.3 API Error Handling

REST API errors return structured JSON via `ApiGlobalExceptionHandler`:

```json
{
  "code": "e.ar.fw.8001",
  "message": "Business error occurred",
  "details": []
}
```

---

## 5. Information Output Handling (SI-15)

| Output Type | Sanitization | Control |
|:------------|:-------------|:--------|
| HTML views (JSP) | JSTL escaping, CSRF tokens in forms | XSS prevention |
| HTML views (Thymeleaf) | Auto-escaping by default | XSS prevention |
| JSON API responses | Jackson serialization (no HTML) | Data type enforcement |
| Log output | Newline characters escaped in Logback pattern | Log injection prevention |
| Report files | Generated server-side (no user-supplied markup) | Injection prevention |

---

## 6. Software and Information Integrity (SI-7)

| Component | Integrity Control |
|:----------|:-----------------|
| Application WAR | Maven checksum verification, artifact signing |
| Dependencies | Central repository checksums, SBOM tracking |
| Database schema | Versioned SQL scripts in Git |
| Configuration | Version-controlled, change-managed |
| Runtime | File integrity monitoring on production servers |

---

## 7. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| SI-1 | Policy & Procedures | ✅ | This document |
| SI-2 | Flaw Remediation | ✅ | Section 1 |
| SI-3 | Malicious Code Protection | ✅ | Section 2 |
| SI-4 | Information System Monitoring | ✅ | Audit & Accountability doc |
| SI-5 | Security Alerts & Advisories | ✅ | Patch management process |
| SI-7 | Software & Information Integrity | ✅ | Section 6 |
| SI-10 | Information Input Validation | ✅ | Section 3 |
| SI-11 | Error Handling | ✅ | Section 4 |
| SI-16 | Memory Protection | ✅ | JVM managed memory, no native code |
