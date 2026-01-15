---
name: java-to-python-migration
description: |
  Migrate Java/Spring applications to Python/FastAPI with exact feature parity.
  Use when user asks to: (1) Convert Java to Python, (2) Migrate Spring Boot/MVC to FastAPI,
  (3) Port MyBatis to raw SQL, (4) Convert Spring Security to JWT, (5) Migrate JMS to Redis/arq.
  Handles domain models, repositories, services, REST APIs, auth, and background tasks.
---

# Java to Python Migration

## Overview

```
┌─────────────────────┐     ┌─────────────────────┐
│   Java (Source)     │     │   Python (Target)   │
├─────────────────────┤     ├─────────────────────┤
│ Spring MVC + REST   │ ──► │ FastAPI             │
│ MyBatis (raw SQL)   │ ──► │ databases + asyncpg │
│ Spring Security     │ ──► │ python-jose+passlib │
│ JMS (Artemis)       │ ──► │ arq + Redis         │
│ JSP Views           │ ──► │ API-only (no views) │
└─────────────────────┘     └─────────────────────┘
```

## Step 1: Explore & Ask Clarifying Questions

First, explore the Java codebase using Task tool with Explore agent.

Then use **AskUserQuestion** tool to confirm approach:

```json
{
  "questions": [
    {
      "question": "Which Python web framework do you want to use?",
      "header": "Framework",
      "options": [
        {"label": "FastAPI (Recommended)", "description": "Modern async with auto OpenAPI docs"},
        {"label": "Flask", "description": "Lightweight, good for simpler apps"},
        {"label": "Django", "description": "Batteries-included with admin UI"}
      ],
      "multiSelect": false
    },
    {
      "question": "What is the primary migration goal?",
      "header": "Goal",
      "options": [
        {"label": "Exact feature parity", "description": "Replicate all functionality 1:1"},
        {"label": "Modernize + simplify", "description": "Refactor and improve"},
        {"label": "Minimal viable port", "description": "Core features only"}
      ],
      "multiSelect": false
    },
    {
      "question": "How should we handle the database layer?",
      "header": "Database",
      "options": [
        {"label": "Keep MyBatis-style (Recommended)", "description": "Raw SQL, easier to verify"},
        {"label": "SQLAlchemy ORM", "description": "Full ORM, more Pythonic"},
        {"label": "SQLAlchemy Core", "description": "SQL expressions"}
      ],
      "multiSelect": false
    }
  ]
}
```

### ATRS Project Defaults

For ATRS migration, use: **FastAPI + Exact parity + MyBatis-style raw SQL**

## Step 2: Execute Migration Phases

### Phase 1: Project Setup + Database Layer
- Create project structure → See [references/project-structure.md](references/project-structure.md)
- Port Java models → Pydantic → See [references/type-mapping.md](references/type-mapping.md)
- Extract SQL from MyBatis XML → Python modules

### Phase 2: Core Services
- Port `*ServiceImpl.java` → Python service classes
- See [references/patterns.md](references/patterns.md) for transaction/SQL patterns

### Phase 3: Auth + Security
- Convert Spring Security → JWT + passlib
- See [references/annotation-mapping.md](references/annotation-mapping.md)

### Phase 4: API Layer
- Convert `@Controller` → FastAPI routers
- See [references/annotation-mapping.md](references/annotation-mapping.md)

### Phase 5: Background Tasks
- Replace JMS → arq + Redis
- See [references/patterns.md](references/patterns.md)

### Phase 6: Testing
- Write pytest tests to validate migration
- See [references/testing.md](references/testing.md)

## Reference Docs (Load as needed)

| Doc | When to Load |
|-----|--------------|
| [type-mapping.md](references/type-mapping.md) | Converting entities, enums, validation |
| [annotation-mapping.md](references/annotation-mapping.md) | Converting controllers, security, services |
| [project-structure.md](references/project-structure.md) | Setting up Python project |
| [patterns.md](references/patterns.md) | MyBatis SQL, transactions, exceptions |
| [testing.md](references/testing.md) | Writing pytest tests for validation |

## Dependencies Template

```toml
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "databases[asyncpg]>=0.9.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.2.0",
    "passlib[bcrypt]>=1.7.4",
    "python-jose[cryptography]>=3.3.0",
    "arq>=0.25.0",
    "redis>=5.0.0",
]
```

## Quick Patterns

### Entity → Pydantic
```python
class Member(BaseModel):
    customer_no: str = Field(max_length=10)
    name: str
    email: EmailStr
```

### MyBatis → Raw SQL
```python
FIND_BY_ID = "SELECT * FROM member WHERE customer_no = :id"

async def find_by_id(self, id: str) -> Member | None:
    row = await self.db.fetch_one(FIND_BY_ID, {"id": id})
    return Member(**row._mapping) if row else None
```

### Transaction
```python
async with self.db.transaction():
    flight = await self.flight_repo.find_for_update(flight_id)
    # ... business logic
```

### FastAPI Router
```python
@router.get("/search")
async def search(dep: str = Query(...), db: Database = Depends(get_database)):
    return await TicketSearchService(db).search(dep)
```
