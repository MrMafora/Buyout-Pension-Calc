---
name: config-manager
description: Manage OpenClaw configuration, environment variables, and settings
author: OpenClaw
version: 1.0.0
requires: []
---

# config-manager

A comprehensive skill for managing OpenClaw configuration files, environment variables, and settings with backup/restore capabilities and profile switching.

## Features

- **View Configuration**: Display current OpenClaw configuration
- **Update Config**: Safely modify configuration values
- **Environment Variables**: Manage env vars and .env files
- **Backup/Restore**: Create and restore configuration backups
- **Validation**: Validate configuration files for errors
- **Profile Switching**: Switch between different config profiles
- **Secret Management**: Securely handle sensitive values in .env files
- **Documentation**: Auto-generate config documentation

## Installation

Place this skill in your skills directory:
```bash
/root/.openclaw/workspace/skills/config-manager/
```

## Usage

### View Configuration

```bash
# View entire configuration
./skills/config-manager/scripts/config-view.sh

# View specific section
./skills/config-manager/scripts/config-view.sh --section browser

# View as JSON
./skills/config-manager/scripts/config-view.sh --format json
```

### Update Configuration

```bash
# Update a config value
./skills/config-manager/scripts/config-update.sh --key "browser.headless" --value "false"

# Update using JSON path
./skills/config-manager/scripts/config-update.sh --path "$.browser.timeout" --value "30000"
```

### Environment Variables

```bash
# View all environment variables
./skills/config-manager/scripts/env-manager.sh --list

# Set environment variable
./skills/config-manager/scripts/env-manager.sh --set "API_KEY" "secret123"

# Load from .env file
./skills/config-manager/scripts/env-manager.sh --load ".env.production"

# Unset variable
./skills/config-manager/scripts/env-manager.sh --unset "API_KEY"
```

### Backup and Restore

```bash
# Create backup
./skills/config-manager/scripts/backup.sh --create

# Create named backup
./skills/config-manager/scripts/backup.sh --create --name "before-migration"

# List backups
./skills/config-manager/scripts/backup.sh --list

# Restore from backup
./skills/config-manager/scripts/backup.sh --restore "backup-2024-01-15"

# Restore to specific file
./skills/config-manager/scripts/backup.sh --restore "backup-2024-01-15" --target "/path/to/openclaw.json"
```

### Validate Configuration

```bash
# Validate current config
./skills/config-manager/scripts/validate.sh

# Validate specific file
./skills/config-manager/scripts/validate.sh --file "/path/to/openclaw.json"

# Validate with strict mode
./skills/config-manager/scripts/validate.sh --strict
```

### Profile Management

```bash
# List available profiles
./skills/config-manager/scripts/profile.sh --list

# Switch to profile
./skills/config-manager/scripts/profile.sh --switch "production"

# Create new profile
./skills/config-manager/scripts/profile.sh --create "staging"

# Copy existing profile
./skills/config-manager/scripts/profile.sh --copy "default" "development"

# Delete profile
./skills/config-manager/scripts/profile.sh --delete "old-profile"
```

### Secret Management

```bash
# Create .env file from template
./skills/config-manager/scripts/secrets.sh --init

# Encrypt .env file
./skills/config-manager/scripts/secrets.sh --encrypt ".env"

# Decrypt .env file
./skills/config-manager/scripts/secrets.sh --decrypt ".env.enc"

# Rotate secrets
./skills/config-manager/scripts/secrets.sh --rotate

# Check for exposed secrets
./skills/config-manager/scripts/secrets.sh --scan
```

### Generate Documentation

```bash
# Generate config documentation
./skills/config-manager/scripts/docs.sh --generate

# Generate with examples
./skills/config-manager/scripts/docs.sh --generate --examples

# Output to file
./skills/config-manager/scripts/docs.sh --generate --output "CONFIG.md"
```

## Configuration File Locations

The skill looks for configuration files in the following order:

1. `$OPENCLAW_CONFIG` - Environment variable override
2. `./openclaw.json` - Current directory
3. `~/.openclaw/config.json` - User home directory
4. `/etc/openclaw/config.json` - System-wide config

## Profile Directory Structure

```
~/.openclaw/
├── config.json              # Active configuration
├── profiles/
│   ├── default/
│   │   └── openclaw.json
│   ├── production/
│   │   └── openclaw.json
│   └── development/
│       └── openclaw.json
└── backups/
    ├── backup-2024-01-15-120000.json
    └── backup-2024-01-14-090000.json
```

## Environment Variables

The following environment variables affect this skill:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENCLAW_CONFIG` | Path to config file | `./openclaw.json` |
| `OPENCLAW_PROFILE` | Active profile name | `default` |
| `OPENCLAW_BACKUP_DIR` | Backup directory | `~/.openclaw/backups` |
| `CONFIG_MANAGER_EDITOR` | Editor for interactive mode | `$EDITOR` or `nano` |

## Safety Features

- **Automatic Backups**: Creates backup before any destructive operation
- **Validation**: Validates JSON syntax before saving
- **Confirmation**: Prompts before overwriting existing files
- **Dry Run**: `--dry-run` flag to preview changes
- **Audit Log**: Logs all configuration changes

## Examples

### Setup Development Environment

```bash
# Create development profile
./skills/config-manager/scripts/profile.sh --create "development"

# Switch to it
./skills/config-manager/scripts/profile.sh --switch "development"

# Configure for development
./skills/config-manager/scripts/config-update.sh --key "browser.headless" --value "false"
./skills/config-manager/scripts/config-update.sh --key "log.level" --value "debug"
```

### Production Deployment

```bash
# Create production profile
./skills/config-manager/scripts/profile.sh --copy "default" "production"

# Switch to production
./skills/config-manager/scripts/profile.sh --switch "production"

# Set production values
./skills/config-manager/scripts/config-update.sh --key "browser.headless" --value "true"
./skills/config-manager/scripts/config-update.sh --key "log.level" --value "warn"

# Validate before deploy
./skills/config-manager/scripts/validate.sh --strict
```

### Secure Secret Management

```bash
# Initialize secrets
./skills/config-manager/scripts/secrets.sh --init

# Add secrets
./skills/config-manager/scripts/env-manager.sh --set "DATABASE_URL" "postgres://..."
./skills/config-manager/scripts/env-manager.sh --set "API_SECRET" "supersecret"

# Encrypt for storage
./skills/config-manager/scripts/secrets.sh --encrypt ".env"

# Scan for accidental commits
./skills/config-manager/scripts/secrets.sh --scan
```

## Troubleshooting

### Config file not found

```bash
# Initialize default config
./skills/config-manager/scripts/config-view.sh --init
```

### Invalid JSON

```bash
# Validate and fix
./skills/config-manager/scripts/validate.sh --fix
```

### Permission denied

```bash
# Fix permissions
chmod 600 ~/.openclaw/config.json
chmod 700 ~/.openclaw/
```

## License

MIT - Part of OpenClaw Skills Collection
