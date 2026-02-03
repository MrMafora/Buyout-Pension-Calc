---
name: skill-manager
description: Manage OpenClaw skills - install, update, package, and organize skills. Use for skill operations, validation, packaging, and dependency management.
---

# Skill Manager for OpenClaw

A comprehensive skill management system for installing, updating, packaging, and organizing OpenClaw skills.

## Key Features

- **List Installed Skills** - View all skills with metadata and status
- **Validate Skill Structure** - Check skill integrity and requirements
- **Package Skills** - Create distributable .skill files
- **Install Skills** - Install from .skill files or git repositories
- **Update Registry** - Maintain skill registry and index
- **Dependency Checking** - Verify and resolve skill dependencies
- **Browse Documentation** - Read skill docs without loading

## Quick Start

### List All Installed Skills
```bash
python3 /root/.openclaw/workspace/skills/skill-manager/scripts/skill-manager.py list
```

### Validate a Skill
```bash
python3 /root/.openclaw/workspace/skills/skill-manager/scripts/skill-manager.py validate --skill blog-writer
```

### Package a Skill
```bash
python3 /root/.openclaw/workspace/skills/skill-manager/scripts/skill-manager.py package --skill blog-writer --output ./my-skill.skill
```

### Install a Skill
```bash
python3 /root/.openclaw/workspace/skills/skill-manager/scripts/skill-manager.py install --file ./my-skill.skill
```

### Update Skill Registry
```bash
python3 /root/.openclaw/workspace/skills/skill-manager/scripts/skill-manager.py registry-update
```

### Check Dependencies
```bash
python3 /root/.openclaw/workspace/skills/skill-manager/scripts/skill-manager.py deps --skill email-campaigns
```

### Browse Skill Documentation
```bash
python3 /root/.openclaw/workspace/skills/skill-manager/scripts/skill-manager.py docs --skill blog-writer
```

## Commands Reference

### list
List all installed skills with their metadata.

Options:
- `--format {table,json}` - Output format (default: table)
- `--filter <keyword>` - Filter by name or description

```bash
# List all skills
python3 scripts/skill-manager.py list

# List as JSON
python3 scripts/skill-manager.py list --format json

# Filter skills
python3 scripts/skill-manager.py list --filter "email"
```

### validate
Validate skill structure and integrity.

Options:
- `--skill <name>` - Skill to validate
- `--all` - Validate all skills
- `--strict` - Strict validation (fail on warnings)

```bash
# Validate single skill
python3 scripts/skill-manager.py validate --skill blog-writer

# Validate all skills
python3 scripts/skill-manager.py validate --all

# Strict validation
python3 scripts/skill-manager.py validate --skill blog-writer --strict
```

Validation checks:
- SKILL.md exists and has valid frontmatter
- Required directories exist (scripts/, if referenced)
- Script files are executable
- No broken references
- Dependencies are satisfied

### package
Package a skill into a distributable .skill file.

Options:
- `--skill <name>` - Skill to package
- `--output <path>` - Output file path
- `--include-registry` - Include in local registry

```bash
# Package skill
python3 scripts/skill-manager.py package --skill blog-writer --output ./blog-writer-v1.0.skill

# Package and register
python3 scripts/skill-manager.py package --skill blog-writer --include-registry
```

Packaging includes:
- SKILL.md and all referenced files
- scripts/ directory contents
- assets/ directory (if exists)
- templates/ directory (if exists)
- Metadata manifest

### install
Install a skill from a .skill file.

Options:
- `--file <path>` - Path to .skill file
- `--url <url>` - URL to download .skill file
- `--git <url>` - Git repository URL
- `--force` - Overwrite existing skill
- `--deps` - Install dependencies automatically

```bash
# Install from file
python3 scripts/skill-manager.py install --file ./blog-writer-v1.0.skill

# Install from URL
python3 scripts/skill-manager.py install --url https://example.com/skills/blog-writer.skill

# Install from git
python3 scripts/skill-manager.py install --git https://github.com/user/skill-repo.git

# Force reinstall
python3 scripts/skill-manager.py install --file ./blog-writer.skill --force
```

### uninstall
Remove an installed skill.

Options:
- `--skill <name>` - Skill to uninstall
- `--keep-data` - Keep data and config files

```bash
# Uninstall skill
python3 scripts/skill-manager.py uninstall --skill old-skill

# Uninstall but keep data
python3 scripts/skill-manager.py uninstall --skill old-skill --keep-data
```

### update
Update an installed skill.

Options:
- `--skill <name>` - Skill to update
- `--all` - Update all skills
- `--check` - Check for updates only

```bash
# Update single skill
python3 scripts/skill-manager.py update --skill blog-writer

# Check all for updates
python3 scripts/skill-manager.py update --all --check

# Update all skills
python3 scripts/skill-manager.py update --all
```

### registry-update
Update the local skill registry index.

Options:
- `--add <path>` - Add a skill to registry
- `--remove <name>` - Remove from registry
- `--sync <url>` - Sync with remote registry

```bash
# Update registry from installed skills
python3 scripts/skill-manager.py registry-update

# Sync with remote
python3 scripts/skill-manager.py registry-update --sync https://skills.openclaw.dev/registry.json
```

### deps (dependencies)
Check and manage skill dependencies.

Options:
- `--skill <name>` - Check dependencies for skill
- `--install` - Install missing dependencies
- `--tree` - Show dependency tree

```bash
# Check dependencies
python3 scripts/skill-manager.py deps --skill email-campaigns

# Show dependency tree
python3 scripts/skill-manager.py deps --skill email-campaigns --tree

# Install missing deps
python3 scripts/skill-manager.py deps --skill email-campaigns --install
```

### docs
Browse skill documentation.

Options:
- `--skill <name>` - Show docs for skill
- `--search <query>` - Search in documentation
- `--section <name>` - Jump to section

```bash
# Show skill docs
python3 scripts/skill-manager.py docs --skill blog-writer

# Search docs
python3 scripts/skill-manager.py docs --skill blog-writer --search "SEO"

# Show specific section
python3 scripts/skill-manager.py docs --skill blog-writer --section "Quick Start"
```

### search
Search for skills in registry.

Options:
- `--query <text>` - Search query
- `--tag <tag>` - Filter by tag
- `--source {local,remote,all}` - Search scope

```bash
# Search skills
python3 scripts/skill-manager.py search --query "email"

# Search by tag
python3 scripts/skill-manager.py search --tag "marketing"
```

### create
Create a new skill from template.

Options:
- `--name <name>` - Skill name
- `--description <text>` - Skill description
- `--template <name>` - Template to use

```bash
# Create new skill
python3 scripts/skill-manager.py create --name my-new-skill --description "Does cool things"

# Use specific template
python3 scripts/skill-manager.py create --name my-new-skill --template python
```

## Skill File Format (.skill)

A .skill file is a tar.gz archive containing:

```
skill-name/
├── SKILL.md              # Main documentation with frontmatter
├── manifest.json         # Package metadata
├── scripts/              # Executable scripts (optional)
├── assets/               # Assets and templates (optional)
└── README.md            # Additional documentation (optional)
```

### Manifest Format

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "What this skill does",
  "author": "Author Name",
  "license": "MIT",
  "minOpenclawVersion": "1.0.0",
  "dependencies": [
    "other-skill >= 1.0.0"
  ],
  "tags": ["productivity", "automation"],
  "entryPoint": "scripts/main.py"
}
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name
description: Brief description for skill discovery
version: 1.0.0
author: Author Name
tags: [tag1, tag2]
dependencies: [other-skill]
---
```

## Skill Structure Requirements

### Minimum Valid Skill
```
skill-name/
└── SKILL.md          # Required, with frontmatter
```

### Standard Skill Structure
```
skill-name/
├── SKILL.md          # Required
├── scripts/          # Recommended
│   └── main.py
├── assets/           # Optional
│   └── templates/
└── references/       # Optional
    └── guide.md
```

## Best Practices

### For Skill Authors

1. **Always include SKILL.md** with proper frontmatter
2. **Version your skills** using semantic versioning
3. **Document dependencies** clearly
4. **Use descriptive names** without "skill-" prefix
5. **Test before packaging** - validate your skill
6. **Include examples** in documentation
7. **Keep scripts executable** with proper shebangs

### For Skill Users

1. **Validate before installing** - check skill integrity
2. **Review dependencies** - know what you're installing
3. **Test in isolation** - try new skills on test data
4. **Keep backups** - before major updates
5. **Read the docs** - understand what a skill does

### For Skill Distribution

1. **Use semantic versioning** (MAJOR.MINOR.PATCH)
2. **Sign your packages** when possible
3. **Include changelog** in SKILL.md
4. **Support uninstall cleanly** - no orphaned files
5. **Document requirements** - Python version, dependencies

## Configuration

Skill manager stores configuration in:

```
/root/.openclaw/workspace/skills/skill-manager/config.json
```

Default configuration:

```json
{
  "skillsDir": "/root/.openclaw/workspace/skills",
  "registryPath": "/root/.openclaw/workspace/skills/skill-manager/registry.json",
  "defaultTemplate": "basic",
  "autoInstallDeps": false,
  "strictValidation": false,
  "backupOnUpdate": true
}
```

## Troubleshooting

### Skill Won't Install

1. Check file permissions: `ls -la skill-file.skill`
2. Validate the .skill file: `skill-manager.py validate --file ...`
3. Check for dependency conflicts
4. Use `--force` to overwrite existing

### Validation Failures

1. Missing SKILL.md - create with proper frontmatter
2. Invalid frontmatter - check YAML syntax
3. Broken references - verify all linked files exist
4. Missing scripts - ensure referenced scripts exist

### Dependency Issues

1. Run `deps --tree` to see full dependency chain
2. Install dependencies manually first
3. Check version compatibility
4. Use `--install` flag to auto-resolve

### Registry Problems

1. Rebuild registry: `registry-update`
2. Check registry file exists and is valid JSON
3. Sync with remote: `registry-update --sync <url>`

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `skill-manager.py` | Main CLI interface |
| `skill-packager.py` | Create .skill packages |
| `skill-validator.py` | Validate skill structure |
| `registry-manager.py` | Manage skill registry |
| `dependency-checker.py` | Check and resolve deps |
| `doc-browser.py` | Browse skill documentation |
| `skill-creator.py` | Create new skills from templates |

## Resources

- [templates/basic/](templates/basic/) - Basic skill template
- [templates/python/](templates/python/) - Python skill template
- [assets/schemas/](assets/schemas/) - JSON schemas for validation
- [registry.json](registry.json) - Local skill registry
