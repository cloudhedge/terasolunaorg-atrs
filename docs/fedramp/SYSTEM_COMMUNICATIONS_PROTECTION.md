# ATRS — System and Communications Protection

**Document ID:** ATRS-SC-001  
**FedRAMP Control Family:** System and Communications Protection (SC)  
**NIST SP 800-53 Rev. 5 Controls:** SC-1 through SC-44  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Boundary Protection (SC-7)

### 1.1 Network Segmentation

| Zone | Components | Ingress | Egress |
|:-----|:-----------|:--------|:-------|
| **DMZ** | WAF, Load Balancer | HTTPS (443) from internet | HTTPS to App Tier |
| **Application Tier** | Tomcat instances | HTTPS from DMZ only | JDBC to DB, AMQP to Broker |
| **Data Tier** | PostgreSQL, Artemis | JDBC/AMQP from App Tier only | NTP, DNS, SIEM |
| **Management** | Bastion, SIEM, Monitoring | SSH from authorized IPs | All internal |

### 1.2 Denied by Default

All network traffic is denied by default. Only explicitly allowed flows are permitted as documented in the firewall rule set.

---

## 2. Transmission Security (SC-8, SC-13)

### 2.1 TLS Configuration

| Connection | Minimum TLS | Cipher Suites | Certificate |
|:-----------|:-----------|:-------------|:------------|
| Browser → Load Balancer | TLS 1.2 | AEAD ciphers (AES-256-GCM) | Organization PKI or public CA |
| Load Balancer → Tomcat | TLS 1.2 | Internal CA | Internal PKI |
| Tomcat → PostgreSQL | TLS 1.2 | `sslmode=verify-full` | Internal PKI |
| Tomcat → Artemis | TLS 1.2 | Broker TLS configuration | Internal PKI |

### 2.2 FIPS 140-2 Compliance

| Component | FIPS Mechanism | Status |
|:----------|:-------------|:-------|
| Java Runtime | JCE FIPS provider (e.g., Bouncy Castle FIPS) | Configurable |
| PostgreSQL | OpenSSL FIPS module | Configurable |
| TLS Termination | Hardware Security Module (HSM) for key storage | Recommended |

---

## 3. Cryptographic Protection (SC-12, SC-13)

### 3.1 Cryptographic Inventory

| Use Case | Algorithm | Key Length | Standard |
|:---------|:----------|:-----------|:---------|
| Password Hashing | PBKDF2WithHmacSHA256 | 256-bit derived | NIST SP 800-132 |
| Password Hashing (legacy) | BCrypt | 128-bit | — |
| Transport Encryption | TLS 1.2/1.3 | 256-bit (AES-GCM) | FIPS 140-2 |
| Database Encryption at Rest | AES-256 (TDE or filesystem) | 256-bit | FIPS 140-2 |
| Key Derivation (PBKDF2) | HMAC-SHA256, 310,000 iterations | — | NIST SP 800-132 |

### 3.2 Key Management

| Key Type | Storage | Rotation | Access |
|:---------|:--------|:---------|:-------|
| TLS Private Keys | HSM or encrypted keystore | Annual | Infrastructure team only |
| Database Encryption Keys | Key management service | Annual | DBA only |
| Application Signing Keys | Secure keystore | Annual | Build team only |
| Password Salt | Generated per-user (random) | Per password change | Application only |

---

## 4. Session Protection (SC-23)

| Control | Implementation |
|:--------|:---------------|
| **CSRF Tokens** | Spring Security generates per-session CSRF token for all forms |
| **Session Fixation** | New session ID generated on authentication (Spring Security default) |
| **Cookie Security** | `HttpOnly` flag prevents JavaScript access; `Secure` flag in production |
| **Session Timeout** | Configurable idle timeout (recommended: 30 minutes) |
| **Session Invalidation** | Explicit invalidation on logout with cookie deletion |

---

## 5. Information at Rest (SC-28)

| Data Store | Encryption Method | Key Management |
|:-----------|:-----------------|:---------------|
| PostgreSQL Database | TDE or filesystem-level encryption (LUKS/dm-crypt) | KMS |
| Report Files (`/atrs/reports/`) | Encrypted filesystem | OS-level key management |
| Application Logs | Encrypted filesystem | OS-level key management |
| Backup Storage | AES-256 encrypted backups | Backup encryption keys in KMS |
| Password Hashes | One-way hash (PBKDF2/BCrypt) — not reversible | N/A |

---

## 6. Input/Output Protection (SC-18)

### 6.1 Input Sanitization

All user inputs pass through multiple validation layers:

1. **Client-side:** Parsley.js validation (defense in depth, not trusted)
2. **Controller-level:** Spring Bean Validation (`@NotNull`, `@Size`, `@Pattern`)
3. **Custom Validators:** `TicketSearchValidator`, `MemberRegisterValidator`, etc.
4. **Repository-level:** MyBatis parameterized queries (prevent SQL injection)

### 6.2 Output Encoding

| View Technology | XSS Prevention |
|:---------------|:---------------|
| JSP | JSTL `<c:out>` and `fn:escapeXml()` |
| Thymeleaf | Auto-escaping by default (`th:text`) |
| REST API | JSON serialization (Jackson) with no HTML interpretation |

---

## 7. Denial of Service Protection (SC-5)

| Control | Configuration | Purpose |
|:--------|:-------------|:--------|
| Connection Pool Max | `cp.maxActive=96` | Prevent database connection exhaustion |
| Connection Pool Wait | `cp.maxWait=60000` (60s) | Timeout slow requests |
| WAF Rate Limiting | Configurable per deployment | Prevent HTTP flood |
| JMS Concurrency | `concurrency="1"` | Limit message processing load |
| Servlet Thread Pool | Tomcat `maxThreads` (default 200) | Limit concurrent requests |

---

## 8. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| SC-1 | Policy & Procedures | ✅ | This document |
| SC-5 | Denial of Service Protection | ✅ | Section 7 |
| SC-7 | Boundary Protection | ✅ | Section 1 |
| SC-8 | Transmission Confidentiality & Integrity | ✅ | Section 2 |
| SC-12 | Cryptographic Key Management | ✅ | Section 3.2 |
| SC-13 | Cryptographic Protection | ✅ | Section 3 |
| SC-23 | Session Authenticity | ✅ | Section 4 |
| SC-28 | Protection of Information at Rest | ✅ | Section 5 |
