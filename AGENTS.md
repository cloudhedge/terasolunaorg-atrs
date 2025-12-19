# AGENTS.md

## Build & Test Commands
```bash
cd JavaConfig-JSP/atrs/              # or any variant (XMLConfig-JSP, JavaConfig-Thymeleaf, XMLConfig-Thymeleaf)
mvn clean install                    # Build all modules
mvn test                             # Run all tests
mvn test -pl atrs-domain             # Test single module
mvn test -Dtest=TicketSearchServiceImplTest  # Run single test class
mvn sql:execute -f atrs-initdb/pom.xml       # Init DB (PostgreSQL: db=atrs, user/pass=postgres)
mvn cargo:run -pl atrs-web           # Run at http://localhost:8080/atrs/
```

## Code Style
- **Java 17**, Spring MVC, MyBatis, MapStruct, TERASOLUNA Framework
- **Imports**: java.* first, then org.*, then jakarta.*, then jp.co.ntt.* (project classes last)
- **DI**: Use `@Inject` (Jakarta), not `@Autowired`. Field injection preferred
- **Services**: Interface + `*Impl` class pattern. Use `@Service` + `@Transactional`
- **Controllers**: `@Controller` + `@RequestMapping`. Return view names like `"B1/flightSearch"`
- **Validation**: Use `Assert.notNull()` for preconditions. Custom validators extend `Validator`
- **Exceptions**: Extend `RuntimeException`. Use `AtrsBusinessException` for business errors with error codes
- **Naming**: PascalCase classes, camelCase methods/fields. Feature packages use codes: a0-a2 (auth), b0-b2 (tickets), c0-c2 (members), d1 (history)
- **DTOs**: Suffix with `Dto` (e.g., `TicketSearchCriteriaDto`). Use `*Form` for web layer input
- **Comments**: Japanese Javadoc. Include `@author` tag
