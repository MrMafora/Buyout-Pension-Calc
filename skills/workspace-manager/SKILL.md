---
name: workspace-manager
description: Manage OpenClaw workspace environment - organize files, execute git workflows, cleanup old/temp files, backup important data, check workspace health, and create directory structures. Use when the user needs to organize their workspace, manage git operations, clean up files, create backups, check workspace health, or set up directory templates.
---

# Workspace Manager

This skill provides comprehensive workspace management for the OpenClaw environment.

## Capabilities

- **File Organization**: Sort files by type or project
- **Git Workflows**: Status, check, commit, push operations
- **Cleanup**: Remove old and temporary files
- **Backup**: Archive important files
- **Health Check**: Diagnose workspace issues
- **Templates**: Create standardized directory structures

## File Organization

Organize scattered files into a structured layout:

```bash
# Organize by file type
./scripts/organize-files.sh --by-type --source . --dest ./organized

# Organize by project (detects project roots)
./scripts/organize-files.sh --by-project --source . --dest ./projects
```

The organizer:
- Groups by extension (type mode) or detects project boundaries (project mode)
- Creates dated backup before moving
- Generates organization report

## Git Workflows

Execute standardized git operations:

```bash
# Full workflow: status → add → commit → push
./scripts/git-workflow.sh --commit "message" --push

# Check only: show status of all repos
./scripts/git-workflow.sh --check-all

# Commit with auto-generated message
./scripts/git-workflow.sh --auto-commit
```

Workflow steps:
1. Find all git repositories recursively
2. Check status (uncommitted changes, untracked files)
3. Stage and commit with message
4. Push to remote if specified

## Cleanup

Safely remove old and temporary files:

```bash
# Preview what would be deleted (dry run)
./scripts/cleanup.sh --dry-run --days 30

# Clean temp files, old logs, cache
./scripts/cleanup.sh --execute --days 30

# Target specific patterns
./scripts/cleanup.sh --execute --pattern "*.tmp" --pattern "*.log"
```

Cleanup targets:
- Files older than N days (default: 30)
- Common temp patterns (*.tmp, *.temp, .cache)
- Log files and build artifacts
- Empty directories

## Backup

Create timestamped backups of important files:

```bash
# Backup specific directories
./scripts/backup.sh --targets ./important --dest ./backups

# Backup with compression
./scripts/backup.sh --targets ./projects --compress

# List available backups
./scripts/backup.sh --list
```

Features:
- Timestamped archive names
- Optional compression (tar.gz)
- Excludes node_modules, .git, temp files
- Creates restore manifest

## Health Check

Diagnose workspace issues:

```bash
# Full diagnostic report
./scripts/health-check.sh --full

# Quick check
./scripts/health-check.sh --quick
```

Checks include:
- Disk space usage
- Large files (>100MB)
- Git repository status
- Duplicate files
- Permission issues
- Orphaned symlinks

## Directory Templates

Create standardized project structures:

```bash
# Web project structure
./scripts/create-structure.sh --template web --name my-project

# Python package structure
./scripts/create-structure.sh --template python --name my-package

# Documentation structure
./scripts/create-structure.sh --template docs --name my-docs

# List available templates
./scripts/create-structure.sh --list
```

Available templates:
- `web`: HTML/CSS/JS project
- `python`: Python package with tests
- `docs`: Documentation site structure
- `skill`: OpenClaw skill structure
- `empty`: Minimal structure

## Quick Reference

| Task | Command |
|------|---------|
| Organize files | `./scripts/organize-files.sh --by-type` |
| Git status check | `./scripts/git-workflow.sh --check-all` |
| Commit and push | `./scripts/git-workflow.sh --commit "msg" --push` |
| Clean old files | `./scripts/cleanup.sh --execute --days 30` |
| Create backup | `./scripts/backup.sh --targets ./dir --compress` |
| Health check | `./scripts/health-check.sh --quick` |
| New project | `./scripts/create-structure.sh --template web --name proj` |

## Safety Features

All scripts include:
- **Dry-run mode**: Preview changes before executing
- **Backups**: Automatic backup before destructive operations
- **Confirmation**: Prompt for destructive actions
- **Logging**: Operation logs for audit trail

Use `--help` with any script for detailed options.
