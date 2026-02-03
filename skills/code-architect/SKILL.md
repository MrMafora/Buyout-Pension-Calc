---
name: code-architect
description: "Tools for maintaining codebase quality, structure analysis, and documentation generation."
version: 1.0.0
author: OpenClaw
---

# Code Architect Skill

This skill provides utilities for analyzing and maintaining codebases. It helps with generating project structure maps, analyzing dependencies, and automating documentation.

## Usage

### 1. Generate Project Structure Map
Generates a tree-like structure of the codebase, ignoring common ignore files.

```bash
/root/.openclaw/workspace/skills/code-architect/scripts/map_structure.sh [path]
```

### 2. Analyze Dependencies
Scans package files (package.json, requirements.txt, etc.) to list dependencies.

```bash
/root/.openclaw/workspace/skills/code-architect/scripts/analyze_deps.sh [path]
```

### 3. Check Code Style
Runs basic style checks (linting pointers) or identifies potential style issues.

```bash
/root/.openclaw/workspace/skills/code-architect/scripts/check_style.sh [path]
```

### 4. Auto-Generate Documentation Stub
Generates a rough README.md structure based on file analysis.

```bash
/root/.openclaw/workspace/skills/code-architect/scripts/gen_docs.sh [path]
```
