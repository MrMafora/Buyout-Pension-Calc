# Memory File Format Specification

## Daily Memory Files

**Location:** `memory/YYYY-MM-DD.md`

**Format:**
```markdown
# 2024-01-15 - Monday

## Morning
- [EVENT: System Setup] Initial configuration completed
- Met with team to discuss project roadmap

## Afternoon
- [DECISION: Architecture] Chose PostgreSQL over MySQL for primary datastore
  - Reason: Better JSON support for our use case
  - Context: Evaluated both for 2 days
- [LESSON: Database] JSONB queries are faster than expected

## Evening
- Deployed v2.1 to production
- [MILESTONE] 1000 active users reached!
```

## MEMORY.md Format

**Location:** `MEMORY.md`

**Format:**
```markdown
# Long-Term Memory

## Key Decisions
| Date | Decision | Context | Status |
|------|----------|---------|--------|
| 2024-01-15 | PostgreSQL as primary DB | JSON support needs | Active |

## Active Projects
| Project | Started | Status | Notes |
|---------|---------|--------|-------|
| API Rewrite | 2024-01-10 | In Progress | 60% complete |

## Important Events
- **2024-01-15**: Hit 1000 users milestone
- **2024-01-10**: Launched v2.0 with new UI

## Lessons Learned
- Database JSONB performance exceeds expectations (2024-01-15)
- Early user feedback is invaluable

## Contacts & Relationships
- **John Doe** - Tech lead, prefers async communication

## Preferences
- User likes concise summaries
- Prefer bullet points over paragraphs
```

## Archive Format

**Location:** `memory/archive/YYYY-MM/`

Archived files maintain original format but are moved to monthly folders for organization.
