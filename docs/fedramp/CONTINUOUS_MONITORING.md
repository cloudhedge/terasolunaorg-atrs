# ATRS — Continuous Monitoring Strategy

**Document ID:** ATRS-CA-001  
**FedRAMP Control Family:** Security Assessment and Authorization (CA)  
**NIST SP 800-53 Rev. 5 Controls:** CA-1 through CA-9  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Continuous Monitoring Program

This strategy defines the ongoing security assessment and monitoring activities to maintain the FedRAMP authorization of the ATRS system, aligned with NIST SP 800-137 and FedRAMP Continuous Monitoring requirements.

---

## 2. Monitoring Activities

### 2.1 Automated Monitoring

| Activity | Tool/Mechanism | Frequency | Alerts |
|:---------|:-------------|:----------|:-------|
| Application log analysis | SIEM + `atrs-application.log` | Real-time | Threshold-based |
| Security event monitoring | SIEM + `atrs-monitoring.log` | Real-time | All ERROR events |
| Vulnerability scanning | OWASP Dependency-Check | Every build | CVE > CVSS 7.0 |
| Infrastructure scanning | Nessus/Qualys | Monthly | Critical/High findings |
| File integrity monitoring | OSSEC/Tripwire | Real-time | Any change to production artifacts |
| Configuration drift detection | Infrastructure-as-Code tools | Daily | Any deviation from baseline |
| Uptime monitoring | Health check endpoint | Every 60 seconds | Downtime > 2 minutes |
| Database monitoring | PostgreSQL pg_stat + custom queries | Continuous | Anomalous query patterns |

### 2.2 Manual Assessments

| Activity | Frequency | Performed By | Deliverable |
|:---------|:----------|:-------------|:------------|
| Security control assessment | Annual | 3PAO | Assessment report |
| Penetration testing | Annual | Third-party assessor | Pentest report |
| Access review | Quarterly | ISSO + system owners | Access review report |
| Configuration audit | Quarterly | Operations team | Audit findings |
| Incident response drill | Annual | IR team | After-action report |
| Contingency plan test | Annual | Operations team | Test results |
| POA&M review | Monthly | ISSO | Updated POA&M |
| SBOM/dependency review | Quarterly | Application team | SBOM diff report |

---

## 3. Reporting Requirements

### 3.1 FedRAMP Monthly Reporting

| Deliverable | Content | Due |
|:------------|:--------|:----|
| Vulnerability scan results | Infrastructure + application scan summaries | Monthly |
| POA&M updates | Status of all open findings | Monthly |
| Significant change notifications | Architecture, boundary, or control changes | As needed |
| Incident reports | Any security incidents | Per IR timeline |

### 3.2 FedRAMP Annual Reporting

| Deliverable | Content | Due |
|:------------|:--------|:----|
| Annual security assessment | 3PAO assessment of control subset | Annually |
| Updated SSP | Reflect all changes over the year | Annually |
| Updated contingency plan test | Test results and updates | Annually |

---

## 4. Key Performance Indicators (KPIs)

| KPI | Target | Measurement |
|:----|:-------|:------------|
| Critical vulnerability remediation | < 30 days | Days from discovery to patch |
| High vulnerability remediation | < 60 days | Days from discovery to patch |
| Mean time to detect (MTTD) | < 1 hour | Time from event to alert |
| Mean time to respond (MTTR) | < 4 hours (CAT-1/2) | Time from alert to containment |
| System uptime | > 99.5% | Monthly availability |
| POA&M closure rate | > 80% on-time | Milestones met vs. planned |
| Failed login rate | < 5% of total attempts | Indicates credential issues |
| Patch currency | 100% within SLA | All components within patch window |

---

## 5. Significant Change Management

Changes requiring FedRAMP PMO notification:

| Change Type | Example | Action Required |
|:------------|:--------|:---------------|
| Boundary change | New external interface or data flow | Updated SSP + security assessment |
| Technology change | Framework version upgrade, new DBMS | Impact analysis + updated SSP |
| Data category change | New PII/PCI data types | Updated PIA + SSP |
| Infrastructure change | Cloud migration, new hosting | Full re-assessment possible |
| Security control change | Modified authentication, new encryption | Updated SSP + affected controls |

---

## 6. Roles and Responsibilities

| Role | Continuous Monitoring Duty |
|:-----|:--------------------------|
| **ISSO** | Overall ConMon program management, monthly reporting |
| **System Owner** | Authorize changes, resource allocation |
| **SOC** | Real-time monitoring, alert triage, initial response |
| **Application Team** | Dependency updates, SBOM maintenance, code-level fixes |
| **Platform Team** | Infrastructure patching, configuration management |
| **DBA Team** | Database patching, backup verification, query monitoring |
| **3PAO** | Annual assessment, control testing |

---

## 7. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| CA-1 | Policy & Procedures | ✅ | This document |
| CA-2 | Security Assessments | ✅ | Section 2.2 |
| CA-3 | System Interconnections | ✅ | SSP Section 4 |
| CA-5 | Plan of Action & Milestones | ✅ | SSP Section 6 |
| CA-6 | Security Authorization | ✅ | FedRAMP ATO process |
| CA-7 | Continuous Monitoring | ✅ | Sections 2–5 |
| CA-9 | Internal System Connections | ✅ | Architecture document |
