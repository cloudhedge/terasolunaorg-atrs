# ATRS — Identification and Authentication

**Document ID:** ATRS-IA-001  
**FedRAMP Control Family:** Identification and Authentication (IA)  
**NIST SP 800-53 Rev. 5 Controls:** IA-1 through IA-11  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. User Identification (IA-2, IA-4)

### 1.1 Identifier Types

| User Type | Identifier | Format | Uniqueness |
|:----------|:----------|:-------|:-----------|
| Member | `CUSTOMER_NO` (membership number) | VARCHAR(10), numeric | Sequence-generated (`SQ_MEMBER_1`) |
| API Consumer | Username (membership number) | Same as member | Same identifier |
| Administrator | OS/infrastructure account | Per organizational policy | Unique per individual |

### 1.2 Identifier Lifecycle

| Phase | Mechanism |
|:------|:----------|
| **Assignment** | Auto-generated via `SQ_MEMBER_1` sequence (guaranteed unique) |
| **Management** | Stored in `MEMBER.CUSTOMER_NO` (immutable after creation) |
| **Deactivation** | `MEMBER_LOGIN.LOGIN_FLG` set to `false` |
| **Reuse Prevention** | Sequence-based generation prevents reuse (`CYCLE` with 10-digit range) |

---

## 2. Authenticator Management (IA-5)

### 2.1 Password Encoding Stack

```
DelegatingPasswordEncoder
│
├── Primary: "pbkdf2"
│   ├── Algorithm: PBKDF2WithHmacSHA256
│   ├── Iterations: 310,000
│   ├── Salt: 16 bytes (random, per-password)
│   ├── Derived Key Length: 256 bits
│   └── Standard: NIST SP 800-132
│
└── Legacy: "bcrypt"
    ├── Algorithm: BCrypt
    ├── Cost Factor: 10 (1024 iterations)
    └── Salt: 16 bytes (embedded in hash)
```

### 2.2 Password Storage

| Column | Table | Purpose |
|:-------|:------|:--------|
| `MEMBER_LOGIN.PASSWORD` | `MEMBER_LOGIN` | Current password hash (prefixed: `{pbkdf2}...` or `{bcrypt}...`) |
| `MEMBER_LOGIN.LAST_PASSWORD` | `MEMBER_LOGIN` | Previous password hash (for history enforcement) |

### 2.3 Password Policy Requirements

| Policy | Current Implementation | FedRAMP Moderate Requirement |
|:-------|:---------------------|:---------------------------|
| Minimum Length | Application-defined via `@Size` | 12+ characters |
| Complexity | Validation annotations | Upper + lower + number + special |
| History | `LAST_PASSWORD` tracked (1 previous) | 24 previous passwords |
| Maximum Age | Not implemented | 60 days |
| Minimum Age | Not implemented | 1 day |
| Failed Attempts Lockout | Not implemented (POA&M) | 3 attempts → 30 min lockout |

> **POA&M Items:** Password history depth, maximum/minimum age, and account lockout require implementation to meet FedRAMP Moderate.

---

## 3. Authentication Mechanisms (IA-2, IA-8)

### 3.1 Web UI Authentication

| Property | Value |
|:---------|:------|
| Filter | `AtrsUsernamePasswordAuthenticationFilter` |
| Authentication Manager | Spring Security `AuthenticationManager` |
| User Details Service | `AtrsUserDetailsService` |
| Success Handler | `AtrsAuthenticationSuccessHandler` |
| Failure Handler | `AtrsAuthenticationFailureHandler` |
| Login Endpoint | `POST /auth/dologin` |

**Authentication Flow:**

```
1. User submits membershipNumber + password to POST /auth/dologin
2. AtrsUsernamePasswordAuthenticationFilter extracts credentials
3. AuthenticationManager delegates to AuthenticationProvider
4. AtrsUserDetailsService loads AtrsUserDetails from MEMBER_LOGIN table
5. DelegatingPasswordEncoder verifies password hash
6. On success:
   a. AuthLoginService updates LOGIN_FLG=true, LOGIN_DATE_TIME
   b. AtrsAuthenticationSuccessHandler redirects to target URL
   c. Security context stored in HttpSession
7. On failure:
   a. AtrsAuthenticationFailureHandler forwards to /auth/login?error
   b. Event logged
```

### 3.2 REST API Authentication

| Property | Value |
|:---------|:------|
| Mechanism | HTTP Basic Authentication |
| Session | Stateless (`create-session="stateless"`) |
| Scope | `/api/v1/**` |
| CSRF | Disabled (stateless context) |

### 3.3 Multi-Factor Authentication (IA-2(1))

| Scope | MFA Status | Notes |
|:------|:-----------|:------|
| Member accounts (web) | ⚠️ Not implemented | POA&M — implement TOTP or WebAuthn |
| API access | ⚠️ Not implemented | POA&M — migrate to OAuth 2.0 + MFA |
| Administrative access | ✅ Infrastructure-level | SSH key + MFA via bastion host |

---

## 4. Authenticator Feedback (IA-6)

| Context | Feedback | Secure |
|:--------|:---------|:-------|
| Login form password field | Masked (`type="password"`) | ✅ |
| Login failure message | Generic "authentication failed" | ✅ (no username/password hint) |
| API authentication failure | HTTP 401 (no detail) | ✅ |
| Password in logs | Never logged (filtered by framework) | ✅ |

---

## 5. Session Binding (IA-3)

| Property | Implementation |
|:---------|:---------------|
| Session ID | `JSESSIONID` cookie, server-generated |
| Session Fixation | New session on authentication (Spring Security default) |
| Session-to-User Binding | Security context stored in `HttpSessionSecurityContextRepository` |
| Device Identification | Not implemented (browser-based, no device binding) |

---

## 6. Cryptographic Module Authentication (IA-7)

| Module | Authentication |
|:-------|:---------------|
| Java JCE Provider | JVM-managed keystore access |
| TLS Libraries | Certificate-based mutual authentication available |
| PBKDF2 Implementation | Spring Security cryptographic module |

---

## 7. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| IA-1 | Policy & Procedures | ✅ | This document |
| IA-2 | Identification and Authentication | ✅ | Section 3 |
| IA-2(1) | MFA for Privileged Accounts | ⚠️ Partial | Admin: infrastructure MFA; App: POA&M |
| IA-2(2) | MFA for Non-Privileged Accounts | ⚠️ | POA&M |
| IA-3 | Device Identification | ✅ | Session binding |
| IA-4 | Identifier Management | ✅ | Section 1 |
| IA-5 | Authenticator Management | ⚠️ Partial | Encoding: ✅; Policy gaps: POA&M |
| IA-5(1) | Password-Based Authentication | ⚠️ Partial | PBKDF2 ✅; Policy gaps noted |
| IA-6 | Authenticator Feedback | ✅ | Section 4 |
| IA-7 | Cryptographic Module Auth | ✅ | Section 6 |
| IA-8 | Non-Organizational User ID/Auth | ✅ | Guest access + member registration |
