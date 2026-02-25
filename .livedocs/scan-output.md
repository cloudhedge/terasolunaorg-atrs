## Architecture

ATRS (Airline Ticket Reservation System) is a Spring-based enterprise Java application demonstrating TERASOLUNA Server Framework for Java (5.x). The system implements a layered architecture with multiple deployment variants.

```mermaid
graph TD
    A[Web Layer<br/>Controllers & Views] --> B[Application Layer<br/>Services & DTOs]
    B --> C[Domain Layer<br/>Business Logic]
    C --> D[Infrastructure Layer<br/>Repositories & DB]
    
    E[Configuration Variants] --> F[JavaConfig-JSP]
    E --> G[JavaConfig-Thymeleaf] 
    E --> H[XMLConfig-JSP]
    E --> I[XMLConfig-Thymeleaf]
    
    J[External Systems] --> K[PostgreSQL Database]
    J --> L[ActiveMQ/Artemis JMS]
    J --> M[File System Reports]
```

The system provides four architectural variants combining configuration styles (Java/XML) with view technologies (JSP/Thymeleaf), all sharing the same business domain and data model.

## Modules

Each variant contains four core Maven modules with distinct responsibilities:

```mermaid
graph LR
    A[atrs-web<br/>WAR Package] --> B[atrs-domain<br/>Business Logic]
    A --> C[atrs-env<br/>Environment Config]
    B --> D[atrs-initdb<br/>Database Setup]
    
    E[Web Controllers<br/>Forms & Validation] --> A
    F[Service Layer<br/>Business Rules] --> B
    G[Spring Configuration<br/>Data Sources] --> C
    H[SQL Scripts<br/>Test Data] --> D
```

**atrs-web**: Web presentation layer containing controllers (b1-flight search, b2-reservation, c0/c2-member management, d1-reports), form objects, validators, and view templates. Implements MVC pattern with Spring Web MVC.

**atrs-domain**: Core business domain containing services, entities, repositories, and business logic. Houses the airline reservation business rules, member management, and flight operations.

**atrs-env**: Environment-specific configuration module managing database connections, JMS settings, and infrastructure beans. Contains Spring configuration and properties files.

**atrs-initdb**: Database initialization module with PostgreSQL schema definitions and test data population scripts for members, flights, routes, and reservations.

## Dependencies

Core technology stack built on TERASOLUNA Server Framework 5.10.0.RELEASE:

```mermaid
graph TD
    A[TERASOLUNA 5.10.0] --> B[Spring Framework 6.x]
    A --> C[Spring Boot Auto-configuration]
    A --> D[Macchinetta Framework]
    
    E[Database Layer] --> F[PostgreSQL 42.7.4]
    E --> G[MyBatis/JDBC]
    E --> H[Connection Pooling]
    
    I[Messaging] --> J[Apache Artemis]
    I --> K[JMS Integration]
    
    L[View Technologies] --> M[JSP/JSTL]
    L --> N[Thymeleaf Templates]
    
    O[Build & Runtime] --> P[Maven 3.x]
    O --> Q[Java 17/21]
    O --> R[Tomcat 10.x]
```

Key dependencies include PostgreSQL driver, MapStruct for object mapping, validation frameworks, and logging via Logback. The build uses Maven with Cargo plugin for deployment and Failsafe/Surefire for testing.

## Configuration

Environment configuration managed through properties and Spring profiles:

```mermaid
graph LR
    A[atrs-infra.properties] --> B[Database Config<br/>PostgreSQL Connection]
    A --> C[JMS Config<br/>ActiveMQ Settings]
    A --> D[Report Directory<br/>File System Path]
    
    E[Spring Profiles] --> F[Development Profile<br/>Local PostgreSQL]
    E --> G[Tomcat Profile<br/>Container Config]
    
    H[Configuration Styles] --> I[Java @Configuration<br/>Programmatic Setup]
    H --> J[XML Configuration<br/>Declarative Setup]
```

Database connection defaults to `localhost:5432/atrs` with `postgres/postgres` credentials. JMS uses localhost:61616 for message queuing. Report generation writes to `/atrs/reports/reservation` directory.

Java variants use `@Configuration` classes while XML variants use traditional Spring XML files. Container deployment configurations provided for Tomcat 10 with PostgreSQL.

## Risks

Several technical debt and modernization concerns identified:

**Legacy Framework Dependencies**: Built on older TERASOLUNA/Macchinetta stack that may have limited long-term support. Spring 6.x provides modern features but framework wrapper adds abstraction layers.

**Multiple Configuration Variants**: Four separate codebases (4 × ~78K LOC) create maintenance overhead and potential feature drift between variants. Consider consolidating to single modern approach.

**View Technology Fragmentation**: Supporting both JSP and Thymeleaf increases complexity. JSP is legacy technology with security considerations; Thymeleaf is more modern but requires different skillsets.

**Database Configuration**: Hardcoded development database credentials in properties files pose security risks. Missing environment-specific configuration management.

**Monolithic Architecture**: Single WAR deployment model limits scalability and cloud-native adoption. Consider microservices decomposition for better maintainability.

**Limited Test Coverage**: Database initialization scripts suggest integration testing setup, but test coverage across business logic modules needs assessment for production readiness.

🦉