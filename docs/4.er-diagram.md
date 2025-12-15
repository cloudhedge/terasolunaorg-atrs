# ATRS Database ER Diagram

## Overview
- **13 Tables**
- **4 Sequences**
- **PostgreSQL**

## ER Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        ATRS DATABASE ER DIAGRAM                                                 │
│                                         (13 Tables, 4 Sequences)                                                │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────┐                                           ┌─────────────────────────┐
  │      CREDIT_TYPE        │                                           │        AIRPORT          │
  ├─────────────────────────┤                                           ├─────────────────────────┤
  │ PK CREDIT_TYPE_CD  VC(3)│                                           │ PK AIRPORT_CD      VC(3)│
  │    CREDIT_FIRM    VC(80)│                                           │    AIRPORT_NAME  VC(15) │
  │    DISPLAY_ORDER    INT │                                           │    DISPLAY_ORDER    INT │
  └───────────┬─────────────┘                                           └───────────┬─────────────┘
              │                                                                     │
              │ 1                                                                   │ 1
              │                                                           ┌─────────┴─────────┐
              ▼ N                                                         │                   │
  ┌─────────────────────────────────┐                                     ▼ N                 ▼ N
  │            MEMBER               │                         ┌─────────────────────────────────┐
  ├─────────────────────────────────┤                         │            ROUTE                │
  │ PK CUSTOMER_NO         VC(10)   │                         ├─────────────────────────────────┤
  │    KANJI_FAMILY_NAME   VC(10)   │                         │ PK ROUTE_NO               INT   │
  │    KANJI_GIVEN_NAME    VC(10)   │                         │ FK DEP_AIRPORT_CD        VC(3)  │──► AIRPORT
  │    KANA_FAMILY_NAME    VC(10)   │                         │ FK ARR_AIRPORT_CD        VC(3)  │──► AIRPORT
  │    KANA_GIVEN_NAME     VC(10)   │                         │    FLIGHT_TIME           VC(4)  │
  │    BIRTHDAY            DATE     │                         │    BASIC_FARE             INT   │
  │    GENDER              VC(1)    │                         └───────────────┬─────────────────┘
  │    TEL                 VC(13)   │                                         │
  │    ZIP_CODE            VC(7)    │                                         │ 1
  │    ADDRESS             VC(60)   │        ┌────────────────────────┐       │
  │    MAIL                VC(256)  │        │         PLANE          │       │
  │    CREDIT_NO           VC(16)   │        ├────────────────────────┤       │
  │ FK CREDIT_TYPE_CD      VC(3)    │──►     │ PK CRAFT_TYPE    VC(16)│       │
  │    CREDIT_TERM         VC(5)    │        │    N_SEAT_NUM      INT │       │
  └───────────┬─────────────────────┘        │    S_SEAT_NUM      INT │       │
              │                              └──────────┬─────────────┘       │
              │ 1                                       │ 1                   │
              │                                         │                     │
    ┌─────────┼─────────────────────────────────────────┼─────────────────────┘
    │         │                                         │
    │         │                                         ▼ N
    │         │                         ┌───────────────────────────────────┐
    │         │                         │         FLIGHT_MASTER             │
    │         │                         ├───────────────────────────────────┤
    │         │                         │ PK FLIGHT_NAME          VC(6)     │
    │         │                         │ FK ROUTE_NO               INT     │──► ROUTE
    │         │                         │    DEPARTURE_TIME        VC(4)    │
    │         │                         │    ARRIVAL_TIME          VC(4)    │
    │         │                         │ FK CRAFT_TYPE           VC(16)    │──► PLANE
    │         │                         └─────────────────┬─────────────────┘
    │         │                                           │
    │         │                                           │ 1
    ▼ N       │                                           │
  ┌───────────┴─────────────────┐                         │
  │       MEMBER_LOGIN          │                         │
  ├─────────────────────────────┤                         │
  │ PK/FK CUSTOMER_NO    VC(10) │──► MEMBER               │
  │    PASSWORD         VC(124) │                         │
  │    LAST_PASSWORD    VC(124) │                         │
  │    LOGIN_DATE_TIME TIMESTAMP│                         │
  │    LOGIN_FLG        BOOLEAN │                         │
  └─────────────────────────────┘                         │
                                                          │
    ┌─────────────────────────────────────────────────────┼─────────────────────────────────────┐
    │                                                     │                                     │
    │                                                     │                                     │
    │   ┌─────────────────────────┐                       │        ┌─────────────────────────┐  │
    │   │     BOARDING_CLASS      │                       │        │       FARE_TYPE         │  │
    │   ├─────────────────────────┤                       │        ├─────────────────────────┤  │
    │   │ PK BOARDING_CLASS_CD VC(1)│                     │        │ PK FARE_TYPE_CD    VC(4)│  │
    │   │  BOARDING_CLASS_NAME VC(10)│                    │        │  FARE_TYPE_NAME   VC(10)│  │
    │   │    EXTRA_CHARGE       INT │                     │        │    DISCOUNT_RATE     INT│  │
    │   │    DISPLAY_ORDER      INT │                     │        │  RSRV_AVAIL_START_DAY INT│ │
    │   └───────────┬─────────────┘                       │        │  RSRV_AVAIL_END_DAY   INT│ │
    │               │                                     │        │    PASSENGER_MIN_NUM  INT│ │
    │               │ 1                                   │        │    DISPLAY_ORDER      INT│ │
    │               │                                     │        └───────────┬─────────────┘  │
    │               │                                     │                    │                │
    │               │                                     │                    │ 1              │
    │               │                                     ▼ N                  │                │
    │               │                 ┌─────────────────────────────────────────────────────┐   │
    │               │                 │                      FLIGHT                         │   │
    │               │                 ├─────────────────────────────────────────────────────┤   │
    │               └────────────────►│ PK DEPARTURE_DATE                          DATE    │   │
    │                                 │ PK/FK FLIGHT_NAME                          VC(6)   │───┼──► FLIGHT_MASTER
    │                                 │ PK/FK BOARDING_CLASS_CD                    VC(1)   │◄──┘
    └────────────────────────────────►│ PK/FK FARE_TYPE_CD                         VC(4)   │◄─────── FARE_TYPE
                                      │    VACANT_NUM                               INT    │
                                      └───────────────────────────┬─────────────────────────┘
                                                                  │
                                                                  │ 1
                                                                  │
                                                                  │
  ┌───────────────────────────────┐                               │
  │         RESERVATION           │                               │
  ├───────────────────────────────┤                               │
  │ PK RESERVE_NO         VC(10)  │                               │
  │    RESERVE_DATE         DATE  │                               │
  │    TOTAL_FARE            INT  │                               │
  │    REP_FAMILY_NAME    VC(10)  │                               │
  │    REP_GIVEN_NAME     VC(10)  │                               │
  │    REP_AGE               INT  │                               │
  │    REP_GENDER          VC(1)  │                               │
  │    REP_TEL            VC(13)  │                               │
  │    REP_MAIL          VC(256)  │                               │
  │ FK REP_CUSTOMER_NO    VC(10)  │──► MEMBER (optional)          │
  └───────────────┬───────────────┘                               │
                  │                                               │
                  │ 1                                             │
                  │                                               │
                  ▼ N                                             ▼ N
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                           RESERVE_FLIGHT                                  │
  ├───────────────────────────────────────────────────────────────────────────┤
  │ PK RESERVE_FLIGHT_NO                                              INT     │
  │ FK RESERVE_NO                                                    VC(10)   │──► RESERVATION
  │ FK DEPARTURE_DATE + FLIGHT_NAME + BOARDING_CLASS_CD + FARE_TYPE_CD        │──► FLIGHT (composite FK)
  │    DEPARTURE_DATE                                                 DATE    │
  │    FLIGHT_NAME                                                   VC(6)    │
  │    BOARDING_CLASS_CD                                             VC(1)    │
  │    FARE_TYPE_CD                                                  VC(4)    │
  └───────────────────────────────────────┬───────────────────────────────────┘
                                          │
                                          │ 1
                                          │
                                          ▼ N
              ┌───────────────────────────────────────────────────┐
              │                    PASSENGER                      │
              ├───────────────────────────────────────────────────┤
              │ PK PASSENGER_NO                            INT    │
              │ FK RESERVE_FLIGHT_NO                       INT    │──► RESERVE_FLIGHT
              │    FAMILY_NAME                           VC(10)   │
              │    GIVEN_NAME                            VC(10)   │
              │    AGE                                     INT    │
              │    GENDER                                 VC(1)   │
              │ FK CUSTOMER_NO                           VC(10)   │──► MEMBER (optional)
              └───────────────────────────────────────────────────┘


  ┌───────────────────────────────┐
  │         PEAK_TIME             │  (Standalone - no FKs)
  ├───────────────────────────────┤
  │ PK PEAK_TIME_CD       VC(10)  │
  │ PK PEAK_START_DATE      DATE  │
  │ PK PEAK_END_DATE        DATE  │
  │    MULTIPLICATION_RATIO  INT  │
  └───────────────────────────────┘
```

## Legend

| Symbol | Meaning |
|--------|---------|
| PK | Primary Key |
| FK | Foreign Key |
| VC(n) | VARCHAR(n) |
| INT | INTEGER |
| ──► | Foreign Key Reference |
| 1 | One side of relationship |
| N | Many side of relationship |

## Relationship Summary

| Parent Table | Child Table | Relationship | FK Column(s) |
|--------------|-------------|--------------|--------------|
| MEMBER | MEMBER_LOGIN | 1:1 | CUSTOMER_NO |
| MEMBER | RESERVATION | 1:N | REP_CUSTOMER_NO |
| MEMBER | PASSENGER | 1:N | CUSTOMER_NO |
| CREDIT_TYPE | MEMBER | 1:N | CREDIT_TYPE_CD |
| AIRPORT | ROUTE | 1:N | DEP_AIRPORT_CD |
| AIRPORT | ROUTE | 1:N | ARR_AIRPORT_CD |
| ROUTE | FLIGHT_MASTER | 1:N | ROUTE_NO |
| PLANE | FLIGHT_MASTER | 1:N | CRAFT_TYPE |
| FLIGHT_MASTER | FLIGHT | 1:N | FLIGHT_NAME |
| BOARDING_CLASS | FLIGHT | 1:N | BOARDING_CLASS_CD |
| FARE_TYPE | FLIGHT | 1:N | FARE_TYPE_CD |
| RESERVATION | RESERVE_FLIGHT | 1:N | RESERVE_NO |
| FLIGHT | RESERVE_FLIGHT | 1:N | Composite (4 cols) |
| RESERVE_FLIGHT | PASSENGER | 1:N | RESERVE_FLIGHT_NO |

## Sequences

| Sequence | Purpose |
|----------|---------|
| SQ_MEMBER_1 | MEMBER.CUSTOMER_NO |
| SQ_RESERVATION_1 | RESERVATION.RESERVE_NO |
| SQ_RESERVE_FLIGHT_1 | RESERVE_FLIGHT.RESERVE_FLIGHT_NO |
| SQ_PASSENGER_1 | PASSENGER.PASSENGER_NO |

## Schema Location

`atrs-initdb/src/sqls/integration-test-postgres/00100_create_all_tables.sql`
