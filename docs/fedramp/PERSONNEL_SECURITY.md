# ATRS — Personnel Security

**Document ID:** ATRS-PS-001  
**FedRAMP Control Family:** Personnel Security (PS)  
**NIST SP 800-53 Rev. 5 Controls:** PS-1 through PS-8  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Personnel Security Policy (PS-1)

All personnel with access to the ATRS system (development, operations, administration) must comply with organizational personnel security policies including background investigation, access agreements, and security training requirements.

---

## 2. Position Risk Designation (PS-2)

| Role | Risk Level | Access | Screening Required |
|:-----|:-----------|:-------|:------------------|
| System Administrator | High | Full infrastructure access | Tier 2 (BI) |
| Database Administrator | High | Database with PII/PCI | Tier 2 (BI) |
| Application Developer | Moderate | Source code, development data | Tier 1 (NACI) |
| Security Analyst | High | Logs, audit data, security config | Tier 2 (BI) |
| Operations Staff | Moderate | Monitoring, deployment | Tier 1 (NACI) |
| Help Desk | Low | Read-only member lookups | Tier 1 (NACI) |

---

## 3. Personnel Screening (PS-3)

| Requirement | Implementation |
|:------------|:---------------|
| Pre-employment screening | Background check before system access granted |
| Re-investigation | Per risk designation schedule |
| Citizenship verification | Required for roles handling PCI/PII |
| Access pending screening | Escorted/supervised access only |

---

## 4. Personnel Termination (PS-4)

Upon termination or role change:

| Action | Timeline | Responsible |
|:-------|:---------|:------------|
| Disable system accounts | Within 4 hours | IT Operations |
| Revoke VPN/SSH access | Within 4 hours | Infrastructure |
| Revoke database access | Within 4 hours | DBA |
| Revoke Git/artifact repository access | Within 24 hours | DevOps |
| Collect physical access badges | Same day | Physical Security |
| Audit last 30 days of activity | Within 72 hours | Security Team |
| Change shared credentials (if any) | Within 24 hours | All teams |

---

## 5. Personnel Transfer (PS-5)

| Action | Timeline |
|:-------|:---------|
| Review and adjust access rights | Before transfer effective date |
| Remove access no longer needed | On transfer date |
| Grant new access per role | After manager approval |
| Update access control records | Within 24 hours |

---

## 6. Access Agreements (PS-6)

All personnel must sign before receiving system access:

- [x] Acceptable Use Policy (AUP)
- [x] Non-Disclosure Agreement (NDA)
- [x] Rules of Behavior (RoB)
- [x] Security Awareness Acknowledgment
- [x] PCI DSS Awareness (for PCI-access roles)
- [x] Incident Reporting Obligations

---

## 7. Third-Party Personnel Security (PS-7)

| Requirement | Implementation |
|:------------|:---------------|
| Contractor screening | Same requirements as equivalent employee role |
| Access monitoring | Enhanced audit logging for third-party accounts |
| Access duration | Time-limited, expires on contract end date |
| NDA/access agreement | Required before access provisioned |

---

## 8. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| PS-1 | Policy & Procedures | ✅ | This document |
| PS-2 | Position Risk Designation | ✅ | Section 2 |
| PS-3 | Personnel Screening | ✅ | Section 3 |
| PS-4 | Personnel Termination | ✅ | Section 4 |
| PS-5 | Personnel Transfer | ✅ | Section 5 |
| PS-6 | Access Agreements | ✅ | Section 6 |
| PS-7 | Third-Party Personnel Security | ✅ | Section 7 |
| PS-8 | Personnel Sanctions | ✅ | Organizational HR policy |
