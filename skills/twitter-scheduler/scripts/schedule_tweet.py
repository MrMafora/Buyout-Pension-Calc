#!/usr/bin/env python3
"""
Schedule tweets for optimal posting times.
Stores tweets in a JSON file for later processing/integration.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# FedBuyOut optimal posting times (US Eastern)
OPTIMAL_TIMES = [
    ("09:00", "11:00"),  # Morning peak
    ("13:00", "15:00"),  # Afternoon peak
]

DATA_DIR = Path.home() / ".openclaw" / "twitter-scheduler"
SCHEDULED_FILE = DATA_DIR / "scheduled.json"


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_scheduled():
    """Load existing scheduled tweets."""
    if SCHEDULED_FILE.exists():
        with open(SCHEDULED_FILE, 'r') as f:
            return json.load(f)
    return []


def save_scheduled(tweets):
    """Save scheduled tweets to JSON."""
    with open(SCHEDULED_FILE, 'w') as f:
        json.dump(tweets, f, indent=2)


def validate_tweet(content):
    """Validate tweet content."""
    if len(content) > 280:
        return False, f"Tweet exceeds 280 characters ({len(content)} chars)"
    if not content.strip():
        return False, "Tweet content cannot be empty"
    return True, None


def suggest_optimal_time():
    """Suggest the next optimal posting time."""
    now = datetime.now()
    
    # Start from tomorrow at first optimal time
    suggested = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    # If it's already past morning time, suggest afternoon
    if now.hour >= 11:
        suggested = suggested.replace(hour=14, minute=0)
    
    return suggested.strftime("%Y-%m-%d %H:%M")


def schedule_tweet(content, schedule_time=None, auto_time=False, timezone="America/New_York"):
    """Schedule a new tweet."""
    ensure_data_dir()
    
    # Validate content
    valid, error = validate_tweet(content)
    if not valid:
        print(f"❌ Error: {error}")
        sys.exit(1)
    
    # Determine schedule time
    if auto_time:
        schedule_time = suggest_optimal_time()
        print(f"📅 Auto-suggested time: {schedule_time}")
    elif not schedule_time:
        print("❌ Error: Must specify --time or --auto-time")
        sys.exit(1)
    
    # Parse and validate time
    try:
        scheduled_dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
    except ValueError:
        print("❌ Error: Time format must be YYYY-MM-DD HH:MM")
        sys.exit(1)
    
    if scheduled_dt < datetime.now():
        print("⚠️  Warning: Scheduled time is in the past. Tweet will be flagged.")
    
    # Load existing tweets
    tweets = load_scheduled()
    
    # Create tweet entry
    tweet_id = f"tweet_{len(tweets) + 1:04d}"
    tweet_entry = {
        "id": tweet_id,
        "content": content,
        "scheduled_time": schedule_time,
        "timezone": timezone,
        "status": "scheduled",
        "created_at": datetime.now().isoformat(),
        "platform": "twitter",
        "metadata": {
            "char_count": len(content),
            "has_hashtags": "#" in content,
            "has_mentions": "@" in content,
            "has_url": "http" in content
        }
    }
    
    # Add to schedule
    tweets.append(tweet_entry)
    save_scheduled(tweets)
    
    print(f"✅ Tweet scheduled successfully!")
    print(f"   ID: {tweet_id}")
    print(f"   Time: {schedule_time} ({timezone})")
    print(f"   Content: {content[:60]}{'...' if len(content) > 60 else ''}")
    
    return tweet_id


def list_scheduled():
    """List all scheduled tweets."""
    tweets = load_scheduled()
    
    if not tweets:
        print("📭 No scheduled tweets found.")
        return
    
    print(f"📅 Scheduled Tweets ({len(tweets)} total):\n")
    print(f"{'ID':<15} {'Time':<20} {'Status':<12} {'Content':<40}")
    print("-" * 87)
    
    for tweet in tweets:
        content_preview = tweet['content'][:37] + "..." if len(tweet['content']) > 40 else tweet['content']
        print(f"{tweet['id']:<15} {tweet['scheduled_time']:<20} {tweet['status']:<12} {content_preview:<40}")


def main():
    parser = argparse.ArgumentParser(
        description="Schedule tweets for FedBuyOut's Twitter account"
    )
    parser.add_argument("--content", "-c", help="Tweet content")
    parser.add_argument("--time", "-t", help="Schedule time (YYYY-MM-DD HH:MM)")
    parser.add_argument("--auto-time", "-a", action="store_true", help="Use optimal auto-suggested time")
    parser.add_argument("--timezone", "-z", default="America/New_York", help="Timezone (default: America/New_York)")
    parser.add_argument("--list", "-l", action="store_true", help="List all scheduled tweets")
    parser.add_argument("--file", "-f", help="Read tweet content from file")
    
    args = parser.parse_args()
    
    if args.list:
        list_scheduled()
    elif args.file:
        with open(args.file, 'r') as f:
            content = f.read().strip()
        schedule_tweet(content, args.time, args.auto_time, args.timezone)
    elif args.content:
        schedule_tweet(args.content, args.time, args.auto_time, args.timezone)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
