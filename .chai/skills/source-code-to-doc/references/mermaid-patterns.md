# Mermaid Diagram Patterns

Tested patterns for architecture documentation. Copy and modify these.

## Flowchart - System Architecture

```mermaid
flowchart TB
    subgraph Presentation["Presentation Layer"]
        UI[Web UI]
        API[REST API]
    end

    subgraph Business["Business Layer"]
        SVC[Services]
        VAL[Validators]
    end

    subgraph Data["Data Layer"]
        REPO[Repositories]
        DB[(Database)]
    end

    UI --> API
    API --> SVC
    SVC --> VAL
    SVC --> REPO
    REPO --> DB
```

## Flowchart - Request Flow

```mermaid
flowchart LR
    A[Client] --> B[Load Balancer]
    B --> C[Web Server]
    C --> D{Auth?}
    D -->|Valid| E[App Server]
    D -->|Invalid| F[401 Error]
    E --> G[(Database)]
```

## Sequence - API Call

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API Gateway
    participant S as Service
    participant D as Database

    C->>A: HTTP Request
    A->>A: Validate Token
    A->>S: Forward Request
    S->>D: Query
    D-->>S: Results
    S-->>A: Response
    A-->>C: HTTP Response
```

## Sequence - Async Processing

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant Q as Queue
    participant W as Worker

    U->>A: Submit Job
    A->>Q: Enqueue
    A-->>U: Job ID
    W->>Q: Poll
    Q-->>W: Job Data
    W->>W: Process
    Note over W: Async processing
```

## Class Diagram - Domain Model

```mermaid
classDiagram
    class Entity {
        +id: Long
        +createdAt: Date
        +updatedAt: Date
    }

    class User {
        +email: String
        +name: String
        +authenticate()
    }

    class Order {
        +status: String
        +total: Decimal
        +submit()
        +cancel()
    }

    Entity <|-- User
    Entity <|-- Order
    User "1" --> "*" Order : places
```

## ER Diagram - Database Schema

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : includes

    USER {
        long id PK
        string email UK
        string name
    }

    ORDER {
        long id PK
        long user_id FK
        string status
        decimal total
    }
```

## State Diagram - Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted: submit()
    Submitted --> Approved: approve()
    Submitted --> Rejected: reject()
    Rejected --> Draft: revise()
    Approved --> [*]
```

## C4 Context (using flowchart)

```mermaid
flowchart TB
    subgraph boundary["System Boundary"]
        SYS[("Target System")]
    end

    USER[fa:fa-user User]
    EXT[External System]

    USER -->|Uses| SYS
    SYS -->|Calls| EXT
```

## Common Fixes

| Error | Fix |
|-------|-----|
| `Parse error` on spaces | Use camelCase: `UserService` not `User Service` |
| `Invalid syntax` on special chars | Quote the label: `A["Label: text"]` |
| `Unexpected token` | Check arrow syntax: `-->` for flowchart, `->>` for sequence |
| `Unknown diagram type` | Use lowercase: `flowchart` not `Flowchart` |
| Brackets not rendering | Escape in quotes: `A["data[0]"]` |
