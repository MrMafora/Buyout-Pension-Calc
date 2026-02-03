#!/usr/bin/env python3
"""
View and manage the content calendar.
Export to various formats.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import csv

DATA_DIR = Path.home() / ".openclaw" / "twitter-scheduler"
SCHEDULED_FILE = DATA_DIR / "scheduled.json"


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_scheduled():
    """Load scheduled tweets."""
    if SCHEDULED_FILE.exists():
        with open(SCHEDULED_FILE, 'r') as f:
            return json.load(f)
    return []


def filter_by_date(tweets, date_filter):
    """Filter tweets by date criteria."""
    today = datetime.now().date()
    
    if date_filter == "today":
        target_date = today
        return [t for t in tweets if datetime.strptime(t['scheduled_time'], "%Y-%m-%d %H:%M").date() == target_date]
    
    elif date_filter == "week":
        week_start = today
        week_end = today + timedelta(days=7)
        return [t for t in tweets if week_start <= datetime.strptime(t['scheduled_time'], "%Y-%m-%d %H:%M").date() <= week_end]
    
    elif date_filter == "month":
        month_start = today.replace(day=1)
        next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
        return [t for t in tweets if month_start <= datetime.strptime(t['scheduled_time'], "%Y-%m-%d %H:%M").date() < next_month]
    
    return tweets


def view_calendar(filter_type=None, campaign=None):
    """View the content calendar."""
    tweets = load_scheduled()
    
    if not tweets:
        print("📭 No scheduled content found.")
        return
    
    # Apply filters
    if filter_type:
        tweets = filter_by_date(tweets, filter_type)
    
    if campaign:
        tweets = [t for t in tweets if t.get('metadata', {}).get('campaign') == campaign]
    
    if not tweets:
        print(f"📭 No content found for the specified filter.")
        return
    
    # Sort by scheduled time
    tweets.sort(key=lambda x: x['scheduled_time'])
    
    # Group by date
    by_date = {}
    for tweet in tweets:
        date = tweet['scheduled_time'][:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(tweet)
    
    print(f"📅 Content Calendar ({len(tweets)} items)\n")
    
    for date in sorted(by_date.keys()):
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        
        print(f"📆 {day_name}, {date}")
        print("-" * 50)
        
        for tweet in sorted(by_date[date], key=lambda x: x['scheduled_time']):
            time = tweet['scheduled_time'][11:16]
            content_preview = tweet['content'][:40] + "..." if len(tweet['content']) > 40 else tweet['content']
            thread_marker = "🧵" if tweet.get('metadata', {}).get('is_thread') else "🐦"
            
            print(f"   {time} {thread_marker} {content_preview}")
        
        print()


def export_calendar(format_type="json", output_file=None):
    """Export calendar to file."""
    tweets = load_scheduled()
    
    if not tweets:
        print("📭 No content to export.")
        return
    
    if format_type == "json":
        if not output_file:
            output_file = DATA_DIR / "calendar_export.json"
        with open(output_file, 'w') as f:
            json.dump(tweets, f, indent=2)
    
    elif format_type == "csv":
        if not output_file:
            output_file = DATA_DIR / "calendar_export.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Time', 'Content', 'Status', 'Thread', 'Char Count'])
            
            for tweet in tweets:
                writer.writerow([
                    tweet['scheduled_time'][:10],
                    tweet['scheduled_time'][11:16],
                    tweet['content'],
                    tweet['status'],
                    'Yes' if tweet.get('metadata', {}).get('is_thread') else 'No',
                    len(tweet['content'])
                ])
    
    print(f"✅ Exported {len(tweets)} items to {output_file}")


def create_weekly_template():
    """Create a weekly content calendar template."""
    ensure_data_dir()
    print("📋 Weekly Content Calendar Template\n")
    
    template = """
WEEKLY CONTENT PLAN
===================

Content Mix Target:
- Educational (40%): 3 posts
- Success Stories (20%): 1-2 posts  
- Industry News (20%): 1-2 posts
- Engagement (20%): 1-2 posts

MONDAY (Start Strong)
---------------------
☐ 9:00 AM - Educational thread or tip
☐ 2:00 PM - Engagement question

TUESDAY (Educational)
---------------------
☐ 9:30 AM - How-to guide or tutorial
☐ 3:00 PM - Industry insight or news

WEDNESDAY (Mid-week Energy)
---------------------------
☐ 10:00 AM - Success story or testimonial
☐ 2:30 PM - Quick tip or resource share

THURSDAY (Value Day)
--------------------
☐ 9:00 AM - Deep educational content
☐ 1:00 PM - Community engagement

FRIDAY (Weekend Sendoff)
------------------------
☐ 10:00 AM - Light content, recap, or question

WEEKEND (Optional)
------------------
☐ Schedule 1 evergreen post for Saturday/Sunday
    """
    
    print(template)
    
    # Save template to file
    template_file = DATA_DIR / "weekly_template.txt"
    with open(template_file, 'w') as f:
        f.write(template)
    
    print(f"💾 Template saved to: {template_file}")


def show_stats():
    """Show calendar statistics."""
    tweets = load_scheduled()
    
    if not tweets:
        print("📭 No scheduled content.")
        return
    
    total = len(tweets)
    threads = sum(1 for t in tweets if t.get('metadata', {}).get('is_thread'))
    single_tweets = total - threads
    
    # Calculate by week
    by_week = {}
    for tweet in tweets:
        date = datetime.strptime(tweet['scheduled_time'], "%Y-%m-%d %H:%M")
        week_key = date.strftime("%Y-W%U")
        by_week[week_key] = by_week.get(week_key, 0) + 1
    
    print("📊 Content Calendar Statistics\n")
    print(f"Total scheduled items: {total}")
    print(f"Single tweets: {single_tweets}")
    print(f"Thread tweets: {threads}")
    print(f"\nScheduled by week:")
    for week, count in sorted(by_week.items()):
        print(f"   {week}: {count} items")


def main():
    parser = argparse.ArgumentParser(
        description="View and manage the FedBuyOut content calendar"
    )
    parser.add_argument("--today", action="store_true", help="View today's schedule")
    parser.add_argument("--week", action="store_true", help="View this week's schedule")
    parser.add_argument("--month", action="store_true", help="View this month's schedule")
    parser.add_argument("--campaign", help="Filter by campaign name")
    parser.add_argument("--export", action="store_true", help="Export calendar")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--template", action="store_true", help="Generate weekly template")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    if args.template:
        create_weekly_template()
    elif args.stats:
        show_stats()
    elif args.export:
        export_calendar(args.format, args.output)
    elif args.today:
        view_calendar("today")
    elif args.week:
        view_calendar("week")
    elif args.month:
        view_calendar("month")
    elif args.campaign:
        view_calendar(campaign=args.campaign)
    else:
        view_calendar()


if __name__ == "__main__":
    main()
