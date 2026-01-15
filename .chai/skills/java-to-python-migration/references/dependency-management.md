# Dependency Management & Version Pinning

## Critical Lessons Learned

### Problem: Breaking API Changes
When migrating from Java to Python, loose version constraints can break your application when dependencies update.

**Real Example from ATRS Migration:**
```toml
# ❌ BAD - Allowed httpx 0.28 which broke tests
dev = [
    "httpx>=0.27.0",  # Installs latest (0.28.1)
]

# Error: TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'
```

**httpx 0.28 changed the API:**
```python
# Old API (0.27.x)
AsyncClient(app=app, base_url="http://test")

# New API (0.28+) - BREAKING CHANGE
AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
```

### Solution: Pin Major.Minor Versions

```toml
# ✅ GOOD - Prevents breaking changes
dev = [
    "httpx>=0.27.0,<0.28",  # Only allows 0.27.x patches
]
```

## Version Pinning Strategy

### 1. Production Dependencies - Pin Major.Minor

```toml
[project]
dependencies = [
    # Pin major.minor, allow patches
    "fastapi>=0.110.0,<0.111",
    "uvicorn[standard]>=0.27.0,<0.28",
    "databases[asyncpg]>=0.9.0,<0.10",
    "asyncpg>=0.29.0,<0.30",
    "pydantic>=2.6.0,<3",          # Pin major version
    "pydantic-settings>=2.2.0,<3",
    "passlib[bcrypt]>=1.7.4,<2",
    "python-jose[cryptography]>=3.3.0,<4",
]
```

### 2. Dev Dependencies - Also Pin

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0,<9",
    "pytest-asyncio>=0.23.0,<1",
    "httpx>=0.27.0,<0.28",  # CRITICAL - Prevents 0.28 breakage
    "ruff>=0.3.0,<1",
]
```

### 3. Generate Lock File

```bash
# After pinning versions in pyproject.toml
pip freeze > requirements.lock

# Commit both files to git
git add pyproject.toml requirements.lock
```

**Why both files?**
- `pyproject.toml`: Human-readable, defines ranges
- `requirements.lock`: Exact versions for reproducible builds

## Common Breaking Changes to Watch

### httpx (Test Framework)
| Version | Breaking Change |
|---------|----------------|
| 0.28.0  | `AsyncClient(app=)` → `AsyncClient(transport=ASGITransport(app=))` |

### Pydantic (Validation)
| Version | Breaking Change |
|---------|----------------|
| 2.0.0   | `class Config` → `ConfigDict` |
| 2.0.0   | `validator()` → `field_validator()` |

### FastAPI
| Version | Breaking Change |
|---------|----------------|
| 0.100.0 | Starlette compatibility changes |

### databases
| Version | Breaking Change |
|---------|----------------|
| 0.9.0   | Async context manager required |

## Environment Setup Best Practices

### Always Use Virtual Environments

```bash
# ❌ NEVER do this (fails on PEP 668 systems)
pip3 install package

# ✅ ALWAYS use venv
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

**Why?**
- PEP 668: Modern Python (3.11+) blocks global installs
- Prevents breaking system Python
- Isolates project dependencies

### Add to README.md

```markdown
## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"  # Dev dependencies

# Verify installation
pytest tests/ -v
\```
```

## Maven to pyproject.toml Conversion

### Java pom.xml
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>3.2.0</version>
    </dependency>
</dependencies>
```

### Python pyproject.toml
```toml
[project]
dependencies = [
    "fastapi>=0.110.0,<0.111",  # Equivalent to Spring Boot Web
]
```

## Dependency Upgrade Workflow

### 1. Check for Updates
```bash
pip list --outdated
```

### 2. Review Changelogs
- Visit GitHub releases page
- Read CHANGELOG.md
- Look for "BREAKING CHANGE" labels

### 3. Test in Separate Branch
```bash
git checkout -b upgrade-dependencies

# Update pyproject.toml
# Change: "httpx>=0.27.0,<0.28"
# To:     "httpx>=0.28.0,<0.29"

pip install --upgrade httpx
pytest tests/ -v  # Does it break?
```

### 4. Fix Breaking Changes
```python
# Update code for new API
from httpx import AsyncClient, ASGITransport

async with AsyncClient(
    transport=ASGITransport(app=app),
    base_url="http://test"
) as client:
    ...
```

### 5. Update Lock File
```bash
pip freeze > requirements.lock
git add pyproject.toml requirements.lock
git commit -m "chore: upgrade httpx 0.27→0.28"
```

## CI/CD Integration

### Test Against Multiple Versions
```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
    httpx-version: ["0.27.0", "0.27.2"]  # Test min and max

steps:
  - name: Install dependencies
    run: |
      pip install httpx==${{ matrix.httpx-version }}
      pip install -e .
  - name: Run tests
    run: pytest tests/ -v
```

### Lock File Validation
```yaml
- name: Check lock file is up to date
  run: |
    pip freeze > requirements.check
    diff requirements.lock requirements.check
```

## Common Pitfalls

### ❌ Don't: Loose Constraints
```toml
dependencies = [
    "httpx",  # Gets latest - DANGEROUS
    "fastapi>=0.1",  # Allows v0.1→v999
]
```

### ✅ Do: Pin Major.Minor
```toml
dependencies = [
    "httpx>=0.27.0,<0.28",
    "fastapi>=0.110.0,<0.111",
]
```

### ❌ Don't: Skip Lock Files
```bash
# Only pyproject.toml committed
git add pyproject.toml
```

### ✅ Do: Commit Both
```bash
git add pyproject.toml requirements.lock
```

### ❌ Don't: Upgrade Without Testing
```bash
pip install --upgrade-all  # DANGEROUS
```

### ✅ Do: Upgrade One at a Time
```bash
pip install --upgrade httpx
pytest tests/ -v
git commit -m "upgrade: httpx 0.27→0.28"
```

## Monitoring Tools

### Dependabot (GitHub)
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

### Renovate Bot
```json
{
  "extends": ["config:base"],
  "pip_requirements": {
    "fileMatch": ["pyproject.toml", "requirements.lock"]
  }
}
```

### Safety (Security Scanner)
```bash
pip install safety
safety check --json
```

## Quick Reference

### Version Constraint Syntax
| Syntax | Meaning | Example |
|--------|---------|---------|
| `==1.2.3` | Exact version | `httpx==0.27.0` |
| `>=1.2,<2` | Major.minor pin | `httpx>=0.27.0,<0.28` |
| `~=1.2.3` | Compatible release | `~=0.27.0` → `>=0.27.0,<0.28` |
| `>=1.2` | Loose (avoid) | Too permissive |

### Recommended Pins
```toml
dependencies = [
    # Web framework - pin minor
    "fastapi>=0.110.0,<0.111",
    
    # Server - pin minor
    "uvicorn[standard]>=0.27.0,<0.28",
    
    # Database - pin minor
    "databases[asyncpg]>=0.9.0,<0.10",
    "asyncpg>=0.29.0,<0.30",
    
    # Validation - pin major (more stable)
    "pydantic>=2.6.0,<3",
    "pydantic-settings>=2.2.0,<3",
    
    # Security - pin major
    "passlib[bcrypt]>=1.7.4,<2",
    "python-jose[cryptography]>=3.3.0,<4",
    
    # Utils - pin major
    "python-multipart>=0.0.9,<1",
    "email-validator>=2.1.0,<3",
]

[project.optional-dependencies]
dev = [
    # Testing - pin minor for test stability
    "pytest>=8.0.0,<9",
    "pytest-asyncio>=0.23.0,<1",
    "httpx>=0.27.0,<0.28",  # CRITICAL
    
    # Linting - pin minor
    "ruff>=0.3.0,<1",
]
```

## Checklist

**Before Migration:**
- [ ] Review all Java dependencies in pom.xml
- [ ] Find Python equivalents
- [ ] Pin major.minor versions in pyproject.toml

**After Installation:**
- [ ] Generate requirements.lock
- [ ] Commit both pyproject.toml and requirements.lock
- [ ] Test application starts
- [ ] Run full test suite

**For Updates:**
- [ ] Read CHANGELOG for breaking changes
- [ ] Test in separate branch
- [ ] Update code for new APIs
- [ ] Regenerate requirements.lock
- [ ] Run tests before merging

**In CI/CD:**
- [ ] Test against min and max versions
- [ ] Validate lock file is current
- [ ] Fail on deprecation warnings
- [ ] Set up Dependabot/Renovate

## See Also

- [Testing Strategies](testing.md) - How to test dependency upgrades
- [Project Structure](project-structure.md) - pyproject.toml setup
- [Type Mapping](type-mapping.md) - Java library to Python library mapping
