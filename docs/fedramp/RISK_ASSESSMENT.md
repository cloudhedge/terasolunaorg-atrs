# ATRS — Risk Assessment

**Document ID:** ATRS-RA-001  
**FedRAMP Control Family:** Risk Assessment (RA)  
**NIST SP 800-53 Rev. 5 Controls:** RA-1 through RA-7  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. System Characterization

| Attribute | Value |
|:----------|:------|
| System Name | Airline Ticket Reservation System (ATRS) |
| FIPS 199 Category | Moderate |
| Data Sensitivity | PII, Payment Card Data, Authentication Credentials |
| Users | Public (flight search), Members (reservations), Administrators |
| Technology | Java 17/21, Spring 6.x, PostgreSQL, Apache Artemis |

---

## 2. Threat Model

### 2.1 Threat Sources

| Threat Source | Motivation | Capability |
|:-------------|:-----------|:-----------|
| External Attacker | Financial gain, data theft | Moderate to High |
| Insider Threat | Fraud, data exfiltration | High (privileged access) |
| Automated Bot | Credential stuffing, scraping | Moderate |
| Nation-State Actor | Espionage, disruption | Very High |
| Script Kiddie | Opportunistic exploitation | Low |

### 2.2 Attack Surface Analysis

| Entry Point | Exposure | Controls |
|:------------|:---------|:---------|
| Web UI (HTTPS) | Public internet | WAF, TLS, CSRF, input validation |
| REST API (`/api/v1/**`) | Public internet | HTTP Basic, rate limiting (needed), input validation |
| Database (port 5432) | Internal network | Firewall, TLS, authentication |
| JMS Broker (port 61616) | Internal network | Firewall, authentication |
| Report filesystem | Local server | OS permissions, encryption |
| Administrative SSH | Management network | Bastion host, MFA, key-based auth |

---

## 3. Risk Register

### 3.1 Critical Risks

| ID | Risk | Likelihood | Impact | Risk Level | Mitigation | Status |
|:---|:-----|:-----------|:-------|:-----------|:-----------|:-------|
| R-001 | Credential stuffing attack against login | High | High | **Critical** | Implement account lockout (AC-7), rate limiting, CAPTCHA | ⚠️ POA&M |
| R-002 | SQL injection via unvalidated input | Low | Critical | **High** | MyBatis parameterized queries, Bean Validation, WAF | ✅ Mitigated |
| R-003 | PCI data breach (credit card numbers) | Medium | Critical | **Critical** | Encryption at rest, tokenization, PCI DSS controls | ⚠️ Partial |
| R-004 | Session hijacking | Medium | High | **High** | HTTPS, HttpOnly cookies, session fixation protection | ✅ Mitigated |
| R-005 | Cross-site scripting (XSS) | Medium | Medium | **Medium** | Output encoding (JSP/Thymeleaf), CSP headers | ✅ Mitigated |

### 3.2 High Risks

| ID | Risk | Likelihood | Impact | Risk Level | Mitigation | Status |
|:---|:-----|:-----------|:-------|:-----------|:-----------|:-------|
| R-006 | Hardcoded credentials in properties files | High | High | **High** | Secrets manager integration | ⚠️ POA&M |
| R-007 | Unencrypted database connection | High | High | **High** | PostgreSQL TLS (`sslmode=verify-full`) | ⚠️ POA&M |
| R-008 | Insufficient log retention | Medium | Medium | **Medium** | SIEM with 90+ day retention | ⚠️ POA&M |
| R-009 | No MFA for member accounts | Medium | Medium | **Medium** | Implement TOTP/WebAuthn | ⚠️ POA&M |
| R-010 | CSRF disabled on REST API | Low | Medium | **Medium** | Stateless design with HTTP Basic compensates | ✅ Accepted |

### 3.3 Medium Risks

| ID | Risk | Likelihood | Impact | Risk Level | Mitigation | Status |
|:---|:-----|:-----------|:-------|:-----------|:-----------|:-------|
| R-011 | Denial of service (connection pool exhaustion) | Medium | Medium | **Medium** | Connection pool limits (96 max), WAF rate limiting | ✅ Partial |
| R-012 | JMS message tampering | Low | Medium | **Medium** | TLS for JMS, message validation | ⚠️ POA&M |
| R-013 | Report file unauthorized access | Low | Medium | **Medium** | OS permissions, encrypted storage | ✅ Partial |
| R-014 | Dependency vulnerability (supply chain) | Medium | Medium | **Medium** | SBOM, dependency scanning | ⚠️ POA&M |
| R-015 | Information disclosure via error messages | Medium | Low | **Low** | Custom error pages, exception code mapping | ✅ Mitigated |

---

## 4. Vulnerability Assessment

### 4.1 Application Vulnerability Scan Schedule

| Scan Type | Tool | Frequency | Coverage |
|:----------|:-----|:----------|:---------|
| SAST | SonarQube / Checkmarx | Every commit (CI/CD) | Source code |
| DAST | OWASP ZAP / Burp Suite | Monthly | Running application |
| Dependency Scan | OWASP Dependency-Check / Snyk | Every build | Third-party libraries |
| Container Scan | Trivy / Grype | Every build | Container images |
| Infrastructure Scan | Nessus / Qualys | Monthly | OS, services, network |
| Penetration Test | Third-party assessor | Annual | Full scope |

### 4.2 Known Vulnerability Categories

| Category | OWASP Top 10 | ATRS Controls |
|:---------|:-------------|:-------------|
| Injection (A03:2021) | SQL Injection | MyBatis parameterized queries, Bean Validation |
| Broken Authentication (A07:2021) | Session fixation, weak passwords | Spring Security, PBKDF2, session management |
| Sensitive Data Exposure (A02:2021) | PII/PCI in transit/at rest | TLS, encryption, masked logs |
| XSS (A03:2021) | Reflected/Stored XSS | Output encoding, CSP headers |
| CSRF (A01:2021) | Cross-site request forgery | Spring Security CSRF tokens |
| Security Misconfiguration (A05:2021) | Default credentials, verbose errors | Configuration hardening, custom error pages |
| Vulnerable Components (A06:2021) | Outdated libraries | Dependency scanning, SBOM |

---

## 5. Data Classification

| Data Element | Table/Column | Classification | Protection Required |
|:-------------|:-------------|:---------------|:-------------------|
| Member Name (Kanji/Kana) | `MEMBER.KANJI_*`, `MEMBER.KANA_*` | PII | Encryption at rest, TLS in transit |
| Email Address | `MEMBER.MAIL` | PII | Encryption at rest, TLS in transit |
| Phone Number | `MEMBER.TEL` | PII | Encryption at rest, TLS in transit |
| Home Address | `MEMBER.ADDRESS`, `MEMBER.ZIP_CODE` | PII | Encryption at rest, TLS in transit |
| Date of Birth | `MEMBER.BIRTHDAY` | PII | Encryption at rest, TLS in transit |
| Credit Card Number | `MEMBER.CREDIT_NO` | PCI (CHD) | Tokenization/encryption, PCI DSS |
| Credit Card Expiry | `MEMBER.CREDIT_TERM` | PCI (CHD) | Tokenization/encryption, PCI DSS |
| Password Hash | `MEMBER_LOGIN.PASSWORD` | Credential | One-way hash (PBKDF2), never logged |
| Reservation Data | `RESERVATION.*` | Business | Integrity protection, backup |
| Passenger Info | `PASSENGER.*` | PII | Encryption at rest, TLS in transit |

---

## 6. Risk Treatment Plan

| Risk ID | Treatment | Control Enhancement | Owner | Target Date |
|:--------|:----------|:-------------------|:------|:------------|
| R-001 | Mitigate | Account lockout, CAPTCHA, rate limiting | App Team | [TBD] |
| R-003 | Mitigate | PCI tokenization, column-level encryption | DBA + App | [TBD] |
| R-006 | Mitigate | HashiCorp Vault / AWS Secrets Manager | Platform | [TBD] |
| R-007 | Mitigate | PostgreSQL TLS configuration | DBA | [TBD] |
| R-008 | Mitigate | SIEM deployment with retention policies | SecOps | [TBD] |
| R-009 | Mitigate | MFA implementation (TOTP) | App Team | [TBD] |
| R-010 | Accept | Risk accepted with compensating controls | ISSO | Accepted |

---

## 7. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| RA-1 | Policy & Procedures | ✅ | This document |
| RA-2 | Security Categorization | ✅ | SSP Section 1.3 |
| RA-3 | Risk Assessment | ✅ | Section 3 |
| RA-5 | Vulnerability Scanning | ✅ | Section 4 |
| RA-7 | Risk Response | ✅ | Section 6 |
