#!/usr/bin/env python3
"""
Build and schedule tweet threads.
Validates thread structure and character limits.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path.home() / ".openclaw" / "twitter-scheduler"
THREADS_FILE = DATA_DIR / "threads.json"
SCHEDULED_FILE = DATA_DIR / "scheduled.json"


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_threads():
    """Load existing threads."""
    if THREADS_FILE.exists():
        with open(THREADS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_threads(threads):
    """Save threads to JSON."""
    with open(THREADS_FILE, 'w') as f:
        json.dump(threads, f, indent=2)


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


def parse_thread_file(file_path):
    """Parse thread content from file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split by separator (--- or \n---\n)
    tweets = []
    parts = content.split('---')
    
    for i, part in enumerate(parts):
        tweet_text = part.strip()
        if tweet_text:
            tweets.append(tweet_text)
    
    return tweets


def validate_thread(tweets):
    """Validate thread content."""
    errors = []
    
    if len(tweets) < 2:
        errors.append("Thread must have at least 2 tweets")
    
    for i, tweet in enumerate(tweets):
        if len(tweet) > 280:
            errors.append(f"Tweet {i+1} exceeds 280 characters ({len(tweet)} chars)")
        if not tweet.strip():
            errors.append(f"Tweet {i+1} is empty")
    
    return errors


def format_thread_numbered(tweets):
    """Format tweets with thread numbering (1/n, 2/n)."""
    n = len(tweets)
    formatted = []
    
    for i, tweet in enumerate(tweets):
        # Add thread indicator
        indicator = f"{i+1}/{n}"
        
        # Check if tweet already has numbering
        if not tweet.startswith(f"{i+1}/"):
            formatted.append(f"{indicator}\n\n{tweet}")
        else:
            formatted.append(tweet)
    
    return formatted


def build_thread(file_path, schedule_time=None, interval_minutes=10, dry_run=False):
    """Build and schedule a tweet thread."""
    ensure_data_dir()
    
    # Parse thread file
    try:
        tweets = parse_thread_file(file_path)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)
    
    # Validate thread
    errors = validate_thread(tweets)
    if errors:
        print("❌ Thread validation failed:")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)
    
    # Format with numbering
    tweets = format_thread_numbered(tweets)
    
    print(f"✅ Thread validated: {len(tweets)} tweets")
    
    # Show preview
    print("\n📋 Thread Preview:")
    print("=" * 50)
    for i, tweet in enumerate(tweets):
        print(f"\n📝 Tweet {i+1}:")
        print(f"{tweet}")
        print(f"   ({len(tweet)} characters)")
    print("=" * 50)
    
    if dry_run:
        print("\n🏃 Dry run mode - not scheduling")
        return
    
    # Determine schedule time
    if schedule_time:
        try:
            start_dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
        except ValueError:
            print("❌ Error: Time format must be YYYY-MM-DD HH:MM")
            sys.exit(1)
    else:
        # Default to tomorrow 9 AM
        start_dt = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        schedule_time = start_dt.strftime("%Y-%m-%d %H:%M")
        print(f"\n📅 Auto-suggested start time: {schedule_time}")
    
    # Load existing data
    scheduled = load_scheduled()
    threads = load_threads()
    
    # Generate thread ID
    thread_id = f"thread_{len(threads) + 1:04d}"
    
    thread_entry = {
        "id": thread_id,
        "tweet_count": len(tweets),
        "scheduled_time": schedule_time,
        "interval_minutes": interval_minutes,
        "status": "scheduled",
        "created_at": datetime.now().isoformat(),
        "tweets": []
    }
    
    # Schedule each tweet with interval
    current_time = start_dt
    scheduled_ids = []
    
    for i, tweet in enumerate(tweets):
        tweet_id = f"{thread_id}_tweet_{i+1:02d}"
        time_str = current_time.strftime("%Y-%m-%d %H:%M")
        
        tweet_entry = {
            "id": tweet_id,
            "content": tweet,
            "scheduled_time": time_str,
            "timezone": "America/New_York",
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "platform": "twitter",
            "thread_id": thread_id,
            "thread_position": i + 1,
            "metadata": {
                "char_count": len(tweet),
                "is_thread": True
            }
        }
        
        scheduled.append(tweet_entry)
        scheduled_ids.append(tweet_id)
        thread_entry["tweets"].append({
            "position": i + 1,
            "id": tweet_id,
            "scheduled_time": time_str,
            "content": tweet[:60] + "..." if len(tweet) > 60 else tweet
        })
        
        current_time += timedelta(minutes=interval_minutes)
    
    threads.append(thread_entry)
    save_threads(threads)
    save_scheduled(scheduled)
    
    print(f"\n✅ Thread scheduled successfully!")
    print(f"   Thread ID: {thread_id}")
    print(f"   Start Time: {schedule_time}")
    print(f"   Interval: {interval_minutes} minutes")
    print(f"   Tweets: {len(tweets)}")
    print(f"   Scheduled IDs: {', '.join(scheduled_ids)}")


def list_threads():
    """List all scheduled threads."""
    threads = load_threads()
    
    if not threads:
        print("📭 No scheduled threads found.")
        return
    
    print(f"📚 Scheduled Threads ({len(threads)} total):\n")
    
    for thread in threads:
        print(f"🧵 Thread {thread['id']}")
        print(f"   Status: {thread['status']}")
        print(f"   Start Time: {thread['scheduled_time']}")
        print(f"   Tweet Count: {thread['tweet_count']}")
        print(f"   Interval: {thread['interval_minutes']} min")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Build and schedule tweet threads for FedBuyOut"
    )
    parser.add_argument("--file", "-f", help="Path to thread content file")
    parser.add_argument("--time", "-t", help="Schedule start time (YYYY-MM-DD HH:MM)")
    parser.add_argument("--interval", "-i", type=int, default=10, help="Minutes between tweets (default: 10)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview without scheduling")
    parser.add_argument("--list", "-l", action="store_true", help="List all scheduled threads")
    
    args = parser.parse_args()
    
    if args.list:
        list_threads()
    elif args.file:
        build_thread(args.file, args.time, args.interval, args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
