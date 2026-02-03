#!/usr/bin/env python3
"""
Analytics tracking for Twitter content performance.
Generate reports and track metrics.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path.home() / ".openclaw" / "twitter-scheduler"
ANALYTICS_FILE = DATA_DIR / "analytics.json"
SCHEDULED_FILE = DATA_DIR / "scheduled.json"


def load_analytics():
    """Load analytics data."""
    if ANALYTICS_FILE.exists():
        with open(ANALYTICS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_analytics(data):
    """Save analytics data."""
    with open(ANALYTICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_scheduled():
    """Load scheduled tweets."""
    if SCHEDULED_FILE.exists():
        with open(SCHEDULED_FILE, 'r') as f:
            return json.load(f)
    return []


def track_performance(tweet_id, metrics=None):
    """Track performance for a tweet (manual entry)."""
    analytics = load_analytics()
    
    if metrics is None:
        metrics = {}
    
    entry = {
        "tweet_id": tweet_id,
        "recorded_at": datetime.now().isoformat(),
        "metrics": metrics
    }
    
    analytics[tweet_id] = entry
    save_analytics(analytics)
    
    print(f"✅ Analytics recorded for {tweet_id}")


def view_scheduled_analytics():
    """View analytics for scheduled content."""
    tweets = load_scheduled()
    analytics = load_analytics()
    
    if not tweets:
        print("📭 No scheduled content to analyze.")
        return
    
    print("📊 Scheduled Content Analytics\n")
    print(f"{'ID':<20} {'Scheduled':<18} {'Status':<12} {'Impressions':<12}")
    print("-" * 70)
    
    for tweet in tweets:
        tweet_id = tweet['id']
        scheduled = tweet['scheduled_time'][:16]
        status = tweet['status']
        
        # Get metrics if available
        impressions = "-"
        if tweet_id in analytics:
            impressions = analytics[tweet_id]['metrics'].get('impressions', '-')
        
        print(f"{tweet_id:<20} {scheduled:<18} {status:<12} {impressions:<12}")


def generate_weekly_report():
    """Generate a weekly performance report."""
    analytics = load_analytics()
    tweets = load_scheduled()
    
    print("📈 Weekly Twitter Performance Report\n")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # Calculate basic stats
    total_scheduled = len(tweets)
    total_tracked = len(analytics)
    
    print(f"\n📋 Content Summary:")
    print(f"   Total scheduled: {total_scheduled}")
    print(f"   Posts tracked: {total_tracked}")
    
    if not analytics:
        print("\n⚠️  No performance data available yet.")
        print("   Use --track to record metrics for your tweets.")
        return
    
    # Aggregate metrics
    all_impressions = []
    all_engagements = []
    
    for entry in analytics.values():
        metrics = entry.get('metrics', {})
        if 'impressions' in metrics:
            all_impressions.append(metrics['impressions'])
        if 'engagements' in metrics:
            all_engagements.append(metrics['engagements'])
    
    if all_impressions:
        print(f"\n📊 Performance Metrics:")
        print(f"   Total Impressions: {sum(all_impressions):,}")
        print(f"   Avg Impressions: {sum(all_impressions)/len(all_impressions):.0f}")
        print(f"   Total Engagements: {sum(all_engagements) if all_engagements else 0:,}")


def compare_hashtags(hashtag_list):
    """Compare performance of different hashtags."""
    hashtags = [h.strip().lower() for h in hashtag_list.split(',')]
    tweets = load_scheduled()
    analytics = load_analytics()
    
    print("🏷️  Hashtag Performance Comparison\n")
    
    # Find tweets containing each hashtag
    hashtag_stats = defaultdict(lambda: {'count': 0, 'total_impressions': 0, 'tweets': []})
    
    for tweet in tweets:
        tweet_lower = tweet['content'].lower()
        tweet_id = tweet['id']
        
        for hashtag in hashtags:
            tag_clean = hashtag.replace('#', '')
            if f"#{tag_clean}" in tweet_lower or tag_clean in tweet_lower:
                hashtag_stats[hashtag]['count'] += 1
                hashtag_stats[hashtag]['tweets'].append(tweet_id)
                
                if tweet_id in analytics:
                    impressions = analytics[tweet_id]['metrics'].get('impressions', 0)
                    hashtag_stats[hashtag]['total_impressions'] += impressions
    
    # Display results
    for hashtag in hashtags:
        stats = hashtag_stats[hashtag]
        avg_impressions = stats['total_impressions'] / stats['count'] if stats['count'] > 0 else 0
        
        print(f"#{hashtag.replace('#', '')}:")
        print(f"   Used in {stats['count']} tweets")
        print(f"   Total impressions: {stats['total_impressions']:,}")
        print(f"   Avg impressions: {avg_impressions:.0f}")
        print()


def show_best_performing(top_n=5):
    """Show best performing tweets."""
    analytics = load_analytics()
    
    if not analytics:
        print("📭 No performance data available.")
        return
    
    # Sort by impressions
    sorted_tweets = sorted(
        analytics.items(),
        key=lambda x: x[1]['metrics'].get('impressions', 0),
        reverse=True
    )[:top_n]
    
    print(f"🏆 Top {top_n} Performing Tweets\n")
    
    for i, (tweet_id, data) in enumerate(sorted_tweets, 1):
        metrics = data['metrics']
        impressions = metrics.get('impressions', 0)
        engagements = metrics.get('engagements', 0)
        
        print(f"{i}. {tweet_id}")
        print(f"   Impressions: {impressions:,}")
        print(f"   Engagements: {engagements:,}")
        print()


def export_report(format_type="json", output_file=None):
    """Export analytics report."""
    analytics = load_analytics()
    tweets = load_scheduled()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_scheduled": len(tweets),
        "total_tracked": len(analytics),
        "performance_data": analytics
    }
    
    if not output_file:
        output_file = DATA_DIR / f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analytics tracking for FedBuyOut Twitter"
    )
    parser.add_argument("--scheduled", "-s", action="store_true", help="View scheduled content analytics")
    parser.add_argument("--track", help="Track metrics for a tweet ID (JSON format)")
    parser.add_argument("--weekly", "-w", action="store_true", help="Generate weekly report")
    parser.add_argument("--hashtags", help="Compare hashtag performance (comma-separated)")
    parser.add_argument("--best", "-b", action="store_true", help="Show best performing tweets")
    parser.add_argument("--top", type=int, default=5, help="Number of top tweets to show")
    parser.add_argument("--export", action="store_true", help="Export report")
    parser.add_argument("--format", choices=["json"], default="json", help="Export format")
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    if args.track:
        try:
            metrics = json.loads(args.track)
        except json.JSONDecodeError:
            print("❌ Error: Metrics must be valid JSON")
            return
        track_performance(metrics.get('tweet_id', 'unknown'), metrics)
    elif args.scheduled:
        view_scheduled_analytics()
    elif args.weekly:
        generate_weekly_report()
    elif args.hashtags:
        compare_hashtags(args.hashtags)
    elif args.best:
        show_best_performing(args.top)
    elif args.export:
        export_report(args.format, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
