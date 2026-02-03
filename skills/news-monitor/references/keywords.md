# Keyword Tracking

Keywords and phrases used to identify relevant federal buyout news.

## High-Priority Keywords (Weight: 10)

These trigger immediate alerts when found in article titles:

- VSIP (Voluntary Separation Incentive Payment)
- Voluntary Separation Incentive
- Federal buyout
- Federal employee buyout
- Early retirement
- Voluntary Early Retirement (VER)
- Buyout offer
- Separation incentive

## Medium-Priority Keywords (Weight: 5)

These contribute to relevance scoring:

- Federal workforce reduction
- Reduction in Force (RIF)
- Federal layoffs
- Federal employee severance
- Workforce restructuring
- Federal downsizing
- Federal employee departure
- Federal retirement surge
- Federal attrition
- Federal hiring freeze
- Federal job cuts
- Federal position elimination

## Context Keywords (Weight: 3)

These add context and boost scores when combined with priority keywords:

- Federal employee
- Government worker
- Civil service
- Federal agency
- OPM (Office of Personnel Management)
- Federal budget
- Government spending
- Federal compensation
- Federal benefits
- FERS (Federal Employees Retirement System)
- CSRS (Civil Service Retirement System)
- TSP (Thrift Savings Plan)
- Federal pension

## Agency-Specific Terms (Weight: 2)

Relevant when discussing specific agencies:

- VA (Veterans Affairs)
- DOD (Department of Defense)
- DHS (Department of Homeland Security)
- USPS (Postal Service)
- IRS (Internal Revenue Service)
- SSA (Social Security Administration)
- USDA (Agriculture)
- EPA (Environmental Protection Agency)

## Exclusion Keywords

Articles containing these are deprioritized or excluded:

- Private sector buyout
- Corporate buyout
- Private equity
- Defense contractor
- "state employee" (not federal)
- "municipal employee"
- "county worker"

## Relevance Scoring Formula

```
Base Score = 0

Title matches:
  High-priority: +30 per match
  Medium-priority: +15 per match
  Context: +5 per match

Content matches:
  High-priority: +10 per match
  Medium-priority: +5 per match
  Context: +2 per match

Source bonus:
  High-priority source: +10
  Medium-priority source: +5
  Low-priority source: +2

Recency bonus:
  < 1 hour: +5
  < 4 hours: +3
  < 24 hours: +1

Deductions:
  Exclusion keyword: -20 per match
  Already alerted: -100 (skip)

Final Score = min(100, max(0, calculated_score))
```

## Alert Thresholds

| Score | Action |
|-------|--------|
| 70-100 | Immediate alert + social share prompt |
| 40-69 | Daily digest inclusion |
| 20-39 | Weekly digest inclusion |
| 0-19 | Track only (no notification) |

## Keyword Updates

Review and update keywords monthly based on:
- New terminology in federal workforce news
- User feedback on false positives/negatives
- Changes in federal HR terminology
- Emerging topics (e.g., new legislation)

Last reviewed: 2026-02-03
