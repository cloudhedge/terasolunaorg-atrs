# ATRS — Configuration Management

**Document ID:** ATRS-CM-001  
**FedRAMP Control Family:** Configuration Management (CM)  
**NIST SP 800-53 Rev. 5 Controls:** CM-1 through CM-11  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Baseline Configuration (CM-2)

### 1.1 Application Baseline

| Component | Version | Lock Mechanism |
|:----------|:--------|:---------------|
| ATRS Application | 1.11.0.RELEASE | Maven `<version>` in parent POM |
| TERASOLUNA GFW Parent | 5.10.0.RELEASE | Maven `<parent>` POM |
| Java Runtime | 17 (LTS) | `<java-version>17</java-version>` in properties |
| PostgreSQL Driver | 42.7.4 | `<postgresql.version>` in properties |
| Character Encoding | UTF-8 | `<encoding>UTF-8</encoding>` |

### 1.2 Database Baseline

Schema baseline established by versioned SQL scripts in `atrs-initdb/src/sqls/`:

| Script | Purpose |
|:-------|:--------|
| `00000_drop_all_tables.sql` | Clean slate (development/test only) |
| `00100_create_all_tables.sql` | Complete DDL with constraints and indexes |
| `00200_insert_fixed_value.sql` | Reference data (airports, fare types, boarding classes) |
| `00210_insert_route.sql` | Route definitions |
| `00220_insert_flight_master.sql` | Flight master data |
| `00230_insert_member.sql` | Test member accounts |
| `00240_insert_peak_time.sql` | Peak time pricing rules |
| `00250_insert_flight.sql` | Flight availability data |

### 1.3 Dependency Management

All transitive dependency versions are managed through the TERASOLUNA GFW parent POM BOM (Bill of Materials). Direct overrides:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>jp.co.ntt.atrs</groupId>
            <artifactId>atrs-env</artifactId>
            <version>${project.version}</version>
        </dependency>
        <dependency>
            <groupId>jp.co.ntt.atrs</groupId>
            <artifactId>atrs-domain</artifactId>
            <version>${project.version}</version>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <version>${postgresql.version}</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

---

## 2. Configuration Change Control (CM-3)

### 2.1 Change Control Process

```
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐
│ Request   │───▶│ Review    │───▶│ Approve   │───▶│ Implement│───▶│ Verify   │
│ (Ticket)  │    │ (Tech +   │    │ (CCB/ISSO)│    │ (Dev)    │    │ (QA +    │
│           │    │  Security)│    │           │    │          │    │  SecOps) │
└──────────┘    └───────────┘    └───────────┘    └──────────┘    └──────────┘
```

| Step | Activity | Artifacts |
|:-----|:---------|:----------|
| **Request** | Submit change request with impact analysis | Change ticket, risk assessment |
| **Review** | Technical and security review | Review notes, security checklist |
| **Approve** | Configuration Control Board approval | Approval record |
| **Implement** | Code change via Git branch → PR → merge | Git commit, PR review |
| **Verify** | Automated tests + security scan + manual review | Test results, scan report |
| **Deploy** | Release to staging → production | Deployment log, rollback plan |

### 2.2 Git Branching Strategy

| Branch | Purpose | Protection |
|:-------|:--------|:-----------|
| `main` | Production-ready code | Merge requires PR + 2 approvals |
| `develop` | Integration branch | Merge requires PR + 1 approval |
| `feature/*` | Feature development | No direct push to main |
| `hotfix/*` | Emergency fixes | Fast-track approval process |
| `release/*` | Release candidates | Tagged and signed |

---

## 3. Security Impact Analysis (CM-4)

All configuration changes must include a security impact analysis:

| Question | Required Response |
|:---------|:-----------------|
| Does this change modify authentication or authorization? | Yes/No + details |
| Does this change affect data handling (PII, PCI)? | Yes/No + details |
| Does this change modify network boundaries or interfaces? | Yes/No + details |
| Does this change introduce new dependencies? | Yes/No + CVE check |
| Does this change modify logging or audit capabilities? | Yes/No + details |
| Does this change affect CSRF, session, or crypto settings? | Yes/No + details |

---

## 4. Least Functionality (CM-7)

### 4.1 Disabled / Removed Functionality

| Feature | Status | Rationale |
|:--------|:-------|:----------|
| JSP debug mode | Disabled in production | Prevents information disclosure |
| Trace-level logging on repositories | Disabled in production | Prevents data leakage |
| Static resource security context | Removed (`security="none"`) | Performance optimization (no auth needed) |
| CSRF on stateless API | Disabled | Not applicable to stateless sessions |
| Development test data scripts | Not deployed to production | Prevents default credential exposure |

### 4.2 Required Services Only

| Service | Required | Port | Justification |
|:--------|:---------|:-----|:-------------|
| Tomcat HTTP/HTTPS | Yes | 8080/8443 | Application serving |
| PostgreSQL | Yes | 5432 | Data persistence |
| Apache Artemis | Yes | 61616 | Async report generation |
| SSH | Management only | 22 | Administrative access |
| All others | No | — | Disabled |

---

## 5. Configuration Settings (CM-6)

### 5.1 Application Properties

| Property | File | Default | Production Requirement |
|:---------|:-----|:--------|:----------------------|
| `database.url` | `atrs-infra.properties` | `jdbc:postgresql://localhost:5432/atrs` | Use TLS: `?sslmode=verify-full` |
| `database.username` | `atrs-infra.properties` | `postgres` | Dedicated service account |
| `database.password` | `atrs-infra.properties` | `postgres` | Externalized to secrets manager |
| `cp.maxActive` | `atrs-infra.properties` | `96` | Tuned per capacity plan |
| `cp.maxIdle` | `atrs-infra.properties` | `16` | Tuned per capacity plan |
| `cp.maxWait` | `atrs-infra.properties` | `60000` (ms) | Review for DoS protection |
| `jms.mq.host` | `atrs-infra.properties` | `localhost` | Internal network only |
| `jms.mq.port` | `atrs-infra.properties` | `61616` | Firewall-restricted |
| `report.dir` | `atrs-infra.properties` | `/atrs/reports/reservation` | Encrypted filesystem |

### 5.2 Spring Security Settings

| Setting | Configuration | Value |
|:--------|:-------------|:------|
| CSRF Protection | `spring-security.xml` | Enabled (web), Disabled (API) |
| Session Creation | `spring-security.xml` | Stateful (web), Stateless (API) |
| Password Encoder | `applicationContext.xml` | PBKDF2 (default) + BCrypt (legacy) |
| Login URL | `spring-security.xml` | `/auth/login` |
| Logout URL | `spring-security.xml` | `/auth/dologout` |
| Session Invalidation | `spring-security.xml` | `invalidate-session="true"` |
| Cookie Deletion | `spring-security.xml` | `delete-cookies="JSESSIONID"` |

---

## 6. Software Bill of Materials (CM-8)

### 6.1 SBOM Generation

Generate CycloneDX SBOM:
```bash
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom
```

### 6.2 Direct Dependencies

| Artifact | Group | Version | License | CVE Status |
|:---------|:------|:--------|:--------|:-----------|
| terasoluna-gfw-parent | org.terasoluna.gfw | 5.10.0.RELEASE | Apache 2.0 | Review required |
| postgresql | org.postgresql | 42.7.4 | BSD-2 | Review required |
| mapstruct | org.mapstruct | Managed | Apache 2.0 | Review required |
| artemis-jakarta-client | org.apache.activemq | Managed | Apache 2.0 | Review required |
| slf4j-api | org.slf4j | Managed | MIT | Review required |

> **FedRAMP Requirement:** Full SBOM with transitive dependencies must be submitted as part of the authorization package. Run `mvn dependency:tree` and vulnerability scan before each release.

---

## 7. Build Reproducibility (CM-3, SA-10)

### 7.1 Build Commands

```bash
# Clean build
mvn clean install

# Run application (development)
mvn cargo:run -pl atrs-web

# Initialize database
mvn sql:execute -f atrs-initdb/pom.xml

# Generate SBOM
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom

# Dependency vulnerability check
mvn org.owasp:dependency-check-maven:check
```

### 7.2 Build Artifact Integrity

| Control | Mechanism |
|:--------|:----------|
| Source integrity | Git commit signing (GPG) |
| Build integrity | Maven checksum verification for dependencies |
| Artifact signing | JAR/WAR signing with organizational certificate |
| Artifact storage | Signed artifacts in secure artifact repository |

---

## 8. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| CM-1 | Policy & Procedures | ✅ | This document |
| CM-2 | Baseline Configuration | ✅ | Section 1 |
| CM-3 | Configuration Change Control | ✅ | Section 2 |
| CM-4 | Security Impact Analysis | ✅ | Section 3 |
| CM-5 | Access Restrictions for Change | ✅ | Git branch protection |
| CM-6 | Configuration Settings | ✅ | Section 5 |
| CM-7 | Least Functionality | ✅ | Section 4 |
| CM-8 | Information System Component Inventory | ✅ | Section 6 |
| CM-10 | Software Usage Restrictions | ✅ | Apache 2.0 / BSD licenses |
| CM-11 | User-Installed Software | ✅ | No user-installable components |
