# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is This

Airline Ticket Reservation System - Java/Spring demo app with 4 variants:
- **JavaConfig-JSP/** - Java config + JSP (recommended)
- **JavaConfig-Thymeleaf/** - Java config + Thymeleaf
- **XMLConfig-JSP/** - XML config + JSP
- **XMLConfig-Thymeleaf/** - XML config + Thymeleaf

## Build & Run

```bash
cd JavaConfig-JSP/atrs/   # or any variant

mvn clean install                        # Build
mvn sql:execute -f atrs-initdb/pom.xml   # Init DB (needs PostgreSQL: db=atrs, user=postgres, pass=postgres)
mvn cargo:run -pl atrs-web               # Run at http://localhost:8080/atrs/
```

## Where Things Are

Each variant has identical structure:
```
atrs/
├── atrs-web/       → Controllers (app/), REST APIs (api/), views
├── atrs-domain/    → Entities (model/), Services (service/), Repositories (repository/)
├── atrs-env/       → Config files
└── atrs-initdb/    → SQL init scripts
```

**Feature packages** use codes: `a0/a1/a2` (auth), `b0/b1/b2` (tickets), `c0/c1/c2` (members), `d1` (history)

## Tech Stack

Java 17, Spring MVC, MyBatis, MapStruct, PostgreSQL, TERASOLUNA Framework
