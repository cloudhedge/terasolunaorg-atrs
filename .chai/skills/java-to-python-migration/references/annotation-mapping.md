# Spring to FastAPI Annotation Mapping

## Controller Annotations

| Spring | FastAPI |
|--------|---------|
| `@Controller` | `router = APIRouter()` |
| `@RestController` | `router = APIRouter()` |
| `@RequestMapping("/api")` | `router = APIRouter(prefix="/api")` |
| `@GetMapping("/path")` | `@router.get("/path")` |
| `@PostMapping("/path")` | `@router.post("/path")` |
| `@PutMapping("/path")` | `@router.put("/path")` |
| `@DeleteMapping("/path")` | `@router.delete("/path")` |
| `@PatchMapping("/path")` | `@router.patch("/path")` |

## Parameter Annotations

| Spring | FastAPI |
|--------|---------|
| `@PathVariable("id")` | Path parameter: `id: str` |
| `@RequestParam("q")` | `q: str = Query(...)` |
| `@RequestParam(required=false)` | `q: str \| None = Query(None)` |
| `@RequestParam(defaultValue="x")` | `q: str = Query("x")` |
| `@RequestBody` | `body: Model` (Pydantic model) |
| `@RequestHeader("X-Token")` | `x_token: str = Header(...)` |
| `@CookieValue("session")` | `session: str = Cookie(...)` |

## Dependency Injection

| Spring | FastAPI |
|--------|---------|
| `@Autowired` | `Depends()` |
| `@Service` | Regular class |
| `@Repository` | Regular class |
| `@Component` | Regular class |
| `@Configuration` | Pydantic Settings |

## Security Annotations

| Spring Security | FastAPI |
|-----------------|---------|
| `@PreAuthorize("isAuthenticated()")` | `Depends(get_current_user)` |
| `@PreAuthorize("hasRole('ADMIN')")` | `Depends(require_role("ADMIN"))` |
| `@Secured("ROLE_USER")` | `Depends(require_role("USER"))` |
| `UserDetails` | Custom `User` model |
| `SecurityContextHolder` | `Depends(get_current_user)` |

## Transaction Annotations

| Spring | Python |
|--------|--------|
| `@Transactional` | `async with db.transaction():` |
| `@Transactional(readOnly=true)` | Regular query (no transaction needed) |
| `@Transactional(isolation=...)` | `async with db.transaction(isolation="...")` |

## Controller Example

**Java:**
```java
@RestController
@RequestMapping("/api/v1/flights")
public class FlightController {

    @Autowired
    private FlightService flightService;

    @GetMapping("/search")
    public List<FlightDto> search(
            @RequestParam String departure,
            @RequestParam String arrival,
            @RequestParam @DateTimeFormat(iso = ISO.DATE) LocalDate date) {
        return flightService.search(departure, arrival, date);
    }

    @PostMapping("/reserve")
    @PreAuthorize("isAuthenticated()")
    public ReservationDto reserve(@RequestBody @Valid ReserveRequest request) {
        return flightService.reserve(request);
    }
}
```

**Python:**
```python
from fastapi import APIRouter, Query, Depends
from datetime import date

router = APIRouter(prefix="/api/v1/flights", tags=["flights"])

@router.get("/search")
async def search(
    departure: str = Query(...),
    arrival: str = Query(...),
    date: date = Query(...),
    db: Database = Depends(get_database)
) -> list[FlightDto]:
    service = FlightService(db)
    return await service.search(departure, arrival, date)

@router.post("/reserve")
async def reserve(
    request: ReserveRequest,
    db: Database = Depends(get_database),
    user: User = Depends(get_current_user)  # Auth required
) -> ReservationDto:
    service = FlightService(db)
    return await service.reserve(request, user)
```

## Service Example

**Java:**
```java
@Service
@Transactional
public class FlightServiceImpl implements FlightService {

    @Autowired
    private FlightRepository flightRepository;

    @Override
    public List<Flight> search(String dep, String arr, LocalDate date) {
        return flightRepository.findByRoute(dep, arr, date);
    }

    @Override
    @Transactional
    public Reservation reserve(ReserveRequest request) {
        Flight flight = flightRepository.findByIdForUpdate(request.getFlightId());
        if (flight.getVacantNum() < request.getPassengerCount()) {
            throw new InsufficientSeatsException();
        }
        flight.setVacantNum(flight.getVacantNum() - request.getPassengerCount());
        flightRepository.save(flight);
        return reservationRepository.save(new Reservation(...));
    }
}
```

**Python:**
```python
class FlightService:
    def __init__(self, db: Database):
        self.db = db
        self.flight_repo = FlightRepository(db)
        self.reservation_repo = ReservationRepository(db)

    async def search(self, dep: str, arr: str, date: date) -> list[Flight]:
        return await self.flight_repo.find_by_route(dep, arr, date)

    async def reserve(self, request: ReserveRequest) -> Reservation:
        async with self.db.transaction():
            flight = await self.flight_repo.find_by_id_for_update(request.flight_id)
            if flight.vacant_num < request.passenger_count:
                raise InsufficientSeatsException()
            await self.flight_repo.update_vacant(flight.id, -request.passenger_count)
            return await self.reservation_repo.create(...)
```

## Authentication Setup

**Spring Security Config → FastAPI Security:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401)
        return await user_repo.find_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401)

def require_role(role: str):
    async def checker(user: User = Depends(get_current_user)):
        if role not in user.roles:
            raise HTTPException(status_code=403)
        return user
    return checker
```
