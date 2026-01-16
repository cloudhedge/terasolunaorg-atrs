# Common Conversion Patterns

## MyBatis XML → Python SQL

### Basic Query
**MyBatis:**
```xml
<select id="findById" resultType="Member">
    SELECT * FROM member WHERE customer_no = #{customerNo}
</select>
```

**Python:**
```python
FIND_BY_ID = """
    SELECT * FROM member WHERE customer_no = :customer_no
"""

async def find_by_id(self, customer_no: str) -> Member | None:
    row = await self.db.fetch_one(FIND_BY_ID, {"customer_no": customer_no})
    return Member(**row._mapping) if row else None
```

### Dynamic SQL with Conditions
**MyBatis:**
```xml
<select id="search" resultType="Flight">
    SELECT * FROM flight
    <where>
        <if test="departure != null">
            AND departure_airport = #{departure}
        </if>
        <if test="arrival != null">
            AND arrival_airport = #{arrival}
        </if>
    </where>
</select>
```

**Python:**
```python
async def search(self, departure: str | None, arrival: str | None) -> list[Flight]:
    conditions = []
    params = {}

    if departure:
        conditions.append("departure_airport = :departure")
        params["departure"] = departure
    if arrival:
        conditions.append("arrival_airport = :arrival")
        params["arrival"] = arrival

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"SELECT * FROM flight {where}"

    rows = await self.db.fetch_all(query, params)
    return [Flight(**r._mapping) for r in rows]
```

### Foreach (IN clause)
**MyBatis:**
```xml
<select id="findByIds" resultType="Flight">
    SELECT * FROM flight WHERE id IN
    <foreach item="id" collection="ids" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>
```

**Python:**
```python
async def find_by_ids(self, ids: list[int]) -> list[Flight]:
    if not ids:
        return []
    placeholders = ", ".join(f":id_{i}" for i in range(len(ids)))
    params = {f"id_{i}": id for i, id in enumerate(ids)}
    query = f"SELECT * FROM flight WHERE id IN ({placeholders})"
    rows = await self.db.fetch_all(query, params)
    return [Flight(**r._mapping) for r in rows]
```

### Pessimistic Locking
**MyBatis:**
```xml
<select id="findByIdForUpdate" resultType="Flight">
    SELECT * FROM flight WHERE id = #{id} FOR UPDATE
</select>
```

**Python:**
```python
FIND_BY_ID_FOR_UPDATE = """
    SELECT * FROM flight WHERE id = :id FOR UPDATE
"""

async def find_by_id_for_update(self, id: int) -> Flight | None:
    # Must be called within a transaction
    row = await self.db.fetch_one(FIND_BY_ID_FOR_UPDATE, {"id": id})
    return Flight(**row._mapping) if row else None
```

## Transaction Patterns

### Service with Transaction
**Java:**
```java
@Transactional
public Reservation reserve(ReserveRequest req) {
    Flight flight = flightRepo.findByIdForUpdate(req.getFlightId());
    flight.setVacantNum(flight.getVacantNum() - req.getCount());
    flightRepo.save(flight);
    return reservationRepo.save(new Reservation(...));
}
```

**Python:**
```python
async def reserve(self, req: ReserveRequest) -> Reservation:
    async with self.db.transaction():
        flight = await self.flight_repo.find_by_id_for_update(req.flight_id)
        await self.flight_repo.update_vacant(flight.id, -req.count)
        return await self.reservation_repo.create(...)
```

## Exception Handling

### Business Exception
**Java:**
```java
public class InsufficientSeatsException extends BusinessException {
    public InsufficientSeatsException() {
        super("E_AR_B2_2001", "Insufficient seats available");
    }
}
```

**Python:**
```python
class AtrsException(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

class InsufficientSeatsException(AtrsException):
    def __init__(self):
        super().__init__("E_AR_B2_2001", "Insufficient seats available")
```

### Global Exception Handler
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(AtrsException)
async def atrs_exception_handler(request: Request, exc: AtrsException):
    return JSONResponse(
        status_code=400,
        content={"code": exc.code, "message": exc.message}
    )
```

## Mapper/DTO Patterns

### MapStruct → Pydantic
**Java:**
```java
@Mapper
public interface FlightMapper {
    FlightDto toDto(Flight flight);
    Flight toEntity(FlightDto dto);
}
```

**Python:**
```python
# No mapper needed - use Pydantic directly
class Flight(BaseModel):
    id: int
    name: str

class FlightDto(BaseModel):
    id: int
    name: str

# Entity to DTO
dto = FlightDto.model_validate(flight.model_dump())

# Or with field mapping
dto = FlightDto(
    id=flight.id,
    name=flight.flight_name  # Different field name
)
```

## Background Tasks

### JMS Listener → arq Task
**Java:**
```java
@JmsListener(destination = "report-queue")
public void processReport(ReportRequest request) {
    reportService.generate(request);
}
```

**Python (arq):**
```python
# tasks/worker.py
from arq import cron
from arq.connections import RedisSettings

async def process_report(ctx, request_data: dict):
    db = ctx["db"]
    service = ReportService(db)
    await service.generate(ReportRequest(**request_data))

class WorkerSettings:
    functions = [process_report]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)

# Enqueue task
from arq import create_pool
pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
await pool.enqueue_job("process_report", {"report_id": 123})
```

## Validation Patterns

### Custom Validator
**Java:**
```java
@Constraint(validatedBy = KatakanaValidator.class)
public @interface Katakana {
    String message() default "Must be katakana";
}
```

**Python:**
```python
import re
from pydantic import field_validator

class Member(BaseModel):
    name_kana: str

    @field_validator('name_kana')
    @classmethod
    def must_be_katakana(cls, v: str) -> str:
        if not re.match(r'^[\u30A0-\u30FF]+$', v):
            raise ValueError('Must be katakana')
        return v
```