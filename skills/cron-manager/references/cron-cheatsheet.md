# Cron Cheatsheet

Quick reference for cron syntax and common patterns.

## Cron Expression Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Day of week (0-7, 0=Sunday)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

## Special Keywords

| Keyword | Equivalent | Description |
|---------|------------|-------------|
| `@reboot` | - | Run once at system startup |
| `@yearly` | `0 0 1 1 *` | Once a year (Jan 1) |
| `@monthly` | `0 0 1 * *` | Once a month (1st) |
| `@weekly` | `0 0 * * 0` | Once a week (Sunday) |
| `@daily` | `0 0 * * *` | Once a day (midnight) |
| `@midnight` | `0 0 * * *` | Same as @daily |
| `@hourly` | `0 * * * *` | Once an hour |

## Common Patterns

### Every N minutes/hours

| Pattern | Description |
|---------|-------------|
| `*/5 * * * *` | Every 5 minutes |
| `*/15 * * * *` | Every 15 minutes |
| `*/30 * * * *` | Every 30 minutes |
| `0 */2 * * *` | Every 2 hours |
| `0 */6 * * *` | Every 6 hours |
| `0 */12 * * *` | Every 12 hours |

### Daily schedules

| Pattern | Description |
|---------|-------------|
| `0 0 * * *` | Daily at midnight |
| `0 6 * * *` | Daily at 6:00 AM |
| `0 9 * * *` | Daily at 9:00 AM |
| `0 12 * * *` | Daily at noon |
| `0 17 * * *` | Daily at 5:00 PM |

### Weekly schedules

| Pattern | Description |
|---------|-------------|
| `0 0 * * 0` | Weekly on Sunday |
| `0 9 * * 1` | Weekly on Monday at 9 AM |
| `0 0 * * 5` | Weekly on Friday |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 10 * * 0,6` | Weekends at 10 AM |

### Monthly schedules

| Pattern | Description |
|---------|-------------|
| `0 0 1 * *` | Monthly on 1st |
| `0 0 15 * *` | Monthly on 15th |
| `0 0 1 1 *` | Yearly on Jan 1 |
| `0 0 1 7 *` | Yearly on July 1 |

### Business hours

| Pattern | Description |
|---------|-------------|
| `0 9-17 * * 1-5` | Every hour during business hours |
| `0 9,13 * * 1-5` | 9 AM and 1 PM on weekdays |
| `*/30 9-17 * * 1-5` | Every 30 min during business hours |

## Operators

### Asterisk (*)
Matches any value.
```
* * * * *     # Every minute
0 * * * *     # Every hour
```

### Comma (,)
List of values.
```
0 9,12,17 * * *   # At 9 AM, 12 PM, and 5 PM
0 * * * 1,3,5     # Every hour on Mon, Wed, Fri
```

### Dash (-)
Range of values.
```
0 9-17 * * 1-5    # Every hour 9-5, Mon-Fri
*/15 * * * *      # Every 15 minutes
```

### Slash (/)
Step values.
```
*/5 * * * *       # Every 5 minutes
0 */2 * * *       # Every 2 hours
```

## Natural Language Equivalents

The cron-manager supports natural language:

| Natural Language | Cron Equivalent |
|------------------|-----------------|
| `every minute` | `* * * * *` |
| `every 5 minutes` | `*/5 * * * *` |
| `every hour` | `0 * * * *` |
| `daily` | `0 0 * * *` |
| `daily at 9am` | `0 9 * * *` |
| `weekly` | `0 0 * * 0` |
| `monthly` | `0 0 1 * *` |
| `every monday` | `0 0 * * 1` |
| `hourly` | `0 * * * *` |

## Tips

1. **Test your cron expression** using `cron_helper.py --validate`
2. **Stagger jobs** - Don't schedule everything at :00
3. **Use absolute paths** in commands (cron has limited PATH)
4. **Set timezone** if needed - cron uses system timezone
5. **Log output** - Redirect stdout/stderr for debugging:
   ```
   0 2 * * * /path/to/script.sh >> /var/log/job.log 2>&1
   ```

## Resources

- crontab.guru - Visual cron editor
- https://crontab.guru/
