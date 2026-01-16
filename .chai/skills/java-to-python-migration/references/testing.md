# Testing Patterns for Python Migration

## Setup

### Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "pytest-cov>=4.1.0",
]
```

### conftest.py
```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from databases import Database

from app.main import app
from app.config import settings

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture
async def db():
    """Test database connection."""
    database = Database(settings.test_database_url)
    await database.connect()
    yield database
    await database.disconnect()

@pytest_asyncio.fixture
async def client():
    """Async test client for API tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
```

## API Endpoint Testing

### Basic GET Endpoint
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_search_flights(client: AsyncClient):
    response = await client.get(
        "/api/v1/flights/search",
        params={"departure": "HND", "arrival": "ITM", "date": "2026-02-01"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

### POST with Authentication
```python
@pytest.mark.asyncio
async def test_create_reservation(client: AsyncClient, auth_token: str):
    response = await client.post(
        "/api/v1/reservations",
        json={
            "flight_id": 1,
            "passengers": [{"name": "Test User", "gender": "M"}]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    assert "reservation_no" in response.json()
```

### Auth Token Fixture
```python
@pytest_asyncio.fixture
async def auth_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpass"}
    )
    return response.json()["access_token"]
```

## Service Layer Testing

### Service with Database
```python
import pytest
from databases import Database
from app.services.ticket import TicketSearchService

@pytest.mark.asyncio
async def test_search_service(db: Database):
    service = TicketSearchService(db)

    results = await service.search(
        departure="HND",
        arrival="ITM",
        date=date(2026, 2, 1)
    )

    assert len(results) > 0
    assert all(r.departure_airport == "HND" for r in results)
```

### Transaction Testing
```python
@pytest.mark.asyncio
async def test_reservation_decrements_seats(db: Database):
    service = TicketReserveService(db)

    # Get initial seat count
    flight = await service.flight_repo.find_by_id(1)
    initial_seats = flight.vacant_num

    # Make reservation
    await service.reserve(ReservationInput(flight_id=1, passenger_count=2))

    # Verify seats decremented
    flight = await service.flight_repo.find_by_id(1)
    assert flight.vacant_num == initial_seats - 2
```

### Rollback on Error
```python
@pytest.mark.asyncio
async def test_reservation_rollback_on_error(db: Database):
    service = TicketReserveService(db)

    flight = await service.flight_repo.find_by_id(1)
    initial_seats = flight.vacant_num

    # Try to reserve more seats than available
    with pytest.raises(InsufficientSeatsException):
        await service.reserve(ReservationInput(
            flight_id=1,
            passenger_count=initial_seats + 100
        ))

    # Verify no change (transaction rolled back)
    flight = await service.flight_repo.find_by_id(1)
    assert flight.vacant_num == initial_seats
```

## Repository Testing

### Basic CRUD
```python
@pytest.mark.asyncio
async def test_member_repository(db: Database):
    repo = MemberRepository(db)

    # Create
    member_id = await repo.create(MemberInput(
        name="Test",
        email="test@example.com"
    ))

    # Read
    member = await repo.find_by_id(member_id)
    assert member.name == "Test"

    # Update
    await repo.update(member_id, {"name": "Updated"})
    member = await repo.find_by_id(member_id)
    assert member.name == "Updated"

    # Delete
    await repo.delete(member_id)
    member = await repo.find_by_id(member_id)
    assert member is None
```

## Mocking Patterns

### Mock Repository
```python
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_service_with_mock_repo():
    # Create mock repository
    mock_repo = MagicMock()
    mock_repo.find_by_id = AsyncMock(return_value=Flight(
        id=1,
        name="NH001",
        vacant_num=100
    ))
    mock_repo.update_vacant = AsyncMock()

    # Inject mock
    service = TicketReserveService.__new__(TicketReserveService)
    service.flight_repo = mock_repo

    # Test
    await service.reserve(ReservationInput(flight_id=1, passenger_count=2))

    mock_repo.find_by_id.assert_called_once_with(1)
    mock_repo.update_vacant.assert_called_once()
```

### Mock External Services
```python
@pytest.mark.asyncio
async def test_with_mocked_redis(mocker):
    mock_pool = mocker.patch("arq.create_pool")
    mock_pool.return_value.enqueue_job = AsyncMock()

    service = ReportService()
    await service.request_report({"type": "history"})

    mock_pool.return_value.enqueue_job.assert_called_once()
```

## Test Database Setup

### Using Test Database
```python
# .env.test
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/atrs_test

# conftest.py
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Run before all tests."""
    import subprocess
    subprocess.run(["psql", "-f", "scripts/setup_test_db.sql"])
    yield
    subprocess.run(["psql", "-f", "scripts/teardown_test_db.sql"])
```

### Transaction Rollback per Test
```python
@pytest_asyncio.fixture
async def db_transaction(db: Database):
    """Each test runs in a transaction that gets rolled back."""
    async with db.transaction() as transaction:
        yield db
        await transaction.rollback()
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_flights.py

# Run tests matching pattern
pytest -k "reservation"

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_api/
│   ├── test_auth.py
│   ├── test_flights.py
│   └── test_reservations.py
├── test_services/
│   ├── test_search_service.py
│   └── test_reserve_service.py
└── test_repositories/
    ├── test_flight_repo.py
    └── test_member_repo.py
```
