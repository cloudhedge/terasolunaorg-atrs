# ATRS — Privacy Impact Assessment (PIA)

**Document ID:** ATRS-PIA-001  
**FedRAMP Control Families:** AP, AR, DI, DM, IP, SE, TR, UL  
**Version:** 1.0 | **Date:** 2026-02-24

---

## 1. System Description

The Airline Ticket Reservation System (ATRS) collects, processes, and stores Personally Identifiable Information (PII) and Payment Card Industry (PCI) Cardholder Data (CHD) for the purpose of airline flight search, ticket reservation, and member account management.

---

## 2. PII Inventory

### 2.1 Data Elements Collected

| Data Element | Source | Table.Column | Classification | Required |
|:-------------|:-------|:-------------|:---------------|:---------|
| Family Name (Kanji) | Member registration | `MEMBER.KANJI_FAMILY_NAME` | PII | Yes |
| Given Name (Kanji) | Member registration | `MEMBER.KANJI_GIVEN_NAME` | PII | Yes |
| Family Name (Kana) | Member registration | `MEMBER.KANA_FAMILY_NAME` | PII | Yes |
| Given Name (Kana) | Member registration | `MEMBER.KANA_GIVEN_NAME` | PII | Yes |
| Date of Birth | Member registration | `MEMBER.BIRTHDAY` | PII | Yes |
| Gender | Member registration | `MEMBER.GENDER` | PII | Yes |
| Phone Number | Member registration | `MEMBER.TEL` | PII | Yes |
| ZIP Code | Member registration | `MEMBER.ZIP_CODE` | PII | Yes |
| Address | Member registration | `MEMBER.ADDRESS` | PII | Yes |
| Email Address | Member registration | `MEMBER.MAIL` | PII | Yes |
| Credit Card Number | Member registration | `MEMBER.CREDIT_NO` | PCI CHD | Yes |
| Credit Card Type | Member registration | `MEMBER.CREDIT_TYPE_CD` | PCI Metadata | Yes |
| Credit Card Expiry | Member registration | `MEMBER.CREDIT_TERM` | PCI CHD | Yes |
| Password | Member registration | `MEMBER_LOGIN.PASSWORD` | Credential | Yes |
| Passenger Name | Reservation | `PASSENGER.FAMILY_NAME`, `PASSENGER.GIVEN_NAME` | PII | Yes |
| Passenger Age | Reservation | `PASSENGER.AGE` | PII | Yes |
| Passenger Gender | Reservation | `PASSENGER.GENDER` | PII | Yes |
| Representative Name | Reservation | `RESERVATION.REP_FAMILY_NAME`, `REP_GIVEN_NAME` | PII | Yes |
| Representative Phone | Reservation | `RESERVATION.REP_TEL` | PII | Yes |
| Representative Email | Reservation | `RESERVATION.REP_MAIL` | PII | Yes |
| Representative Age | Reservation | `RESERVATION.REP_AGE` | PII | Yes |

### 2.2 Data Volume Estimate

| Entity | Estimated Records | Growth Rate |
|:-------|:-----------------|:-----------|
| Members | Variable | Per registration |
| Reservations | Variable | Per booking |
| Passengers | Variable (multiple per reservation) | Per booking |

---

## 3. Purpose and Use of PII

### 3.1 Purpose Specification (AP-2)

| Purpose | Data Used | Legal Basis |
|:--------|:----------|:------------|
| Member account management | All member PII | User consent at registration |
| Flight reservation processing | Passenger PII, contact info | Contractual necessity |
| Payment processing | Credit card data | Contractual necessity |
| Authentication | Password, membership number | System security |
| Reservation history reporting | Reservation + passenger data | User-requested service |
| Contacting representative | Rep name, phone, email | Operational necessity |

### 3.2 Use Limitation (UL-1)

PII is used **only** for the purposes specified above. Data is not:
- Sold to third parties
- Used for marketing without explicit consent
- Shared with external parties except as required by law
- Used for automated decision-making or profiling

---

## 4. Data Minimization (DM-1, DM-2)

### 4.1 Collection Minimization

| Field | Necessity Assessment |
|:------|:--------------------|
| Full name (Kanji + Kana) | Required for airline boarding |
| Date of birth | Required for age-based fare types |
| Gender | Required for passenger manifest |
| Phone number | Required for emergency contact |
| Address + ZIP | Required for member correspondence |
| Email | Required for booking confirmation |
| Credit card data | Required for payment processing |

### 4.2 Retention Schedule (DM-2)

| Data Category | Retention Period | Disposal Method |
|:-------------|:----------------|:----------------|
| Active member data | Duration of membership | N/A (active) |
| Inactive member data | 3 years after last login | Secure deletion |
| Reservation records | 7 years (regulatory) | Secure deletion |
| Passenger records | Same as reservation | Secure deletion |
| Password hashes | Until changed/account deleted | Overwritten |
| Application logs (with user ID) | 90 days online, 1 year archive | Secure deletion |
| Report files | 90 days | Secure deletion |

---

## 5. Privacy Protections

### 5.1 Data Protection Controls

| Control | Implementation |
|:--------|:---------------|
| Encryption in transit | TLS 1.2+ for all communications |
| Encryption at rest | Database TDE or filesystem encryption |
| Password protection | One-way hash (PBKDF2, 310K iterations) |
| Access control | RBAC — members access only own data |
| Audit logging | All data access logged with user ID and X-Track |
| Input validation | Bean Validation prevents malformed PII injection |
| Output encoding | XSS prevention in displayed PII |
| Credit card masking | Display only last 4 digits in UI (recommended) |

### 5.2 PCI DSS Considerations

| Requirement | ATRS Status | Notes |
|:------------|:-----------|:------|
| Encrypt CHD at rest | ⚠️ POA&M | `MEMBER.CREDIT_NO` stored in clear text — requires encryption or tokenization |
| Mask PAN in display | ⚠️ POA&M | UI should display only last 4 digits |
| Restrict CHD access | ✅ | Only authenticated member + authorized services |
| Log CHD access | ✅ | Repository-level logging |
| Secure transmission | ✅ | TLS required |

---

## 6. Individual Rights (IP-1 through IP-4)

| Right | Implementation |
|:------|:---------------|
| **Access** | Members can view own profile via `/member/update` |
| **Correction** | Members can update own profile data |
| **Deletion** | Account deletion available via administrative request |
| **Consent** | Registration constitutes consent; terms displayed |
| **Notification** | Privacy notice displayed during registration |

---

## 7. Data Quality (DI-1, DI-2)

| Control | Implementation |
|:--------|:---------------|
| Input validation | Multi-layer validation (client, controller, service) |
| Format enforcement | Custom validators (`@FullWidth`, `@HalfWidthNumber`, etc.) |
| Referential integrity | Foreign key constraints in database |
| Data freshness | `LOGIN_DATE_TIME` tracks last access |

---

## 8. Accountability and Transparency (AR-1, TR-1)

| Requirement | Implementation |
|:------------|:---------------|
| Privacy policy | Published on system and available before registration |
| Data use transparency | Purposes documented in this PIA |
| Processing records | Audit logs with user ID for all data operations |
| Breach notification | Per Incident Response Plan and applicable regulations |
| Privacy training | Annual training for all personnel handling PII |

---

## 9. Privacy Impact Summary

| Factor | Assessment |
|:-------|:-----------|
| **PII Sensitivity** | High (includes financial data, DOB, address) |
| **Volume** | Medium (member and passenger records) |
| **Accessibility** | Limited (RBAC, member access to own data only) |
| **Risk of Harm** | High (identity theft, financial fraud if breached) |
| **Mitigations** | Encryption, access control, audit logging, input validation |
| **Residual Risk** | Medium (PCI data encryption POA&M outstanding) |

---

## 10. FedRAMP Control Traceability

| Control ID | Control Name | Status | Implementation |
|:-----------|:-------------|:-------|:---------------|
| AP-1 | Authority to Collect | ✅ | User consent at registration |
| AP-2 | Purpose Specification | ✅ | Section 3 |
| AR-1 | Governance & Privacy Program | ✅ | Section 8 |
| DI-1 | Data Quality | ✅ | Section 7 |
| DM-1 | Minimization of PII Collection | ✅ | Section 4.1 |
| DM-2 | Data Retention & Disposal | ✅ | Section 4.2 |
| IP-1 | Consent | ✅ | Section 6 |
| IP-2 | Individual Access | ✅ | Section 6 |
| IP-3 | Redress | ✅ | Administrative process |
| SE-1 | Inventory of PII | ✅ | Section 2 |
| TR-1 | Privacy Notice | ✅ | Section 8 |
| UL-1 | Internal Use | ✅ | Section 3.2 |
