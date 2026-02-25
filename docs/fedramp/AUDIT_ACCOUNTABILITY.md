# ATRS — Audit and Accountability

**Document ID:** ATRS-AU-001  
**FedRAMP Control Family:** Audit and Accountability (AU)  
**NIST SP 800-53 Rev. 5 Controls:** AU-1 through AU-16  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Audit Architecture

### 1.1 Logging Framework

ATRS uses **Logback** (via SLF4J) for all application logging, configured in `logback.xml`.

### 1.2 Log Destinations

| Log File | Purpose | Retention | Level Filter |
|:---------|:--------|:----------|:-------------|
| `STDOUT` | Console output (development) | Ephemeral | All |
| `atrs-application.log` | Application events & errors | 7 days (rolling daily) | Per logger config |
| `atrs-monitoring.log` | Security & operational alerts | 7 days (rolling daily) | ERROR only |

> **FedRAMP Requirement:** Production deployments MUST forward logs to a centralized SIEM with minimum **90-day online** and **1-year archive** retention.

### 1.3 Log Record Format

All log entries follow a consistent tab-delimited format:

```
date:<timestamp>\tthread:<thread>\tuser:<userId>\tX-Track:<trackingId>\tlevel:<level>\tlogger:<loggerName>\tmessage:<message>
```

| Field | Description | AU-3 Requirement |
|:------|:------------|:-----------------|
| `date` | `yyyy-MM-dd HH:mm:ss` | ✅ When |
| `thread` | JVM thread name | ✅ Process ID |
| `user` | Authenticated user ID (via MDC) | ✅ Who |
| `X-Track` | Request correlation ID | ✅ What (request tracing) |
| `level` | DEBUG, INFO, WARN, ERROR | ✅ Severity |
| `logger` | Fully qualified class name | ✅ Source |
| `message` | Event description (newlines escaped) | ✅ What |

---

## 2. Auditable Events (AU-2)

### 2.1 Security Events

| Event | Logger / Component | Level | Trigger |
|:------|:-------------------|:------|:--------|
| Successful login | `AtrsAuthenticationSuccessHandler` | INFO | Valid credentials submitted |
| Failed login | `AtrsAuthenticationFailureHandler` | WARN | Invalid credentials |
| Logout | `AtrsLogoutSuccessHandler` | INFO | User logout |
| CSRF violation | Spring Security | ERROR | Invalid/missing CSRF token |
| Access denied | `DelegatingAccessDeniedHandler` | WARN | Unauthorized resource access |
| User ID tracking | `UserIdMDCPutFilter` | — | Every authenticated request (MDC) |

### 2.2 Application Events

| Event | Logger / Component | Level | Trigger |
|:------|:-------------------|:------|:--------|
| HTTP request/response | `AccessLogFilter` | INFO | Every HTTP request |
| Business exception | `ExceptionLogger` | ERROR | Business rule violation |
| Service entry/exit | `TraceLoggingInterceptor` | TRACE | Controller method invocation |
| Data access | `domain.repository.*` | TRACE | MyBatis SQL execution |
| Request mapping | `RequestMappingHandlerMapping` | TRACE | URL-to-controller resolution |
| JDBC operations | `JdbcTemplate` | TRACE | SQL statement execution |

### 2.3 Infrastructure Events

| Event | Source | Level | Trigger |
|:------|:-------|:------|:--------|
| Application startup/shutdown | Spring Framework | INFO | Container lifecycle |
| Connection pool events | DataSource | WARN/ERROR | Pool exhaustion, connection failures |
| JMS message processing | `ReservationHistoryReportListener` | INFO/ERROR | Message received/failed |
| JMS error handling | `AtrsJmsErrorHandler` | ERROR | Message processing failure |

---

## 3. Audit Processing and Protection (AU-4, AU-5, AU-9)

### 3.1 Log Integrity

| Control | Implementation |
|:--------|:---------------|
| Log file permissions | OS-level file permissions (644) |
| Log tampering detection | SIEM-based integrity monitoring |
| Centralized aggregation | Forward to write-once log store |
| Newline injection prevention | `%replace(%msg){'(\r\n|\r|\n)','$1  '}` in Logback pattern |

### 3.2 Audit Storage Capacity (AU-4)

| Environment | Storage | Retention | Overflow Handling |
|:------------|:--------|:----------|:------------------|
| Development | Local filesystem | 7 days rolling | Oldest logs overwritten |
| Production | SIEM + cold storage | 90 days online / 1 year archive | Alert on 80% capacity |

### 3.3 Response to Audit Processing Failures (AU-5)

- Logback `ConsoleAppender` provides fallback if file appender fails
- Monitoring log (`ExceptionLogger.Monitoring`) uses separate appender
- SIEM alerts on log ingestion gaps
- System continues operation if logging fails (fail-open for availability)

---

## 4. Audit Review and Reporting (AU-6, AU-7)

### 4.1 Review Schedule

| Activity | Frequency | Responsible |
|:---------|:----------|:------------|
| Automated alerting (ERROR events) | Real-time | SOC / SIEM |
| Security event review | Daily (automated) | SOC |
| Manual audit log review | Weekly | Security Team |
| Comprehensive audit analysis | Monthly | ISSO |
| Audit policy review | Annual | CISO |

### 4.2 Key Metrics to Monitor

| Metric | Threshold | Action |
|:-------|:----------|:-------|
| Failed login attempts per user | > 3 in 15 min | Trigger lockout + alert |
| Failed login attempts system-wide | > 50 in 5 min | Brute-force alert |
| CSRF violations | Any | Investigate immediately |
| Access denied events | > 10 per user/hour | Investigate privilege escalation |
| Business exceptions | > 100/hour | Application health check |
| JMS error handler invocations | Any | Check message broker health |

---

## 5. Time Synchronization (AU-8)

| Requirement | Implementation |
|:------------|:---------------|
| Clock source | NTP synchronized to authoritative source |
| Timestamp format | `yyyy-MM-dd HH:mm:ss` (ISO 8601 compatible) |
| Timezone | Server local time (should be UTC in production) |
| Accuracy | ± 1 second (NTP stratum 2 or better) |

---

## 6. Logger Configuration Detail

```xml
<!-- Security & Access Logging -->
<logger name="jp.co.ntt.atrs.app.common.logging.AccessLogFilter" level="info" />
<logger name="jp.co.ntt.atrs" level="debug" />
<logger name="jp.co.ntt.atrs.domain.repository" level="trace" />

<!-- Framework Logging -->
<logger name="org.terasoluna.gfw" level="debug" />
<logger name="org.terasoluna.gfw.web.logging.TraceLoggingInterceptor" level="trace" />

<!-- Monitoring (separate appender) -->
<logger name="org.terasoluna.gfw.common.exception.ExceptionLogger.Monitoring" 
        additivity="false" level="error">
    <appender-ref ref="MONITORING_LOG_FILE" />
</logger>

<!-- Spring Framework -->
<logger name="org.springframework" level="warn" />
<logger name="org.springframework.web.servlet" level="info" />
```

> **FedRAMP Production Hardening:** Set `jp.co.ntt.atrs` to `INFO` and disable `TRACE` on repositories to prevent sensitive data leakage in logs.

---

## 7. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| AU-1 | Policy & Procedures | ✅ | This document |
| AU-2 | Audit Events | ✅ | Section 2 |
| AU-3 | Content of Audit Records | ✅ | Section 1.3 |
| AU-4 | Audit Storage Capacity | ✅ | Section 3.2 |
| AU-5 | Response to Audit Failures | ✅ | Section 3.3 |
| AU-6 | Audit Review | ✅ | Section 4 |
| AU-7 | Audit Reduction & Report Generation | ✅ | SIEM-based |
| AU-8 | Time Stamps | ✅ | Section 5 |
| AU-9 | Protection of Audit Information | ✅ | Section 3.1 |
| AU-11 | Audit Record Retention | ⚠️ | 7 days local; SIEM needed |
| AU-12 | Audit Generation | ✅ | Logback + Spring filters |
