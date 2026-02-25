# ATRS — Supply Chain Risk Management

**Document ID:** ATRS-SR-001  
**FedRAMP Control Family:** Supply Chain Risk Management (SR)  
**NIST SP 800-53 Rev. 5 Controls:** SR-1 through SR-12  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. Supply Chain Risk Management Policy (SR-1)

ATRS manages supply chain risk through dependency management, provenance tracking, and continuous vulnerability monitoring of all third-party components in the software stack.

---

## 2. Dependency Inventory (SR-2, SR-4)

### 2.1 Direct Dependencies

| Component | Provider | Source | Provenance |
|:----------|:---------|:-------|:-----------|
| TERASOLUNA GFW 5.10.0 | NTT DATA / TERASOLUNA | Maven Central | Open-source, Apache 2.0 |
| Spring Framework 6.x | VMware / Pivotal | Maven Central | Open-source, Apache 2.0 |
| Spring Security 6.x | VMware / Pivotal | Maven Central | Open-source, Apache 2.0 |
| PostgreSQL JDBC 42.7.4 | PostgreSQL Global Dev Group | Maven Central | Open-source, BSD-2 |
| MapStruct | MapStruct Authors | Maven Central | Open-source, Apache 2.0 |
| Apache Artemis Client | Apache Software Foundation | Maven Central | Open-source, Apache 2.0 |
| Logback | QOS.ch | Maven Central | Open-source, EPL 1.0 / LGPL 2.1 |
| SLF4J | QOS.ch | Maven Central | Open-source, MIT |

### 2.2 Build-Time Dependencies

| Component | Provider | Purpose |
|:----------|:---------|:--------|
| Apache Maven 3.x | Apache Software Foundation | Build system |
| Maven Compiler Plugin | Apache Software Foundation | Java compilation |
| Maven WAR Plugin 3.4.0 | Apache Software Foundation | WAR packaging |
| Cargo Maven Plugin | Codehaus | Deployment (development) |
| Maven Surefire 3.5.2 | Apache Software Foundation | Unit testing |
| Maven Failsafe 3.5.2 | Apache Software Foundation | Integration testing |

### 2.3 Runtime Infrastructure

| Component | Provider | License |
|:----------|:---------|:--------|
| OpenJDK 17/21 | Oracle / Adoptium / Red Hat | GPL v2 + Classpath Exception |
| Apache Tomcat 10.x | Apache Software Foundation | Apache 2.0 |
| PostgreSQL 14+ | PostgreSQL Global Dev Group | PostgreSQL License (BSD-like) |
| Apache Artemis | Apache Software Foundation | Apache 2.0 |
| Linux OS | Various (RHEL, Ubuntu, etc.) | GPL v2 / Various |

---

## 3. SBOM Management (SR-4)

### 3.1 SBOM Generation

```bash
# CycloneDX format (recommended for FedRAMP)
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom

# SPDX format (alternative)
mvn org.spdx:spdx-maven-plugin:createSPDX

# Dependency tree (human-readable)
mvn dependency:tree > dependency-tree.txt
```

### 3.2 SBOM Review Process

| Activity | Frequency | Trigger | Owner |
|:---------|:----------|:--------|:------|
| Full SBOM generation | Every release | Release pipeline | Build team |
| Vulnerability scan against SBOM | Every build | CI/CD pipeline | Security team |
| License compliance check | Every release | Release pipeline | Legal/compliance |
| SBOM diff review (changes) | Every release | Release pipeline | Application team |
| SBOM submission to FedRAMP | Annual | Authorization renewal | ISSO |

---

## 4. Vulnerability Management (SR-6)

### 4.1 Dependency Vulnerability Scanning

```bash
# OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# Output: target/dependency-check-report.html
```

### 4.2 Vulnerability Response SLA

| CVSS Score | Severity | Remediation SLA |
|:-----------|:---------|:----------------|
| 9.0 – 10.0 | Critical | 14 days |
| 7.0 – 8.9 | High | 30 days |
| 4.0 – 6.9 | Medium | 90 days |
| 0.1 – 3.9 | Low | Next scheduled release |

### 4.3 Remediation Strategies

| Strategy | When Used |
|:---------|:----------|
| **Upgrade** | Patched version available | 
| **Patch** | Direct fix for vulnerability |
| **Workaround** | No patch available; compensating control |
| **Accept** | Low risk; documented risk acceptance |
| **Remove** | Vulnerable dependency not needed |

---

## 5. Provenance Verification (SR-3)

### 5.1 Artifact Integrity

| Verification | Mechanism |
|:-------------|:----------|
| Maven Central artifacts | SHA-256 checksum + GPG signature verification |
| Build reproducibility | Locked dependency versions in POM |
| Source code integrity | Git commit signing (GPG) |
| Build artifact integrity | WAR checksum generation and verification |

### 5.2 Repository Trust

| Repository | Trust Level | Verification |
|:-----------|:-----------|:-------------|
| Maven Central | Trusted | Checksums + GPG signatures |
| Sonatype Snapshots | Development only | Not for production |
| Internal Nexus/Artifactory | Trusted | Proxied + cached from Central |

---

## 6. Counterfeit Component Prevention (SR-5, SR-11)

| Control | Implementation |
|:--------|:---------------|
| Lock all dependency versions | `<dependencyManagement>` in parent POM |
| Verify checksums on download | Maven default behavior |
| No wildcard version ranges | All versions explicitly specified |
| Snapshot exclusion in production | Build profile configuration |
| Repository allowlisting | Only approved repositories in settings.xml |

---

## 7. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| SR-1 | Policy & Procedures | ✅ | This document |
| SR-2 | Supply Chain Risk Assessment | ✅ | Section 2 |
| SR-3 | Supply Chain Controls & Processes | ✅ | Section 5 |
| SR-4 | Provenance | ✅ | Sections 3, 5 |
| SR-5 | Acquisition Strategies | ✅ | Section 6 |
| SR-6 | Supplier Assessments & Reviews | ✅ | Section 4 |
| SR-11 | Component Authenticity | ✅ | Section 6 |
