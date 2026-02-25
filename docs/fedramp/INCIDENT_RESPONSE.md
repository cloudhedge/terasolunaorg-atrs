# ATRS — Incident Response Plan

**Document ID:** ATRS-IR-001  
**FedRAMP Control Family:** Incident Response (IR)  
**NIST SP 800-53 Rev. 5 Controls:** IR-1 through IR-10  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Purpose and Scope

This plan establishes procedures for detecting, responding to, and recovering from security incidents affecting the Airline Ticket Reservation System (ATRS). It covers all components within the ATRS authorization boundary including application servers, database, message broker, and supporting infrastructure.

---

## 2. Incident Response Team

| Role | Responsibility | Contact |
|:-----|:---------------|:--------|
| **Incident Commander** | Overall incident coordination | [TBD] |
| **ISSO** | Security assessment and FedRAMP notification | [TBD] |
| **Application Lead** | ATRS application-level investigation | [TBD] |
| **DBA Lead** | Database forensics and recovery | [TBD] |
| **Infrastructure Lead** | Network, server, and broker investigation | [TBD] |
| **Communications Lead** | Stakeholder and user notification | [TBD] |

---

## 3. Incident Categories

| Category | Severity | Description | Examples |
|:---------|:---------|:------------|:---------|
| **CAT-1** | Critical | Active exploitation or data breach | PII/PCI data exfiltration, unauthorized admin access |
| **CAT-2** | High | Attempted exploitation or policy violation | Brute-force attacks, SQL injection attempts, CSRF violations |
| **CAT-3** | Medium | Suspicious activity | Unusual login patterns, excessive failed logins, anomalous API usage |
| **CAT-4** | Low | Policy non-compliance | Missing patches, configuration drift, expired certificates |

---

## 4. Detection Capabilities

### 4.1 Application-Level Detection

| Indicator | Source | Detection Method |
|:----------|:-------|:-----------------|
| Failed login spike | `AtrsAuthenticationFailureHandler` | SIEM threshold alert |
| CSRF violations | Spring Security logs | SIEM pattern match |
| Access denied events | `DelegatingAccessDeniedHandler` | SIEM correlation |
| Business exception surge | `ExceptionLogger.Monitoring` | Monitoring log alerts |
| SQL injection attempts | Bean Validation / MyBatis errors | SIEM pattern match |
| Anomalous API usage | `AccessLogFilter` | SIEM behavioral analysis |

### 4.2 Infrastructure-Level Detection

| Indicator | Source | Detection Method |
|:----------|:-------|:-----------------|
| Unauthorized access attempts | WAF / IDS | Automated alerting |
| Database anomalies | PostgreSQL audit logs | DBA monitoring |
| JMS broker issues | Artemis logs | Infrastructure monitoring |
| Resource exhaustion | System metrics | Threshold alerts |

---

## 5. Incident Response Procedures

### 5.1 Phase 1: Detection and Analysis (0–1 hour)

1. **Triage** — Confirm incident is genuine (not false positive)
2. **Categorize** — Assign severity (CAT-1 through CAT-4)
3. **Document** — Create incident ticket with initial findings
4. **Notify** — Alert Incident Response Team per severity:
   - CAT-1/2: Immediate notification
   - CAT-3/4: Next business day

### 5.2 Phase 2: Containment (1–4 hours for CAT-1/2)

| Action | Scope | Procedure |
|:-------|:------|:----------|
| Isolate affected server | Infrastructure | Remove from load balancer, block network access |
| Disable compromised accounts | Application | Set `LOGIN_FLG = false`, reset passwords |
| Block attacking IPs | WAF/Firewall | Add to block list |
| Preserve evidence | All | Snapshot logs, memory dumps, disk images |
| Rotate credentials | Database/JMS | Change service account passwords |

### 5.3 Phase 3: Eradication (4–24 hours)

1. Identify root cause and attack vector
2. Patch vulnerability or close configuration gap
3. Review all system accounts for unauthorized changes
4. Scan for persistence mechanisms (backdoors, scheduled tasks)
5. Verify database integrity (`MEMBER`, `RESERVATION`, `MEMBER_LOGIN` tables)

### 5.4 Phase 4: Recovery (24–72 hours)

1. Restore from verified clean backups if needed
2. Rebuild compromised systems from baseline images
3. Re-deploy application from trusted artifact repository
4. Re-initialize database from versioned SQL scripts if needed
5. Gradually restore service with enhanced monitoring
6. Validate system functionality via smoke tests

### 5.5 Phase 5: Post-Incident (1–2 weeks)

1. Complete incident report
2. Conduct lessons-learned meeting
3. Update POA&M with new findings
4. Update detection rules and response procedures
5. Brief stakeholders

---

## 6. FedRAMP Reporting Requirements

### 6.1 US-CERT Notification Timeline

| Incident Type | Notification Timeline |
|:--------------|:---------------------|
| CAT-1 (Critical) | Within 1 hour of detection |
| CAT-2 (High) | Within 2 hours of detection |
| CAT-3 (Medium) | Within 72 hours of detection |
| CAT-4 (Low) | Monthly report |

### 6.2 Required Notifications

| Recipient | Method | Timeline |
|:----------|:-------|:---------|
| FedRAMP PMO | FedRAMP Incident Communication Procedures | Per category |
| US-CERT | us-cert.cisa.gov incident report | Per category |
| Authorizing Official | Email + phone | Within 1 hour (CAT-1/2) |
| Affected Users | Email notification | After containment |

---

## 7. ATRS-Specific Incident Playbooks

### 7.1 Credential Compromise

1. Identify affected `MEMBER_LOGIN` records
2. Force password reset on affected accounts
3. Invalidate all active sessions
4. Review `LOGIN_DATE_TIME` for unauthorized access timestamps
5. Check `RESERVATION` table for fraudulent bookings
6. Notify affected members

### 7.2 SQL Injection Attempt

1. Review application logs for injection patterns
2. Verify MyBatis parameterized queries are intact
3. Check database for unauthorized DDL/DML
4. Update WAF rules with attack signatures
5. Review and strengthen input validation

### 7.3 PCI Data Exposure

1. Immediately contain exposure vector
2. Identify scope (which `MEMBER.CREDIT_NO` records affected)
3. Notify PCI DSS QSA
4. Follow PCI incident response requirements
5. Notify affected cardholders and issuers

---

## 8. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| IR-1 | Policy & Procedures | ✅ | This document |
| IR-2 | Incident Response Training | ✅ | Annual training + drills |
| IR-3 | Incident Response Testing | ✅ | Annual tabletop exercise |
| IR-4 | Incident Handling | ✅ | Section 5 |
| IR-5 | Incident Monitoring | ✅ | Section 4 |
| IR-6 | Incident Reporting | ✅ | Section 6 |
| IR-7 | Incident Response Assistance | ✅ | Section 2 (team roles) |
| IR-8 | Incident Response Plan | ✅ | This document |
