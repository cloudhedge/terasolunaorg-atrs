# POM XML Changes Reference

## Java Version Property

### Before (Java 17)
```xml
<properties>
    <java-version>17</java-version>
</properties>
```

### After (Java 21)
```xml
<properties>
    <java-version>21</java-version>
</properties>
```

## Search Pattern

Find files to update:
```bash
grep -r "<java-version>17</java-version>" --include="pom.xml" .
```

## Edit Pattern

Replace in each file:
- **old_string:** `<java-version>17</java-version>`
- **new_string:** `<java-version>21</java-version>`

## Expected Files in ATRS Project

```
atrs/
├── JavaConfig-JSP/atrs/pom.xml
├── JavaConfig-Thymeleaf/atrs/pom.xml
├── XMLConfig-JSP/atrs/pom.xml
└── XMLConfig-Thymeleaf/atrs/pom.xml
```

## Java 21 Features (Optional Upgrades)

After upgrading, consider using:

| Feature | Description |
|---------|-------------|
| Record Patterns | Enhanced pattern matching for records |
| Virtual Threads | Lightweight concurrency (Project Loom) |
| Sequenced Collections | New collection interfaces |
| String Templates | Preview feature for string interpolation |

## Rollback

If needed, revert changes:
```bash
git checkout -- "*/pom.xml"
```
