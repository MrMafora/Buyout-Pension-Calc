# Memory Tagging Guide

## Standard Tags

### [DECISION: <topic>]
Record important decisions with context.

```markdown
[DECISION: Tech Stack] Chose Node.js over Python for API
- Reason: Team expertise, ecosystem fit
- Alternatives considered: Python, Go, Rust
- Date: 2024-01-15
- Reversible: Yes, with ~2 week migration effort
```

### [EVENT: <name>]
Significant occurrences worth remembering.

```markdown
[EVENT: Production Outage] Database connection pool exhausted
- Duration: 15 minutes
- Impact: 500 error rate spike
- Resolution: Increased pool size, added monitoring
```

### [LESSON: <topic>]
Insights and knowledge gained.

```markdown
[LESSON: Caching] Redis significantly improves response times
- Before: ~200ms average
- After: ~20ms average
- Key learning: Cache invalidation is tricky
```

### [PROJECT: <name>]
Project milestones and updates.

```markdown
[PROJECT: Website Redesign] Phase 1 complete
- Delivered: New homepage, about page
- Next: Product pages, checkout flow
- Blockers: Waiting on design approval
```

### [MEETING: <who>]
Important conversations.

```markdown
[MEETING: Sarah - Product Manager] Q1 roadmap review
- Key points: Focus on mobile experience
- Action items: Prepare mobile audit report
- Follow-up: Schedule design sprint
```

### [MILESTONE]
Achievements and completions.

```markdown
[MILESTONE] 10,000 users registered!
- Took 3 months from launch
- Growth rate accelerating
```

### [TODO]
Action items (should be completed and removed).

```markdown
[TODO] Update API documentation
- Priority: High
- Due: 2024-01-20
```

## Tagging Best Practices

1. **Be consistent** - Use the same tag format throughout
2. **Add context** - Include relevant details after the tag
3. **Link related** - Cross-reference related entries
4. **Date important entries** - Helps with timeline reconstruction
5. **Review and clean** - Remove completed TODOs regularly

## Tag Hierarchy

```
[DECISION] → Permanent record, affects future choices
[EVENT]     → Significant occurrence, may have lasting impact
[LESSON]    → Knowledge to apply going forward
[PROJECT]   → Track progress over time
[MEETING]   → Relationship and commitment tracking
[MILESTONE] → Celebrate progress
[TODO]      → Temporary, remove when done
```
