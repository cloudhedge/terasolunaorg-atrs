# JavaConfig-JSP/atrs - Architecture Design Document

## Executive Summary

**Airline Ticket Reservation System (ATRS)** - A Java Spring-based web application for booking airline tickets, managing memberships, and generating reservation reports.

| Attribute | Value |
|-----------|-------|
| **Type** | Monolithic Web Application |
| **Stack** | Java 17, Spring MVC, MyBatis, PostgreSQL, JSP |
| **Framework** | TERASOLUNA Framework 5.10.0 |
| **Architecture** | 3-Tier Layered (Web → Domain → Infrastructure) |

---

## 1. Module Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        JavaConfig-JSP/atrs                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   atrs-web   │  │ atrs-domain  │  │   atrs-env   │           │
│  │ Controllers  │──│   Services   │──│   Config     │           │
│  │ REST APIs    │  │   Entities   │  │  DataSource  │           │
│  │ JSP Views    │  │ Repositories │  │     JMS      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      atrs-initdb                          │   │
│  │               SQL Scripts (DDL + DML)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

| Module | Purpose | Key Dependencies |
|--------|---------|------------------|
| **atrs-web** | Controllers, REST APIs, Views, Security | Spring MVC, Spring Security |
| **atrs-domain** | Business logic, Entities, Repositories | MyBatis, MapStruct |
| **atrs-env** | Environment config (DataSource, JMS) | DBCP2, ActiveMQ Artemis |
| **atrs-initdb** | Database initialization scripts | sql-maven-plugin |

---

## 2. High-Level Architecture

```mermaid
flowchart TB
    subgraph Client
        Browser[Web Browser]
    end
    
    subgraph "atrs-web"
        subgraph Controllers
            A1[AuthLoginController]
            B1[TicketSearchController]
            B2[TicketReserveController]
            C1[MemberRegisterController]
            C2[MemberUpdateController]
            D1[ReportController]
        end
        subgraph REST
            API[REST APIs<br>/api/flights, /api/member]
        end
        subgraph Views
            JSP[JSP Views<br>login, search, reserve, register]
        end
    end
    
    subgraph "atrs-domain"
        subgraph Services
            SVC1[TicketSearchService]
            SVC2[TicketReserveService]
            SVC3[MemberRegisterService]
            SVC4[AuthLoginService]
        end
        subgraph Entities
            ENT[Flight, Member, Reservation<br>Route, FareType, Airport]
        end
        subgraph Repositories
            REPO[FlightRepository<br>MemberRepository<br>ReservationRepository]
        end
    end
    
    subgraph "atrs-env"
        DS[(DataSource<br>PostgreSQL)]
        JMS[(ActiveMQ<br>Artemis)]
    end
    
    Browser --> Controllers
    Browser --> API
    Controllers --> JSP
    Controllers --> Services
    API --> Services
    Services --> ENT
    Services --> REPO
    REPO --> DS
    Services --> JMS
```

---

## 3. Database Schema (ER Diagram)

```mermaid
erDiagram
    MEMBER ||--|| MEMBER_LOGIN : has
    MEMBER ||--o{ RESERVATION : makes
    MEMBER }o--|| CREDIT_TYPE : uses
    
    RESERVATION ||--|{ RESERVE_FLIGHT : contains
    RESERVE_FLIGHT ||--|{ PASSENGER : has
    RESERVE_FLIGHT }|--|| FLIGHT : books
    
    FLIGHT }|--|| FLIGHT_MASTER : "based on"
    FLIGHT }|--|| BOARDING_CLASS : "has class"
    FLIGHT }|--|| FARE_TYPE : "has fare"
    
    FLIGHT_MASTER }|--|| ROUTE : "flies"
    FLIGHT_MASTER }|--|| PLANE : "uses"
    
    ROUTE }|--|| AIRPORT : "departs from"
    ROUTE }|--|| AIRPORT : "arrives at"
    
    PEAK_TIME ||--o{ FLIGHT : "adjusts price"

    MEMBER {
        varchar customer_no PK "会員番号"
        varchar kanji_family_name "姓(漢字)"
        varchar kanji_given_name "名(漢字)"
        date birthday "生年月日"
        char gender "性別 M/F"
        varchar mail "メール"
        varchar credit_no "クレカ番号"
        char credit_type_cd FK "クレカ種別"
    }
    
    MEMBER_LOGIN {
        varchar customer_no PK,FK
        varchar password "パスワード"
        varchar last_password "前回PW"
        timestamp login_date_time "ログイン日時"
        boolean login_flg "ログイン中"
    }
    
    FLIGHT {
        date departure_date PK "出発日"
        varchar flight_name PK,FK "便名"
        char boarding_class_cd PK,FK "搭乗クラス"
        char fare_type_cd PK,FK "運賃種別"
        int vacant_num "空席数"
    }
    
    FLIGHT_MASTER {
        varchar flight_name PK "便名"
        int route_no FK "区間番号"
        time departure_time "出発時刻"
        time arrival_time "到着時刻"
        varchar craft_type FK "機種"
    }
    
    ROUTE {
        int route_no PK "区間番号"
        char dep_airport_cd FK "出発空港"
        char arr_airport_cd FK "到着空港"
        int basic_fare "基本運賃"
    }
    
    RESERVATION {
        int reserve_no PK "予約番号"
        date reserve_date "予約日"
        int total_fare "総運賃"
        varchar rep_family_name "代表者姓"
        varchar rep_tel "電話番号"
        varchar rep_mail "メール"
        varchar customer_no FK "会員番号(optional)"
    }
    
    RESERVE_FLIGHT {
        int reserve_flight_no PK "予約便番号"
        int reserve_no FK "予約番号"
        date departure_date "出発日"
        varchar flight_name "便名"
        char boarding_class_cd "搭乗クラス"
        char fare_type_cd "運賃種別"
    }
    
    PASSENGER {
        int passenger_no PK "搭乗者番号"
        int reserve_flight_no FK "予約便番号"
        varchar family_name "姓"
        varchar given_name "名"
        int age "年齢"
        char gender "性別"
    }
    
    AIRPORT {
        char airport_cd PK "空港コード"
        varchar airport_name "空港名"
        int display_order "表示順"
    }
    
    PLANE {
        varchar craft_type PK "機種"
        int n_seat_num "普通席数"
        int s_seat_num "特別席数"
    }
    
    FARE_TYPE {
        char fare_type_cd PK "運賃種別コード"
        varchar fare_type_name "運賃種別名"
        int discount_rate "割引率"
        int rsrv_available_start_day_num "予約可能開始日数"
        int rsrv_available_end_day_num "予約可能終了日数"
        int passenger_min_num "最小人数"
    }
    
    BOARDING_CLASS {
        char boarding_class_cd PK "N/S"
        varchar boarding_class_name "クラス名"
        int extra_charge "追加料金"
    }
    
    PEAK_TIME {
        char peak_time_cd PK "繁忙期コード"
        date peak_start_date PK "開始日"
        date peak_end_date PK "終了日"
        int multiplication_ratio "倍率"
    }
    
    CREDIT_TYPE {
        char credit_type_cd PK "クレカ種別"
        varchar credit_firm "クレカ会社"
    }
```

---

## 4. Service Layer Architecture

```mermaid
flowchart LR
    subgraph "Feature Packages"
        subgraph "a0-a2: Authentication"
            A0[MembershipSharedService]
            A1[AuthLoginService]
            A2[AuthLogoutService]
        end
        
        subgraph "b0-b2: Ticket"
            B0[TicketSharedService]
            B1[TicketSearchService]
            B2[TicketReserveService]
        end
        
        subgraph "c0-c2: Member"
            C0[MemberErrorCode]
            C1[MemberRegisterService]
            C2[MemberUpdateService]
        end
        
        subgraph "d1: Report"
            D1[ReservationHistoryReportService]
        end
    end
    
    B1 --> B0
    B2 --> B0
    A1 --> A0
    C1 --> A0
    C2 --> A0
```

### Service Methods Summary

| Service | Methods |
|---------|---------|
| **TicketSearchService** | `searchFlight(criteria)` → List&lt;FlightVacantInfoDto&gt; |
| **TicketReserveService** | `calculateTotalFare()`, `validateReservation()`, `registerReservation()` |
| **TicketSharedService** | `getSearchLimitDate()`, `validateFlightList()`, `calculateBasicFare()`, `calculateFare()` |
| **MemberRegisterService** | `register(member)` → Member with generated ID |
| **MemberUpdateService** | `findMember()`, `updateMember()`, `checkMemberPassword()` |
| **AuthLoginService** | `login(member)` - updates login status |
| **ReservationHistoryReportService** | `sendRequest()` (async JMS), `createReport()`, `getReportFilePath()` |

---

## 5. Request Flow - Ticket Booking

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant TicketSearchController
    participant TicketSearchService
    participant FlightRepository
    participant TicketReserveController
    participant TicketReserveService
    participant ReservationRepository
    participant DB[(PostgreSQL)]

    User->>Browser: Enter search criteria
    Browser->>TicketSearchController: POST /ticket/search
    TicketSearchController->>TicketSearchService: searchFlight(criteria)
    TicketSearchService->>FlightRepository: findByVacantSeatSearchCriteria()
    FlightRepository->>DB: SELECT flights with vacancy
    DB-->>FlightRepository: Result set
    FlightRepository-->>TicketSearchService: List<Flight>
    TicketSearchService-->>TicketSearchController: List<FlightVacantInfoDto>
    TicketSearchController-->>Browser: B1/flightSearch.jsp
    
    User->>Browser: Select flight & enter passengers
    Browser->>TicketReserveController: POST /ticket/reserve?confirm
    TicketReserveController->>TicketReserveService: calculateTotalFare()
    TicketReserveService-->>TicketReserveController: Total fare
    TicketReserveController-->>Browser: B2/reserveConfirm.jsp
    
    User->>Browser: Confirm reservation
    Browser->>TicketReserveController: POST /ticket/reserve
    TicketReserveController->>TicketReserveService: validateReservation()
    TicketReserveService->>FlightRepository: findOneForUpdate() [Lock]
    FlightRepository->>DB: SELECT FOR UPDATE
    TicketReserveService->>FlightRepository: update() [Decrement seats]
    TicketReserveService->>ReservationRepository: insert()
    ReservationRepository->>DB: INSERT reservation
    TicketReserveService-->>TicketReserveController: TicketReserveDto
    TicketReserveController-->>Browser: B2/reserveComplete.jsp
```

---

## 6. Fare Calculation Logic

```mermaid
flowchart TD
    A[Route.basicFare] --> B[+ BoardingClass.extraCharge]
    B --> C{Peak Time?}
    C -->|Yes| D[× PeakTime.multiplicationRatio]
    C -->|No| E[Basic Fare]
    D --> E
    E --> F{Passenger Age?}
    F -->|Child < 12| G[× childFareRate / 100]
    F -->|Adult| H[Keep Basic Fare]
    G --> I[Apply FareType Discount]
    H --> I
    I --> J[× (100 - discountRate) / 100]
    J --> K[Ceil to 100 yen]
    K --> L[Final Fare]
```

### Fare Type Rules

| Code | Name | Discount | Passengers | Booking Window |
|------|------|----------|------------|----------------|
| OW | 片道 (One-way) | 0% | 1+ | 90-0 days |
| RT | 往復 (Round-trip) | 5% | 1+ | 90-0 days |
| RD1 | 予約割1 (Advance 1) | 10% | 1+ | 60-1 days |
| RD7 | 予約割7 (Advance 7) | 20% | 1+ | 60-7 days |
| ED | 早期割 (Early) | 30% | 1+ | 60-30 days |
| LD | レディース割 (Ladies) | 30% | Women only | 60-1 days |
| GD | グループ割 (Group) | 30% | 3+ | 60-1 days |

---

## 7. Component Dependency Graph

```mermaid
graph TB
    subgraph "Web Layer (atrs-web)"
        CTL[Controllers]
        API[REST APIs]
        FORM[Forms]
        VAL[Validators]
        HLP[Helpers]
    end
    
    subgraph "Domain Layer (atrs-domain)"
        SVC[Services]
        ENT[Entities/Models]
        REPO[Repositories]
        DTO[DTOs]
        ERR[Error Codes]
    end
    
    subgraph "Infrastructure (atrs-env)"
        DS[DataSource]
        TXM[TransactionManager]
        JMS[ActiveMQ]
        CFG[Config]
    end
    
    subgraph "Database (atrs-initdb)"
        DDL[DDL Scripts]
        DML[DML Scripts]
    end
    
    CTL --> SVC
    CTL --> FORM
    CTL --> HLP
    API --> SVC
    FORM --> VAL
    
    SVC --> ENT
    SVC --> REPO
    SVC --> DTO
    SVC --> ERR
    
    REPO --> DS
    SVC --> TXM
    SVC --> JMS
    
    DS --> DDL
    DS --> DML
```

---

## 8. Security Architecture

```mermaid
flowchart LR
    subgraph "Spring Security"
        A[SecurityFilterChain]
        B[UsernamePasswordAuthenticationFilter]
        C[AtrsUserDetailsService]
        D[PasswordEncoder BCrypt]
    end
    
    subgraph "Authorization"
        E["/auth/**" - permitAll]
        F["/member/**" - authenticated]
        G["/ticket/**" - authenticated]
        H["/report/**" - authenticated]
    end
    
    subgraph "Protection"
        I[TransactionToken]
        J[CSRF]
        K[Session Management]
    end
    
    A --> B
    B --> C
    C --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    A --> J
    A --> K
```

---

## 9. Async Report Generation (JMS)

```mermaid
sequenceDiagram
    actor User
    participant Controller
    participant ReportService
    participant JMS[(ActiveMQ Artemis)]
    participant ReportListener
    participant FileSystem

    User->>Controller: Request report
    Controller->>ReportService: sendRequest(membershipNumber)
    ReportService->>JMS: Send message to queue
    Controller-->>User: "Request accepted"
    
    Note over JMS,ReportListener: Async processing
    
    JMS->>ReportListener: Receive message
    ReportListener->>ReportService: createReport(criteria)
    ReportService->>FileSystem: Write CSV report
    
    User->>Controller: Check available reports
    Controller->>ReportService: getExistingReportNameList()
    ReportService->>FileSystem: List report files
    FileSystem-->>Controller: List of reports
    Controller-->>User: Show download links
    
    User->>Controller: Download report
    Controller->>ReportService: getReportFilePath()
    Controller-->>User: CSV file download
```

---

## 10. Configuration Hierarchy

```mermaid
flowchart TB
    subgraph "Web Initialization"
        WI[WebAppInitializer<br>AbstractAnnotationConfigDispatcherServletInitializer]
    end
    
    subgraph "Root Context"
        RC[AtrsDomainConfig]
        RC --> IC[AtrsInfraConfig<br>- MyBatis SqlSession]
        RC --> CC[AtrsCodeListConfig<br>- DB Code Lists]
        RC --> EC[AtrsEnvConfig<br>- DataSource, JMS]
        IC --> MC[MybatisConfig<br>- Type Aliases]
    end
    
    subgraph "Servlet Context"
        SC[SpringMvcConfig]
        SC --> SEC[SpringSecurityConfig<br>- Security Filter Chain]
    end
    
    WI --> RC
    WI --> SC
```

### Key Configuration Details

| Config Class | Responsibility |
|-------------|----------------|
| **AtrsDomainConfig** | Enables @Transactional, imports infra configs |
| **MybatisConfig** | mapUnderscoreToCamelCase, lazyLoading, type aliases |
| **AtrsCodeListConfig** | JdbcCodeList beans (airports, fare types, etc.) |
| **AtrsEnvConfig** | DBCP2 DataSource, TransactionManager, ActiveMQ |
| **SpringMvcConfig** | View resolver, interceptors, exception handlers |
| **SpringSecurityConfig** | Authentication, authorization, CSRF |

---

## 11. Design Patterns Used

| Pattern | Implementation |
|---------|----------------|
| **Service + Impl** | All services: `TicketSearchService` → `TicketSearchServiceImpl` |
| **Repository** | MyBatis mappers as repositories |
| **DTO** | `TicketSearchCriteriaDto`, `FlightVacantInfoDto`, `TicketReserveDto` |
| **Form Objects** | `TicketSearchForm`, `MemberRegisterForm` for web input |
| **Helper/Mapper** | `TicketHelper`, MapStruct `B1Mapper`, `B2Mapper` |
| **Provider** | `FareTypeProvider`, `RouteProvider` for cached master data |
| **Error Codes** | Enum-based: `TicketSearchErrorCode`, `MemberUpdateErrorCode` |
| **Validator** | Spring `Validator` interface: `TicketSearchValidator` |
| **Transaction Token** | `@TransactionTokenCheck` for double-submit prevention |

---

## 12. API Endpoints Summary

### MVC Controllers (JSP Views)

| Path | Controller | Description |
|------|------------|-------------|
| `/` | IndexController | Redirect to home |
| `/auth/login` | AuthLoginController | Login form |
| `/ticket/search` | TicketSearchController | Flight search |
| `/ticket/reserve` | TicketReserveController | Booking flow |
| `/member/register` | MemberRegisterController | Registration |
| `/member/update` | MemberUpdateController | Profile update |
| `/report` | ReservationHistoryReportController | Report generation |

### REST APIs

| Path | Method | Description |
|------|--------|-------------|
| `/api/flights` | GET/POST | Flight search API |
| `/api/member` | GET/POST/PUT | Member CRUD |
| `/api/auth` | POST | Authentication |
| `/ticket` | POST | Reserve ticket |
| `/ticket/check` | GET | Verify reservation |

---

## 13. Technology Stack

```mermaid
graph LR
    subgraph Frontend
        JSP[JSP]
        CSS[CSS]
        JS[JavaScript]
    end
    
    subgraph Backend
        J17[Java 17]
        SM[Spring MVC]
        SS[Spring Security]
        MB[MyBatis]
        MS[MapStruct]
        TF[TERASOLUNA 5.10.0]
    end
    
    subgraph Messaging
        AMQ[ActiveMQ Artemis]
    end
    
    subgraph Database
        PG[(PostgreSQL 42.7.4)]
    end
    
    subgraph Build
        MVN[Maven]
        CARGO[Cargo Plugin]
    end
    
    Frontend --> Backend
    Backend --> Messaging
    Backend --> Database
    MVN --> Backend
```

---

## 14. Key Business Rules

1. **Booking Window**: Flights bookable up to 90 days in advance
2. **Representative**: Must be 18+ years old
3. **Child Fare**: Applies to passengers under 12 years
4. **Ladies Discount**: All passengers must be female
5. **Group Discount**: Minimum 3 passengers required
6. **Seat Locking**: Pessimistic lock via `SELECT FOR UPDATE`
7. **Payment Deadline**: Outbound flight departure date

---

## 15. Directory Structure

```
JavaConfig-JSP/atrs/
├── pom.xml                           # Parent POM
│
├── atrs-web/
│   ├── pom.xml
│   └── src/main/
│       ├── java/jp/co/ntt/atrs/
│       │   ├── app/                  # Controllers by feature
│       │   │   ├── a0/               # Common (top, header)
│       │   │   ├── a1/               # Login
│       │   │   ├── b1/               # Flight search
│       │   │   ├── b2/               # Reservation
│       │   │   ├── c1/               # Member register
│       │   │   ├── c2/               # Member update
│       │   │   ├── d1/               # Report
│       │   │   └── common/           # Error handling
│       │   ├── api/                  # REST APIs
│       │   └── config/               # Spring MVC, Security
│       ├── resources/
│       │   └── i18n/                 # Message bundles
│       └── webapp/
│           └── WEB-INF/views/        # JSP views
│
├── atrs-domain/
│   ├── pom.xml
│   └── src/main/java/jp/co/ntt/atrs/
│       ├── config/app/               # Domain config
│       │   ├── AtrsDomainConfig.java
│       │   ├── AtrsInfraConfig.java
│       │   ├── AtrsCodeListConfig.java
│       │   └── mybatis/MybatisConfig.java
│       └── domain/
│           ├── model/                # Entities
│           ├── repository/           # MyBatis repos
│           └── service/              # Business logic
│               ├── a0/, a1/, a2/     # Auth services
│               ├── b0/, b1/, b2/     # Ticket services
│               ├── c0/, c1/, c2/     # Member services
│               └── d1/               # Report service
│
├── atrs-env/
│   ├── pom.xml
│   ├── configs/tomcat10-postgresql/  # Container config
│   └── src/main/
│       ├── java/.../AtrsEnvConfig.java
│       └── resources/
│           └── META-INF/spring/atrs-infra.properties
│
└── atrs-initdb/
    ├── pom.xml
    └── src/sqls/integration-test-postgres/
        ├── 00000_drop_all_tables.sql
        ├── 00100_create_all_tables.sql
        ├── 00200_insert_fixed_value.sql
        └── 002xx_insert_*.sql
```

---

## 16. Build & Run Commands

```bash
# Build
cd JavaConfig-JSP/atrs/
mvn clean install

# Initialize Database (PostgreSQL: db=atrs, user/pass=postgres)
mvn sql:execute -f atrs-initdb/pom.xml

# Run Application
mvn cargo:run -pl atrs-web

# Access: http://localhost:8080/atrs/
```

---

*Document generated: December 2024*
