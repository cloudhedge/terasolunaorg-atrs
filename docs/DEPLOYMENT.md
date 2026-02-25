# ATRS — Deployment Guide

**Document ID:** ATRS-DEPLOY-001  
**FedRAMP Control Mapping:** SA-10, CM-3, CM-6  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Prerequisites

### 1.1 Software Requirements

| Software | Version | Purpose |
|:---------|:--------|:--------|
| Java JDK | 17 or 21 (LTS) | Application runtime & build |
| Apache Maven | 3.8+ | Build tool |
| PostgreSQL | 14+ | Database |
| Apache Artemis | Latest stable | JMS message broker |
| Git | 2.x+ | Source control |

### 1.2 System Requirements

| Resource | Development | Production |
|:---------|:------------|:-----------|
| CPU | 2 cores | 4+ cores per instance |
| Memory | 4 GB | 8+ GB per instance |
| Disk | 10 GB | 100+ GB (encrypted) |
| Network | Local | Private subnet with TLS |

---

## 2. Select Configuration Variant

Choose **one** variant for deployment:

| Variant | Directory | Configuration | View |
|:--------|:----------|:-------------|:-----|
| XMLConfig-JSP | `XMLConfig-JSP/atrs/` | Spring XML | JSP |
| XMLConfig-Thymeleaf | `XMLConfig-Thymeleaf/atrs/` | Spring XML | Thymeleaf |
| JavaConfig-JSP | `JavaConfig-JSP/atrs/` | Java `@Configuration` | JSP |
| JavaConfig-Thymeleaf | `JavaConfig-Thymeleaf/atrs/` | Java `@Configuration` | Thymeleaf |

> **FedRAMP:** Lock to a single variant and document in CM baseline.

---

## 3. Database Setup

### 3.1 Create Database

```sql
CREATE DATABASE atrs;
CREATE USER atrs_svc WITH ENCRYPTED PASSWORD '<strong-password>';
GRANT ALL PRIVILEGES ON DATABASE atrs TO atrs_svc;
```

### 3.2 Initialize Schema and Data

```bash
cd <variant>/atrs
mvn sql:execute -f atrs-initdb/pom.xml
```

This executes scripts in order:
1. `00000_drop_all_tables.sql` — Drop existing tables (⚠️ destructive)
2. `00100_create_all_tables.sql` — Create schema with constraints
3. `00200_insert_fixed_value.sql` — Reference data
4. `00210_insert_route.sql` — Routes
5. `00220_insert_flight_master.sql` — Flight masters
6. `00230_insert_member.sql` — Test members (⚠️ development only)
7. `00240_insert_peak_time.sql` — Peak time pricing
8. `00250_insert_flight.sql` — Flight availability

> **FedRAMP Production:** Do NOT execute `00230_insert_member.sql` in production (contains test accounts with known credentials).

### 3.3 Production Database Configuration

Edit `atrs-env/src/main/resources/META-INF/spring/atrs-infra.properties`:

```properties
# Use TLS connection
database.url=jdbc:postgresql://<db-host>:5432/atrs?sslmode=verify-full&sslrootcert=/path/to/ca.crt
database.username=atrs_svc
database.password=<from-secrets-manager>
database.driverClassName=org.postgresql.Driver

# Connection pool tuning
cp.maxActive=96
cp.maxIdle=16
cp.minIdle=4
cp.maxWait=60000

# JMS (internal network only)
jms.mq.host=<artemis-host>
jms.mq.port=61616

# Report directory (encrypted filesystem)
report.dir=/atrs/reports/reservation
```

> **FedRAMP:** Externalize `database.password` and JMS credentials to a secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.).

---

## 4. Build

```bash
cd <variant>/atrs

# Full clean build
mvn clean install

# Build with dependency vulnerability check
mvn clean install org.owasp:dependency-check-maven:check

# Generate SBOM
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom
```

Output: `atrs-web/target/atrs.war`

---

## 5. Development Deployment

```bash
# Start embedded Tomcat via Cargo
mvn cargo:run -pl atrs-web
```

Access: http://localhost:8080/atrs/

---

## 6. Production Deployment

### 6.1 Tomcat Configuration

1. Copy `atrs.war` to Tomcat `webapps/` directory
2. Place environment configuration in Tomcat's `conf/Catalina/localhost/atrs.xml`:

```xml
<!-- From atrs-env/configs/tomcat10-postgresql/ContainerConfigXML/atrs.xml -->
<Context>
    <Resource name="jdbc/atrsDataSource"
              type="javax.sql.DataSource"
              driverClassName="org.postgresql.Driver"
              url="jdbc:postgresql://<host>:5432/atrs?sslmode=verify-full"
              username="atrs_svc"
              password="<from-secrets-manager>"
              maxTotal="96"
              maxIdle="16"
              minIdle="4"
              maxWaitMillis="60000" />
</Context>
```

### 6.2 TLS Configuration

Configure Tomcat's `server.xml` for HTTPS:

```xml
<Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
           maxThreads="200"
           SSLEnabled="true"
           scheme="https"
           secure="true">
    <SSLHostConfig protocols="TLSv1.2+TLSv1.3"
                   ciphers="TLS_AES_256_GCM_SHA384,TLS_CHACHA20_POLY1305_SHA256">
        <Certificate certificateKeystoreFile="/path/to/keystore.p12"
                     certificateKeystorePassword="<keystore-password>"
                     type="RSA" />
    </SSLHostConfig>
</Connector>
```

### 6.3 Logging Configuration

For production, update `logback.xml`:
- Set `jp.co.ntt.atrs` to `INFO` (not `DEBUG`)
- Set `jp.co.ntt.atrs.domain.repository` to `INFO` (not `TRACE`)
- Add syslog appender for SIEM forwarding
- Ensure `atrs-monitoring.log` alerts are forwarded

### 6.4 JMS Broker Setup

1. Install and configure Apache Artemis
2. Create required queues for reservation history reports
3. Configure TLS between Tomcat and Artemis
4. Create dedicated broker credentials

---

## 7. Verification Checklist

### 7.1 Functional Verification

- [ ] Home page loads at `/atrs/`
- [ ] Flight search returns results
- [ ] Member registration creates account
- [ ] Login with new member succeeds
- [ ] Ticket reservation completes
- [ ] Member profile update works
- [ ] Reservation history report generates
- [ ] Logout invalidates session

### 7.2 Security Verification

- [ ] TLS terminates correctly (no plain HTTP)
- [ ] CSRF tokens present in all forms
- [ ] Login failure logs correctly
- [ ] Session invalidated on logout
- [ ] Protected pages require authentication
- [ ] Database credentials not in WAR file
- [ ] Test member accounts NOT in production DB
- [ ] Trace-level logging disabled in production
- [ ] Application logs forwarding to SIEM
- [ ] Monitoring log capturing ERROR events

---

## 8. Rollback Procedure

1. Stop Tomcat instance
2. Replace `atrs.war` with previous version from artifact repository
3. Restore database from pre-deployment backup (if schema changed)
4. Restart Tomcat
5. Verify functionality per Section 7
6. Document rollback in change management system
