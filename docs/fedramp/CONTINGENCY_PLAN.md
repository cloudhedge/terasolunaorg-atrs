# ATRS — Contingency Plan

**Document ID:** ATRS-CP-001  
**FedRAMP Control Family:** Contingency Planning (CP)  
**NIST SP 800-53 Rev. 5 Controls:** CP-1 through CP-13  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Purpose

This plan ensures the Airline Ticket Reservation System (ATRS) can be recovered and reconstituted following a disruption, ensuring continuity of operations for airline reservation services.

---

## 2. Recovery Objectives

| Metric | Target | Rationale |
|:-------|:-------|:----------|
| **Recovery Time Objective (RTO)** | 4 hours | Business operations require timely restoration |
| **Recovery Point Objective (RPO)** | 1 hour | Minimize reservation and member data loss |
| **Maximum Tolerable Downtime (MTD)** | 24 hours | Beyond this, manual processes activated |

---

## 3. Essential Functions

| Priority | Function | Components | Impact of Loss |
|:---------|:---------|:-----------|:---------------|
| 1 | Database availability | PostgreSQL | All operations halted |
| 2 | Application serving | Tomcat + WAR | No user access |
| 3 | Authentication service | Spring Security + MEMBER_LOGIN | No secure access |
| 4 | Reservation processing | TicketReserveService | Revenue loss |
| 5 | Flight search | TicketSearchService | Customer impact |
| 6 | Report generation | Artemis + JMS Listener | Delayed reports (non-critical) |

---

## 4. Backup Strategy (CP-9)

### 4.1 Database Backups

| Backup Type | Frequency | Retention | Storage |
|:------------|:----------|:----------|:--------|
| WAL Archiving | Continuous | 7 days | Encrypted off-site storage |
| Full Database Dump | Daily (03:00 UTC) | 30 days | Encrypted off-site storage |
| Logical Backup (pg_dump) | Weekly | 90 days | Encrypted cold storage |

### 4.2 Application Backups

| Component | Backup Method | Storage |
|:----------|:-------------|:--------|
| WAR artifact | Maven artifact repository | Artifact repository (versioned) |
| Configuration files | Git repository | Git + off-site mirror |
| SQL migration scripts | Git repository | Git + off-site mirror |
| Environment properties | Secrets manager + Git | Secrets manager backup |

### 4.3 Report File Backups

| Path | Frequency | Retention |
|:-----|:----------|:----------|
| `/atrs/reports/reservation` | Daily incremental | 90 days |

---

## 5. Recovery Procedures (CP-10)

### 5.1 Database Recovery

```
1. Provision replacement PostgreSQL instance
2. Restore from latest full backup
3. Apply WAL archives to reach RPO
4. Verify data integrity:
   - SELECT COUNT(*) from MEMBER, RESERVATION, FLIGHT
   - Validate foreign key constraints
   - Verify sequence values (SQ_MEMBER_1, SQ_RESERVATION_1, etc.)
5. Update application connection strings
6. Verify connectivity from application tier
```

### 5.2 Application Recovery

```
1. Provision replacement Tomcat instance(s)
2. Deploy verified WAR from artifact repository:
   - Verify artifact checksum/signature
   - Deploy specific version: atrs-1.11.0.RELEASE.war
3. Apply environment configuration:
   - atrs-infra.properties (from secrets manager)
   - logback.xml (from configuration management)
4. Verify database connectivity
5. Smoke test core functions:
   - Home page loads
   - Flight search returns results
   - Login/logout works
   - Reservation flow completes
6. Register with load balancer
```

### 5.3 Message Broker Recovery

```
1. Provision replacement Artemis instance
2. Configure queues for reservation history reports
3. Update JMS connection properties
4. Verify message flow:
   - Submit test report request
   - Confirm ReservationHistoryReportListener processes message
5. Re-process any undelivered messages from dead-letter queue
```

### 5.4 Complete System Recovery (Disaster)

```
1. Activate DR site infrastructure
2. Restore database (5.1)
3. Deploy application (5.2)
4. Restore message broker (5.3)
5. Restore report file storage
6. Update DNS / load balancer to DR site
7. Validate all interconnections
8. Execute full integration test suite
9. Notify stakeholders of recovery
```

---

## 6. Contingency Plan Testing (CP-4)

| Test Type | Frequency | Scope |
|:----------|:----------|:------|
| Tabletop Exercise | Semi-annual | Walk through recovery procedures |
| Component Recovery Test | Annual | Restore individual components from backup |
| Full DR Test | Annual | Complete failover to DR site |
| Backup Verification | Monthly | Verify backup integrity and restorability |

---

## 7. Alternative Processing (CP-7)

| Scenario | Alternative | Duration |
|:---------|:------------|:---------|
| Application server failure | Failover to standby instance | Automatic (< 5 min) |
| Database failure | Promote read replica | Manual (< 30 min) |
| Data center outage | Activate DR site | Manual (< 4 hours) |
| Extended outage (> MTD) | Manual reservation processing | Until recovery |

---

## 8. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| CP-1 | Policy & Procedures | ✅ | This document |
| CP-2 | Contingency Plan | ✅ | This document |
| CP-3 | Contingency Training | ✅ | Annual training |
| CP-4 | Contingency Plan Testing | ✅ | Section 6 |
| CP-6 | Alternate Storage Site | ✅ | Encrypted off-site backups |
| CP-7 | Alternate Processing Site | ✅ | Section 7 |
| CP-9 | Information System Backup | ✅ | Section 4 |
| CP-10 | System Recovery & Reconstitution | ✅ | Section 5 |
