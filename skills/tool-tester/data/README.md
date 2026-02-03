# Test Results Directory

This directory stores test results and artifacts.

## Structure

```
data/test-results/
├── latest.json          # Most recent test results
├── history/             # Archived test results by date
│   ├── 20240115_090000.json
│   └── 20240116_090000.json
├── screenshots/         # Visual test captures
│   └── test-001.png
└── logs/                # Detailed test logs
    └── test-run-20240115_090000.log
```

## File Formats

### JSON Results (latest.json)

```json
{
  "timestamp": "20240115_090000",
  "date": "2024-01-15T09:00:00",
  "summary": {
    "total": 10,
    "passed": 9,
    "failed": 1,
    "skipped": 0
  },
  "results": {
    "Tools": {
      "status": "PASS",
      "duration": 5
    }
  }
}
```

### Log Files

Plain text logs containing detailed test output and error messages.

### Screenshots

PNG images captured during visual tests.

## Retention

- Latest results: Always kept
- History: 30 days (configurable)
- Logs: 30 days
- Screenshots: 7 days

## Manual Cleanup

To clean up old results:

```bash
# Remove old history
find data/test-results/history -name "*.json" -mtime +30 -delete

# Remove old logs
find data/test-results/logs -name "*.log" -mtime +30 -delete

# Remove old screenshots
find data/test-results/screenshots -name "*.png" -mtime +7 -delete
```
