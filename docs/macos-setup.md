# ATRS macOS Setup Guide

Setup the Airline Ticket Reservation System (JavaConfig-JSP variant) on macOS.

---

## Step 1: Install Homebrew ✅

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## Step 2: Install Java 17 ✅

```bash
brew install openjdk@17
```

**Configure JAVA_HOME:**
```bash
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Verify:**
```bash
java -version   # Should show version 17.x.x
```

---

## Step 3: Install Maven ✅

```bash
brew install maven
```

**Verify:**
```bash
mvn -version   # Should show 3.x.x with Java 17
```

---

## Step 4: Install & Configure PostgreSQL ✅

```bash
brew install postgresql@14
brew services start postgresql@14
```

**Add to PATH:**
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Create database and postgres role:**
```bash
createdb atrs
psql -d postgres -c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';"
```

**Verify:**
```bash
psql -d atrs -c "SELECT 1;"
```

---

## Step 5: Update Config ✅

**File:** `JavaConfig-JSP/atrs/atrs-env/src/main/resources/META-INF/spring/atrs-infra.properties`

Update these values:
```properties
database.username=<your-macos-username>
report.dir=./reports/reservation
```

---

## Step 6: Build Project ✅

```bash
cd JavaConfig-JSP/atrs/
mvn clean install
```

---

## Step 7: Initialize Database Schema ✅

```bash
mvn sql:execute -f atrs-initdb/pom.xml
```

---

## Step 8: Run Application ✅

```bash
mvn cargo:run -pl atrs-web
```

---

## Step 9: Verify ✅

Open: http://localhost:8080/atrs/

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DB connection fails | Check PostgreSQL running, credentials in `atrs-infra.properties` |
| Port 8080 in use | `lsof -i :8080` then kill the process |
| Java version mismatch | Check `JAVA_HOME` points to JDK 17 |
| Maven build fails | Try `mvn clean install -DskipTests` |

---

## Key Files

| Purpose | Path |
|---------|------|
| DB config | `atrs-env/src/main/resources/META-INF/spring/atrs-infra.properties` |
| App settings | `atrs-domain/src/main/resources/META-INF/spring/atrs.properties` |
| Logging | `atrs-env/src/main/resources/logback.xml` |
