# ATRS — Airline Ticket Reservation System Documentation

## Document Index

| Document | Description | FedRAMP Control Families |
|:---------|:------------|:------------------------|
| [System Security Plan (SSP)](fedramp/SYSTEM_SECURITY_PLAN.md) | Comprehensive security plan covering all NIST 800-53 control families | All |
| [Architecture & Design](ARCHITECTURE.md) | System architecture, data flow diagrams, and component inventory | SA-4, SA-5, CM-6 |
| [Access Control Policy](fedramp/ACCESS_CONTROL.md) | Authentication, authorization, and session management | AC-1 through AC-25 |
| [Audit & Accountability](fedramp/AUDIT_ACCOUNTABILITY.md) | Logging, monitoring, and audit trail documentation | AU-1 through AU-16 |
| [Configuration Management](fedramp/CONFIGURATION_MANAGEMENT.md) | Build process, dependency management, and change control | CM-1 through CM-11 |
| [Incident Response Plan](fedramp/INCIDENT_RESPONSE.md) | Incident detection, reporting, and recovery procedures | IR-1 through IR-10 |
| [Contingency Plan](fedramp/CONTINGENCY_PLAN.md) | Backup, disaster recovery, and business continuity | CP-1 through CP-13 |
| [Risk Assessment](fedramp/RISK_ASSESSMENT.md) | Threat modeling, vulnerability analysis, and risk register | RA-1 through RA-7 |
| [System & Communications Protection](fedramp/SYSTEM_COMMUNICATIONS_PROTECTION.md) | Network security, encryption, and boundary protection | SC-1 through SC-44 |
| [System & Information Integrity](fedramp/SYSTEM_INFORMATION_INTEGRITY.md) | Input validation, error handling, and integrity controls | SI-1 through SI-16 |
| [Identification & Authentication](fedramp/IDENTIFICATION_AUTHENTICATION.md) | Authenticator management, credential policies | IA-1 through IA-11 |
| [Personnel Security](fedramp/PERSONNEL_SECURITY.md) | Screening, termination, and role-based access | PS-1 through PS-8 |
| [Continuous Monitoring Strategy](fedramp/CONTINUOUS_MONITORING.md) | Ongoing assessment and authorization maintenance | CA-1 through CA-9 |
| [Supply Chain Risk Management](fedramp/SUPPLY_CHAIN_RISK.md) | Third-party dependencies and provenance tracking | SR-1 through SR-12 |
| [Privacy Impact Assessment](fedramp/PRIVACY_IMPACT_ASSESSMENT.md) | PII handling, data classification, and retention | AP, AR, DI, DM, IP, SE, TR, UL |
| [Deployment Guide](DEPLOYMENT.md) | Installation, configuration, and operational procedures | SA-10, CM-3 |
| [API Reference](API_REFERENCE.md) | REST API endpoints, request/response schemas | SA-5 |
| [Database Schema](DATABASE_SCHEMA.md) | Entity-relationship model and data dictionary | SA-5, SC-28 |

## FedRAMP Authorization Levels

This documentation is structured to support **FedRAMP Moderate** baseline authorization (NIST SP 800-53 Rev. 5). The control implementations documented herein address 325 controls across 20 control families.

## Document Revision History

| Version | Date | Author | Description |
|:--------|:-----|:-------|:------------|
| 1.0 | 2026-02-24 | ATRS Security Team | Initial FedRAMP documentation package |
