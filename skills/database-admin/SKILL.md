---
name: database-admin
description: PostgreSQL database management skill for backups, migrations, monitoring, and user management.
version: 1.0.0
author: OpenClaw
---

# Database Admin Skill

This skill provides a suite of tools for managing PostgreSQL databases. It includes functionality for automated backups, safe migrations, query monitoring, maintenance tasks, and user management.

## Prerequisites

- PostgreSQL client tools (`psql`, `pg_dump`, `pg_restore`) must be installed on the system.
- Database connection string or credentials should be available via environment variables (e.g., `DATABASE_URL` or `PGHOST`, `PGUSER`, etc.).

## Scripts

The following scripts are available in the `scripts/` directory:

### 1. `backup.sh`
Creates a backup of the specified database using `pg_dump`.
- **Usage:** `./scripts/backup.sh [database_name] [retention_days]`
- **Features:** Compresses output, rotates old backups based on retention policy.

### 2. `restore.sh`
Restores a database from a backup file.
- **Usage:** `./scripts/restore.sh [database_name] [backup_file]`
- **Safety:** Prompts for confirmation before overwriting data.

### 3. `monitor_queries.sh`
Lists active queries and optionally kills long-running ones.
- **Usage:** `./scripts/monitor_queries.sh [list|kill] [duration_threshold]`
- **Features:** Shows query duration, user, and SQL text.

### 4. `maintenance.sh`
Performs database maintenance tasks like VACUUM and ANALYZE.
- **Usage:** `./scripts/maintenance.sh [database_name] [full|analyze]`

### 5. `user_mgmt.sh`
Manages database users and permissions.
- **Usage:** `./scripts/user_mgmt.sh [create|drop|grant] [username] [database_name]`

### 6. `health_check.sh`
Checks database connectivity and basic health metrics.
- **Usage:** `./scripts/health_check.sh [database_name]`

### 7. `migrate.sh`
Runs SQL migration files safely within a transaction.
- **Usage:** `./scripts/migrate.sh [database_name] [migration_file]`

## Configuration

Set the following environment variables if not passing arguments directly:
- `PGHOST`: Database host
- `PGPORT`: Database port
- `PGUSER`: Database user
- `PGPASSWORD`: Database password (or use `.pgpass` file)
