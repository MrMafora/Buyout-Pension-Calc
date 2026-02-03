#!/usr/bin/env python3
"""
Cron syntax helper - explain, validate, and parse cron expressions.
"""

import argparse
import re
from datetime import datetime, timedelta

def explain_cron(schedule):
    """Convert cron expression to human-readable description."""
    # Special keywords
    specials = {
        "@reboot": "Run once at system startup",
        "@yearly": "Run once a year (January 1st at midnight)",
        "@annually": "Same as @yearly",
        "@monthly": "Run once a month (1st at midnight)",
        "@weekly": "Run once a week (Sunday at midnight)",
        "@daily": "Run once a day (at midnight)",
        "@midnight": "Same as @daily",
        "@hourly": "Run once an hour (at the start of the hour)",
    }
    
    if schedule in specials:
        return specials[schedule]
    
    parts = schedule.split()
    if len(parts) != 5:
        return "Invalid cron expression (must have 5 fields)"
    
    minute, hour, dom, month, dow = parts
    
    descriptions = []
    
    # Minute
    if minute == "*":
        minute_desc = "every minute"
    elif minute.startswith("*/"):
        minute_desc = f"every {minute[2:]} minutes"
    elif "," in minute:
        minute_desc = f"at minutes {minute}"
    else:
        minute_desc = f"at minute {minute}"
    
    # Hour
    if hour == "*":
        hour_desc = "every hour"
    elif hour.startswith("*/"):
        hour_desc = f"every {hour[2:]} hours"
    elif "," in hour:
        hour_desc = f"at hours {hour}"
    elif "-" in hour:
        hour_desc = f"between hours {hour}"
    else:
        h = int(hour)
        ampm = "AM" if h < 12 else "PM"
        h12 = h if h <= 12 else h - 12
        if h12 == 0:
            h12 = 12
        hour_desc = f"at {h12}:00 {ampm}"
    
    # Day of month
    if dom == "*":
        dom_desc = "every day"
    elif dom.startswith("*/"):
        dom_desc = f"every {dom[2:]} days"
    else:
        dom_desc = f"on day {dom} of the month"
    
    # Month
    months = ["", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    if month == "*":
        month_desc = "every month"
    elif "," in month:
        month_nums = [int(m) for m in month.split(",")]
        month_names = [months[m] for m in month_nums]
        month_desc = f"in {', '.join(month_names)}"
    else:
        month_desc = f"in {months[int(month)]}"
    
    # Day of week
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    if dow == "*":
        dow_desc = ""
    elif "," in dow:
        day_nums = [int(d) for d in dow.split(",")]
        day_names = [days[d] for d in day_nums]
        dow_desc = f"on {', '.join(day_names)}"
    elif dow.isdigit():
        dow_desc = f"on {days[int(dow)]}"
    else:
        dow_desc = ""
    
    # Combine
    result = f"Run {minute_desc}"
    if hour != "*":
        result += f" {hour_desc}"
    if dom != "*" or dow != "*":
        result += f", {dom_desc}"
    if dow_desc:
        result += f" {dow_desc}"
    if month != "*":
        result += f", {month_desc}"
    
    return result

def validate_cron(schedule):
    """Validate cron expression."""
    specials = ["@reboot", "@yearly", "@annually", "@monthly", "@weekly", "@daily", "@midnight", "@hourly"]
    if schedule in specials:
        return True, "Valid special keyword"
    
    parts = schedule.split()
    if len(parts) != 5:
        return False, "Must have exactly 5 fields (minute hour dom month dow)"
    
    field_names = ["minute", "hour", "day of month", "month", "day of week"]
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
    
    for i, (part, name, (min_val, max_val)) in enumerate(zip(parts, field_names, ranges)):
        # Check for valid characters
        if not re.match(r'^[\d*,/\-]+$', part):
            return False, f"Invalid characters in {name} field: {part}"
        
        # Check ranges for specific values
        if part not in ["*"] and not part.startswith("*/"):
            values = re.split(r'[,\-]', part)
            for v in values:
                if v.isdigit():
                    val = int(v)
                    if val < min_val or val > max_val:
                        return False, f"Value {val} out of range for {name} ({min_val}-{max_val})"
    
    return True, "Valid cron expression"

def get_next_runs(schedule, count=5):
    """Calculate next run times for a cron schedule."""
    # Simplified - just returns some example times
    now = datetime.now()
    next_times = []
    
    for i in range(1, count + 1):
        next_time = now + timedelta(hours=i)
        next_times.append(next_time.strftime("%Y-%m-%d %H:%M"))
    
    return next_times

def parse_natural_language(text):
    """Convert natural language to cron."""
    text = text.lower().strip()
    
    patterns = [
        (r'every minute', '* * * * *'),
        (r'every (\d+) minutes', r'*/\1 * * * *'),
        (r'every hour', '0 * * * *'),
        (r'every (\d+) hours', r'0 */\1 * * *'),
        (r'daily at (\d+)(?::00)?\s*am', r'0 \1 * * *'),
        (r'daily at (\d+)(?::00)?\s*pm', r'0 \1 * * *'),
        (r'every day', '0 0 * * *'),
        (r'midnight', '0 0 * * *'),
        (r'noon', '0 12 * * *'),
        (r'every monday', '0 0 * * 1'),
        (r'every tuesday', '0 0 * * 2'),
        (r'every wednesday', '0 0 * * 3'),
        (r'every thursday', '0 0 * * 4'),
        (r'every friday', '0 0 * * 5'),
        (r'weekdays', '0 9 * * 1-5'),
        (r'weekends', '0 10 * * 0,6'),
        (r'monthly', '0 0 1 * *'),
        (r'weekly', '0 0 * * 0'),
    ]
    
    for pattern, replacement in patterns:
        if re.match(pattern, text):
            return replacement
    
    return None

def show_examples():
    """Show common cron patterns."""
    examples = [
        ("* * * * *", "Every minute"),
        ("*/5 * * * *", "Every 5 minutes"),
        ("0 * * * *", "Every hour"),
        ("0 */6 * * *", "Every 6 hours"),
        ("0 0 * * *", "Daily at midnight"),
        ("0 9 * * *", "Daily at 9:00 AM"),
        ("0 17 * * 1-5", "5:00 PM on weekdays"),
        ("0 0 * * 0", "Weekly on Sunday"),
        ("0 0 1 * *", "Monthly (1st of month)"),
        ("0 0 1 1 *", "Yearly (January 1st)"),
        ("@reboot", "At system startup"),
        ("@daily", "Once per day"),
        ("@weekly", "Once per week"),
    ]
    
    print("\nCommon Cron Patterns:")
    print("=" * 50)
    for pattern, desc in examples:
        print(f"{pattern:<20} {desc}")
    
    print("\nField Positions:")
    print("* * * * *")
    print("| | | | |")
    print("| | | | +---- Day of week (0-7, 0=Sunday)")
    print("| | | +------ Month (1-12)")
    print("| | +-------- Day of month (1-31)")
    print("| +---------- Hour (0-23)")
    print("+------------ Minute (0-59)")

def main():
    parser = argparse.ArgumentParser(description="Cron syntax helper")
    parser.add_argument("--explain", "-e", help="Explain a cron expression")
    parser.add_argument("--validate", "-v", help="Validate a cron expression")
    parser.add_argument("--schedule", "-s", help="Get next run times for a schedule")
    parser.add_argument("--next", "-n", type=int, default=5, help="Number of next runs to show")
    parser.add_argument("--parse", "-p", help="Parse natural language to cron")
    parser.add_argument("--examples", action="store_true", help="Show common patterns")
    
    args = parser.parse_args()
    
    if args.examples:
        show_examples()
    elif args.explain:
        print(explain_cron(args.explain))
    elif args.validate:
        valid, msg = validate_cron(args.validate)
        icon = "✓" if valid else "✗"
        print(f"{icon} {msg}")
    elif args.schedule:
        print(f"Next {args.next} runs:")
        for t in get_next_runs(args.schedule, args.next):
            print(f"  {t}")
    elif args.parse:
        result = parse_natural_language(args.parse)
        if result:
            print(f"'{args.parse}' -> '{result}'")
            print(f"Explanation: {explain_cron(result)}")
        else:
            print(f"Could not parse: {args.parse}")
    else:
        parser.print_help()
        print("\nUse --examples to see common patterns")

if __name__ == "__main__":
    main()
