# ATRS — Access Control Policy

**Document ID:** ATRS-AC-001  
**FedRAMP Control Family:** Access Control (AC)  
**NIST SP 800-53 Rev. 5 Controls:** AC-1 through AC-25  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Purpose

This document defines the access control policies, mechanisms, and implementation details for the Airline Ticket Reservation System (ATRS), ensuring compliance with NIST SP 800-53 Rev. 5 Access Control (AC) family at the FedRAMP Moderate baseline.

---

## 2. Access Control Model

ATRS implements **Role-Based Access Control (RBAC)** with two principal roles:

| Role | Description | Privileges |
|:-----|:------------|:-----------|
| `ANONYMOUS` | Unauthenticated user | Flight search, view public pages, member registration |
| `ROLE_MEMBER` | Authenticated member | All anonymous privileges + profile update, reservation, history reports |

### 2.1 Access Control Matrix

| Resource | ANONYMOUS | ROLE_MEMBER | Notes |
|:---------|:----------|:------------|:------|
| `/ ` (Home) | ✅ Read | ✅ Read | Public landing page |
| `/auth/login` | ✅ Read | ✅ Read | Login form |
| `/auth/dologin` | ✅ POST | ✅ POST | Authentication endpoint |
| `/auth/dologout` | ❌ | ✅ POST | Logout with session invalidation |
| `/ticket/search` | ✅ Read | ✅ Read | Flight search |
| `/ticket/reserve/**` | ✅ Read/Write | ✅ Read/Write | Ticket booking (guest or member) |
| `/member/register` | ✅ Read/Write | ✅ Read/Write | New member registration |
| `/member/update` | ❌ Denied | ✅ Read/Write | Profile update (member only) |
| `/HistoryReport/**` | ❌ Denied | ✅ Read | Report download (member only) |
| `/api/v1/**` | ✅ HTTP Basic | ✅ HTTP Basic | REST API (stateless) |
| `/resources/**` | ✅ Read | ✅ Read | Static assets (no security context) |

---

## 3. Authentication Mechanisms

### 3.1 Web UI Authentication (AC-2, IA-2)

| Parameter | Value |
|:----------|:------|
| **Mechanism** | Form-based login |
| **Filter** | `AtrsUsernamePasswordAuthenticationFilter` |
| **Login URL** | `POST /auth/dologin` |
| **Username Field** | `membershipNumber` |
| **Password Field** | `password` |
| **Success Handler** | `AtrsAuthenticationSuccessHandler` (redirect to target URL) |
| **Failure Handler** | `AtrsAuthenticationFailureHandler` (forward to `/auth/login?error`) |
| **User Details Service** | `AtrsUserDetailsService` (queries `MEMBER_LOGIN` table) |

### 3.2 REST API Authentication (AC-2)

| Parameter | Value |
|:----------|:------|
| **Mechanism** | HTTP Basic Authentication |
| **Session** | Stateless (`create-session="stateless"`) |
| **CSRF** | Disabled (stateless context) |
| **Scope** | `/api/v1/**` |

### 3.3 Password Encoding (IA-5)

```
DelegatingPasswordEncoder
├── Default: "pbkdf2" → Pbkdf2PasswordEncoder (Spring Security 5.8 defaults)
│   ├── Algorithm: PBKDF2WithHmacSHA256
│   ├── Iterations: 310,000
│   └── Salt Length: 16 bytes
└── Fallback: "bcrypt" → BCryptPasswordEncoder
    ├── Algorithm: BCrypt
    └── Strength: 10 (default)
```

---

## 4. Session Management (AC-11, AC-12)

| Control | Implementation |
|:--------|:---------------|
| **Session Creation** | Created on successful authentication |
| **Session ID** | `JSESSIONID` cookie (HttpOnly, Secure in production) |
| **Session Fixation** | Protected via Spring Security default (new session on auth) |
| **Session Timeout** | Configurable in `web.xml` (default: 30 minutes) |
| **Logout** | `POST /auth/dologout` → invalidate session + delete JSESSIONID |
| **Concurrent Sessions** | Configurable via `<sec:session-management>` |

### 4.1 Logout Flow

1. User submits `POST /auth/dologout`
2. `AtrsLogoutSuccessHandler` fires `AtrsLogoutSuccessEvent`
3. `AuthLogoutService` updates `LOGIN_FLG = false` in `MEMBER_LOGIN`
4. HTTP session invalidated
5. `JSESSIONID` cookie deleted
6. User redirected to `/`

---

## 5. CSRF Protection (SC-23)

| Scope | CSRF Enabled | Rationale |
|:------|:-------------|:----------|
| Web UI forms | ✅ Yes | Prevents cross-site request forgery |
| REST API (`/api/v1/**`) | ❌ No | Stateless; protected by HTTP Basic |
| Static resources | N/A | Read-only, no security context |

Invalid CSRF tokens result in `InvalidCsrfTokenException` → dedicated error page (`csrf-error.jsp`).

---

## 6. Account Lifecycle Management (AC-2)

### 6.1 Account Creation
- Self-service registration via `MemberRegisterService`
- Generates unique `CUSTOMER_NO` from `SQ_MEMBER_1` sequence
- Stores hashed password in `MEMBER_LOGIN.PASSWORD`
- Initial `LOGIN_FLG = false`

### 6.2 Account Modification
- Profile updates via `MemberUpdateService` (requires `ROLE_MEMBER`)
- Password changes update `MEMBER_LOGIN.PASSWORD` and track `LAST_PASSWORD`

### 6.3 Account Termination
- Account deactivation procedures defined in operational runbooks
- Database-level account removal with cascade handling

---

## 7. Unsuccessful Login Handling (AC-7)

| Control | Current Implementation | FedRAMP Requirement |
|:--------|:----------------------|:--------------------|
| Failure Logging | ✅ `AtrsAuthenticationFailureHandler` logs failure | ✅ Met |
| User Notification | ✅ Forward to login page with error flag | ✅ Met |
| Account Lockout | ⚠️ Not implemented (POA&M item) | ❌ Required |
| Lockout Duration | ⚠️ Not implemented | ❌ Required |
| Lockout Threshold | ⚠️ Not implemented | ❌ Required |

> **POA&M POA-007:** Implement progressive account lockout after 3 consecutive failed attempts with 30-minute automatic unlock.

---

## 8. Access Control Audit Trail

All access control events are logged with the following fields:

| Field | Source | Example |
|:------|:-------|:--------|
| Timestamp | Logback pattern | `2026-02-24 14:30:00` |
| Thread | JVM | `http-nio-8080-exec-1` |
| User ID | `UserIdMDCPutFilter` | `0000000001` |
| Tracking ID | `X-Track` header | `abc123def456` |
| Event Type | Logger name | `AtrsAuthenticationSuccessHandler` |
| Message | Handler | `Authentication successful` |

---

## 9. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| AC-1 | Policy & Procedures | ✅ Implemented | This document |
| AC-2 | Account Management | ✅ Implemented | Sections 3, 6 |
| AC-3 | Access Enforcement | ✅ Implemented | Section 2.1 |
| AC-4 | Information Flow Enforcement | ✅ Implemented | Layered architecture |
| AC-5 | Separation of Duties | ✅ Implemented | RBAC model |
| AC-6 | Least Privilege | ✅ Implemented | Minimal role assignments |
| AC-7 | Unsuccessful Logon Attempts | ⚠️ Partial | Section 7 (lockout pending) |
| AC-8 | System Use Notification | ⚠️ Partial | Login page banner needed |
| AC-11 | Session Lock | ✅ Implemented | Session timeout |
| AC-12 | Session Termination | ✅ Implemented | Section 4 |
| AC-14 | Permitted Actions w/o Auth | ✅ Implemented | Public endpoints |
| AC-17 | Remote Access | ✅ Implemented | TLS required |
