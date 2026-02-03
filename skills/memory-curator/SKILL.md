---
name: memory-curator
description: Manage OpenClaw memory files - organize daily logs, curate MEMORY.md, archive old files, and maintain long-term memory. Use for memory maintenance, extracting important events, consolidating duplicates, and generating summaries.
---

# Memory Curator

Manage and maintain OpenClaw's memory system for optimal long-term context retention.

## Quick Start

```bash
# Review recent memory files and suggest MEMORY.md updates
python3 /root/.openclaw/workspace/skills/memory-curator/scripts/review-recent.py

# Archive old daily memory files
python3 /root/.openclaw/workspace/skills/memory-curator/scripts/archive-old.py --days 30

# Generate memory summary
python3 /root/.openclaw/workspace/skills/memory-curator/scripts/generate-summary.py --days 7

# Full memory maintenance (run during heartbeat)
python3 /root/.openclaw/workspace/skills/memory-curator/scripts/full-maintenance.py
```

## Memory System Overview

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `memory/YYYY-MM-DD.md` | Daily raw logs | Daily |
| `MEMORY.md` | Curated long-term memory | Weekly/Monthly |
| `memory/archive/` | Archived daily files | Monthly |

## When to Use This Skill

**Use memory-curator when:**
- Heartbeat maintenance cycle triggers memory review
- Daily logs are accumulating and need organization
- MEMORY.md needs updating with recent significant events
- Old memory files need archiving
- You need to extract insights from recent activity

**Memory tags to look for:**
- `[DECISION]` - Important decisions made
- `[EVENT]` - Significant occurrences
- `[LESSON]` - Learnings and insights
- `[PROJECT]` - Project milestones
- `[MEETING]` - Important conversations

## Maintenance Workflows

### Weekly Review (Recommended)

1. **Review recent daily files**
   ```bash
   python3 /root/.openclaw/workspace/skills/memory-curator/scripts/review-recent.py --days 7
   ```

2. **Extract important entries**
   - Look for tags: [DECISION], [EVENT], [LESSON], [PROJECT]
   - Identify patterns and recurring themes
   - Note completed projects

3. **Update MEMORY.md**
   - Add significant events to appropriate sections
   - Consolidate duplicate information
   - Remove outdated entries

4. **Archive old files**
   ```bash
   python3 /root/.openclaw/workspace/skills/memory-curator/scripts/archive-old.py --days 30
   ```

### Full Maintenance (Monthly)

```bash
# Run complete maintenance cycle
python3 /root/.openclaw/workspace/skills/memory-curator/scripts/full-maintenance.py
```

This will:
- Review all daily files from the past month
- Update MEMORY.md with consolidated entries
- Archive files older than 30 days
- Generate summary report
- Clean up obsolete entries

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `review-recent.py` | Review recent daily files | `review-recent.py [--days N]` |
| `extract-important.py` | Extract tagged entries | `extract-important.py [--days N] [--tag TAG]` |
| `archive-old.py` | Archive old memory files | `archive-old.py [--days N]` |
| `generate-summary.py` | Generate summary report | `generate-summary.py [--days N]` |
| `cleanup-memory.py` | Clean MEMORY.md obsolete entries | `cleanup-memory.py [--dry-run]` |
| `full-maintenance.py` | Run complete maintenance | `full-maintenance.py [--days N]` |

## Tagging Conventions

When reviewing memory files, look for these standard tags:

- `[DECISION: <topic>]` - Record of decisions with context
- `[EVENT: <name>]` - Significant events worth remembering
- `[LESSON: <topic>]` - Insights and learnings
- `[PROJECT: <name>]` - Project milestones and updates
- `[MEETING: <who>]` - Important conversations
- `[MILESTONE]` - Achievements and completions
- `[TODO]` - Action items (should be completed/removed)

## MEMORY.md Structure

Maintain MEMORY.md with these sections:

```markdown
## Key Decisions
- Decision details with context and date

## Active Projects
- Current projects with status and notes

## Important Events
- Significant occurrences with impact

## Lessons Learned
- Insights and knowledge gained

## Contacts & Relationships
- Key people and context

## Preferences
- User preferences and settings
```

## Automation

Add to `HEARTBEAT.md` for automated maintenance:

```markdown
- [ ] Memory maintenance (weekly)
  - Run: `python3 /root/.openclaw/workspace/skills/memory-curator/scripts/full-maintenance.py`
```

## Manual Memory Curation Tips

1. **Quality over quantity** - Only keep significant events
2. **Add context** - Include "why" not just "what"
3. **Be specific** - Dates, names, and concrete details
4. **Link related entries** - Cross-reference when relevant
5. **Review regularly** - Outdated info loses value

## See Also

- [references/memory-format.md](references/memory-format.md) - Memory file format specification
- [references/tagging-guide.md](references/tagging-guide.md) - Complete tagging conventions
