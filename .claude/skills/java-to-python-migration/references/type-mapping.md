# Java to Python Type Mapping

## Primitive & Basic Types

| Java | Python | Pydantic |
|------|--------|----------|
| `int`, `Integer` | `int` | `int` |
| `long`, `Long` | `int` | `int` |
| `double`, `Double` | `float` | `float` |
| `float`, `Float` | `float` | `float` |
| `boolean`, `Boolean` | `bool` | `bool` |
| `String` | `str` | `str` |
| `char`, `Character` | `str` | `str` (length=1) |
| `byte[]` | `bytes` | `bytes` |

## Date/Time Types

| Java | Python | Notes |
|------|--------|-------|
| `java.util.Date` | `datetime` | `from datetime import datetime` |
| `java.time.LocalDate` | `date` | `from datetime import date` |
| `java.time.LocalDateTime` | `datetime` | `from datetime import datetime` |
| `java.time.LocalTime` | `time` | `from datetime import time` |
| `java.time.Instant` | `datetime` | Use `datetime.utcnow()` |
| `java.time.ZonedDateTime` | `datetime` | Consider `pendulum` for TZ |
| `java.sql.Timestamp` | `datetime` | Same as above |

## Collections

| Java | Python | Pydantic |
|------|--------|----------|
| `List<T>` | `list[T]` | `list[T]` |
| `Set<T>` | `set[T]` | `set[T]` |
| `Map<K,V>` | `dict[K,V]` | `dict[K,V]` |
| `Collection<T>` | `list[T]` | `list[T]` |
| `Optional<T>` | `T \| None` | `T \| None = None` |
| `T[]` (array) | `list[T]` | `list[T]` |

## Special Types

| Java | Python | Notes |
|------|--------|-------|
| `BigDecimal` | `Decimal` | `from decimal import Decimal` |
| `BigInteger` | `int` | Python int is unbounded |
| `UUID` | `UUID` | `from uuid import UUID` |
| `enum` | `Enum` | `from enum import Enum` |
| `Object` | `Any` | `from typing import Any` |
| `void` | `None` | Return type |

## Validation Constraints → Pydantic Field

| Java (JSR-303) | Pydantic |
|----------------|----------|
| `@NotNull` | Required field (no default) |
| `@NotEmpty` | `Field(min_length=1)` |
| `@NotBlank` | `Field(min_length=1)` + strip |
| `@Size(min=x, max=y)` | `Field(min_length=x, max_length=y)` |
| `@Min(x)` | `Field(ge=x)` |
| `@Max(x)` | `Field(le=x)` |
| `@Email` | `EmailStr` |
| `@Pattern(regexp="...")` | `Field(pattern="...")` |
| `@Positive` | `Field(gt=0)` |
| `@PositiveOrZero` | `Field(ge=0)` |
| `@Negative` | `Field(lt=0)` |
| `@Past` | Custom validator |
| `@Future` | Custom validator |

## Entity → Pydantic Model Example

**Java:**
```java
@Data
public class Member {
    @NotNull
    @Size(min=10, max=10)
    private String customerNo;

    @NotEmpty
    private String name;

    @Email
    private String email;

    @Past
    private LocalDate birthday;

    private Integer age;

    @NotNull
    private Gender gender;
}
```

**Python:**
```python
from datetime import date
from pydantic import BaseModel, Field, EmailStr, field_validator

class Member(BaseModel):
    customer_no: str = Field(min_length=10, max_length=10)
    name: str = Field(min_length=1)
    email: EmailStr | None = None
    birthday: date | None = None
    age: int | None = None
    gender: Gender

    @field_validator('birthday')
    @classmethod
    def birthday_must_be_past(cls, v):
        if v and v >= date.today():
            raise ValueError('birthday must be in the past')
        return v
```

## Enum Conversion

**Java:**
```java
public enum Gender {
    M("Male"),
    F("Female");

    private final String label;
    Gender(String label) { this.label = label; }
}
```

**Python:**
```python
from enum import Enum

class Gender(str, Enum):
    M = "M"
    F = "F"

    @property
    def label(self) -> str:
        return {"M": "Male", "F": "Female"}[self.value]
```

## Nullable Handling

| Java Pattern | Python Pattern |
|--------------|----------------|
| `@Nullable String x` | `x: str \| None = None` |
| `Optional<String> x` | `x: str \| None = None` |
| `String x` (can be null) | `x: str \| None = None` |
| `@NotNull String x` | `x: str` (required) |
