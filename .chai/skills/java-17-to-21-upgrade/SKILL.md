---
name: Java 17 to 21 Upgrade
description: Upgrade Maven Java projects from Java 17 to 21
triggers:
  - upgrade to java 21
  - java 21 upgrade
  - upgrade java version
  - update java to 21
---

# Java 17 → 21 Upgrade Skill

Automates Java version upgrade in Maven projects.

## Workflow

### Step 1: Find POM Files

Search for all `pom.xml` files containing `<java-version>` property:

```bash
grep -r "<java-version>" --include="pom.xml" .
```

### Step 2: Update Java Version

For each pom.xml found, change:
```xml
<java-version>17</java-version>
```
To:
```xml
<java-version>21</java-version>
```

### Step 3: Report Changes

After updating, output a summary table:

| File | Status |
|------|--------|
| path/to/pom.xml | Updated 17 → 21 |

### Step 4: Provide Runtime Switch Command

Output the jenv command to switch runtime:

```bash
jenv local 21
java -version  # Verify switch
```

## Target Files

| File | Change |
|------|--------|
| `JavaConfig-JSP/atrs/pom.xml` | 17 → 21 |
| `JavaConfig-Thymeleaf/atrs/pom.xml` | 17 → 21 |
| `XMLConfig-JSP/atrs/pom.xml` | 17 → 21 |
| `XMLConfig-Thymeleaf/atrs/pom.xml` | 17 → 21 |

## Verification

After upgrade, verify with:
```bash
mvn clean compile
```

## References

- [POM Changes Reference](references/pom-changes.md)
