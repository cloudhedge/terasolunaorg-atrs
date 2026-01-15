# Target Python Project Structure

## Standard Layout

```
app-python/
├── pyproject.toml              # Dependencies + config
├── .env.example                # Environment template
├── alembic/                    # DB migrations (optional)
└── src/<app>/
    ├── __init__.py
    ├── main.py                 # FastAPI entry point
    │
    ├── config/
    │   ├── __init__.py
    │   ├── settings.py         # Pydantic Settings
    │   └── database.py         # DB connection pool
    │
    ├── models/                 # Pydantic domain models
    │   ├── __init__.py
    │   ├── enums.py
    │   └── *.py                # One per entity group
    │
    ├── repositories/           # Data access layer
    │   ├── __init__.py
    │   ├── base.py
    │   └── *.py                # One per aggregate
    │
    ├── services/               # Business logic
    │   ├── __init__.py
    │   └── */                  # Grouped by domain
    │
    ├── api/
    │   ├── __init__.py
    │   ├── deps.py             # Dependencies
    │   └── v1/                 # Versioned routes
    │
    ├── schemas/                # Request/Response DTOs
    │   └── *.py
    │
    ├── core/
    │   ├── security.py
    │   └── exceptions.py
    │
    └── tasks/                  # Background tasks
        └── *.py
```

## Java → Python Layer Mapping

| Java Package | Python Package |
|--------------|----------------|
| `domain/model` | `models/` |
| `domain/repository` | `repositories/` |
| `domain/service` | `services/` |
| `app/*Controller` | `api/v1/` |
| `api/*Form` | `schemas/` |
| `config/` | `config/` |
| `listener/` | `tasks/` |

## File Templates

### pyproject.toml
```toml
[project]
name = "app"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    # Pin major.minor to prevent breaking changes
    # See: references/dependency-management.md
    "fastapi>=0.110.0,<0.111",
    "uvicorn[standard]>=0.27.0,<0.28",
    "databases[asyncpg]>=0.9.0,<0.10",
    "pydantic>=2.6.0,<3",
    "pydantic-settings>=2.2.0,<3",
    "passlib[bcrypt]>=1.7.4,<2",
    "python-jose[cryptography]>=3.3.0,<4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0,<9",
    "pytest-asyncio>=0.23.0,<1",
    "httpx>=0.27.0,<0.28",  # CRITICAL: Pin to prevent 0.28 API breakage
]
```

**IMPORTANT:** Always pin major.minor versions to prevent breaking changes.
See [dependency-management.md](dependency-management.md) for details.

### config/settings.py
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    redis_url: str = "redis://localhost:6379"
    secret_key: str
    debug: bool = False

settings = Settings()
```

### config/database.py
```python
from databases import Database
from .settings import settings

database = Database(settings.database_url)

async def get_database() -> Database:
    return database
```

### main.py
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .config.database import database
from .api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
```

### repositories/base.py
```python
from databases import Database

class BaseRepository:
    def __init__(self, db: Database):
        self.db = db

    async def fetch_one(self, query: str, values: dict = None):
        return await self.db.fetch_one(query, values or {})

    async def fetch_all(self, query: str, values: dict = None):
        return await self.db.fetch_all(query, values or {})

    async def execute(self, query: str, values: dict = None):
        return await self.db.execute(query, values or {})
```

### api/deps.py
```python
from typing import Annotated
from fastapi import Depends
from databases import Database
from ..config.database import get_database
from ..core.security import get_current_user
from ..models import User

DatabaseDep = Annotated[Database, Depends(get_database)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
```

## File Reduction

Typical: **200+ Java files → ~50 Python files**

Reasons:
- No interface + impl separation
- No XML configs
- Pydantic combines entity + validation
- Python modules are more compact
