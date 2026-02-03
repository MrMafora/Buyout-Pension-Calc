#!/usr/bin/env python3
"""
Daily Traffic Summary Report Generator
Fetches and displays daily Google Analytics 4 metrics for FedBuyOut.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Google Analytics Data API
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension,
)
from google.oauth2 import service_account

# Default property ID for FedBuyOut
DEFAULT_PROPERTY_ID = "G-07WYT2HRDW"

# Service account credentials path
CREDENTIALS_PATH = os.path.expanduser("~/.config/fedbuyout-analytics/credentials.json")


def get_credentials():
    """Load service account credentials."""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Credentials not found at {CREDENTIALS_PATH}. "
            "Please set up Google Analytics API credentials."
        )
    return service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )


def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"


def format_duration(seconds: float) -> str:
    """Format seconds into mm:ss."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


def format_percent(value: float) -> str:
    """Format as percentage."""
    return f"{value:.1f}%"


def run_daily_report(property_id: str, days: int = 1, output_format: str = "console") -> Dict[str, Any]:
    """Generate daily traffic report."""
    
    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")
    
    try:
        credentials = get_credentials()
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        # Core metrics request
        metrics_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="engagementRate"),
            ],
        )
        
        metrics_response = client.run_report(metrics_request)
        
        # Top pages request
        pages_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews"), Metric(name="sessions")],
            limit=10,
            order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
        )
        
        pages_response = client.run_report(pages_request)
        
        # Traffic sources request
        sources_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[Metric(name="sessions"), Metric(name="totalUsers")],
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        sources_response = client.run_report(sources_request)
        
        # Parse metrics
        metrics = {}
        if metrics_response.rows:
            row = metrics_response.rows[0]
            metrics = {
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "new_users": int(row.metric_values[2].value),
                "pageviews": int(row.metric_values[3].value),
                "bounce_rate": float(row.metric_values[4].value) * 100,
                "avg_session_duration": float(row.metric_values[5].value),
                "engagement_rate": float(row.metric_values[6].value) * 100,
            }
        
        # Parse top pages
        top_pages = []
        for row in pages_response.rows:
            top_pages.append({
                "title": row.dimension_values[0].value,
                "path": row.dimension_values[1].value,
                "pageviews": int(row.metric_values[0].value),
                "sessions": int(row.metric_values[1].value),
            })
        
        # Parse traffic sources
        sources = []
        for row in sources_response.rows:
            sources.append({
                "channel": row.dimension_values[0].value,
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
            })
        
        report = {
            "report_type": "daily",
            "property_id": property_id,
            "date_range": {"start": start_date, "end": end_date},
            "metrics": metrics,
            "top_pages": top_pages,
            "traffic_sources": sources,
            "generated_at": datetime.now().isoformat(),
        }
        
        return report
        
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)


def output_console(report: Dict[str, Any]):
    """Output report in console format."""
    print("=" * 60)
    print("DAILY TRAFFIC SUMMARY - FedBuyOut")
    print("=" * 60)
    print(f"Period: {report['date_range']['start']} to {report['date_range']['end']}")
    print(f"Property: {report['property_id']}")
    print("=" * 60)
    
    metrics = report.get("metrics", {})
    print("\n📊 KEY METRICS")
    print("-" * 40)
    print(f"  Sessions:           {format_number(metrics.get('sessions', 0))}")
    print(f"  Total Users:        {format_number(metrics.get('users', 0))}")
    print(f"  New Users:          {format_number(metrics.get('new_users', 0))}")
    print(f"  Pageviews:          {format_number(metrics.get('pageviews', 0))}")
    print(f"  Bounce Rate:        {format_percent(metrics.get('bounce_rate', 0))}")
    print(f"  Avg Session:        {format_duration(metrics.get('avg_session_duration', 0))}")
    print(f"  Engagement Rate:    {format_percent(metrics.get('engagement_rate', 0))}")
    
    print("\n📄 TOP PAGES")
    print("-" * 40)
    for i, page in enumerate(report.get("top_pages", [])[:5], 1):
        print(f"  {i}. {page['title'][:40]}")
        print(f"     Path: {page['path'][:50]}")
        print(f"     Views: {format_number(page['pageviews'])}, Sessions: {format_number(page['sessions'])}")
    
    print("\n🌐 TRAFFIC SOURCES")
    print("-" * 40)
    for source in report.get("traffic_sources", []):
        pct = (source['sessions'] / metrics.get('sessions', 1)) * 100 if metrics.get('sessions') else 0
        print(f"  {source['channel'][:20]:<20} {format_number(source['sessions']):>10} ({format_percent(pct)})")
    
    print("\n" + "=" * 60)
    print(f"Generated: {report['generated_at']}")
    print("=" * 60)


def output_markdown(report: Dict[str, Any]):
    """Output report in Markdown format."""
    print(f"# Daily Traffic Summary - FedBuyOut")
    print(f"\n**Period:** {report['date_range']['start']} to {report['date_range']['end']}")
    print(f"**Property:** {report['property_id']}")
    print(f"**Generated:** {report['generated_at']}")
    
    print("\n## Key Metrics")
    print("\n| Metric | Value |")
    print("|--------|-------|")
    metrics = report.get("metrics", {})
    print(f"| Sessions | {format_number(metrics.get('sessions', 0))} |")
    print(f"| Total Users | {format_number(metrics.get('users', 0))} |")
    print(f"| New Users | {format_number(metrics.get('new_users', 0))} |")
    print(f"| Pageviews | {format_number(metrics.get('pageviews', 0))} |")
    print(f"| Bounce Rate | {format_percent(metrics.get('bounce_rate', 0))} |")
    print(f"| Avg Session Duration | {format_duration(metrics.get('avg_session_duration', 0))} |")
    print(f"| Engagement Rate | {format_percent(metrics.get('engagement_rate', 0))} |")
    
    print("\n## Top Pages")
    print("\n| Page | Path | Views | Sessions |")
    print("|------|------|-------|----------|")
    for page in report.get("top_pages", [])[:10]:
        print(f"| {page['title'][:30]} | {page['path'][:30]} | {format_number(page['pageviews'])} | {format_number(page['sessions'])} |")
    
    print("\n## Traffic Sources")
    print("\n| Source | Sessions | Users |")
    print("|--------|----------|-------|")
    for source in report.get("traffic_sources", []):
        print(f"| {source['channel']} | {format_number(source['sessions'])} | {format_number(source['users'])} |")


def main():
    parser = argparse.ArgumentParser(
        description="Generate daily traffic summary from Google Analytics 4"
    )
    parser.add_argument(
        "--property",
        default=DEFAULT_PROPERTY_ID,
        help=f"GA4 Property ID (default: {DEFAULT_PROPERTY_ID})"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to report (default: 1)"
    )
    parser.add_argument(
        "--format",
        choices=["console", "json", "markdown"],
        default="console",
        help="Output format (default: console)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (optional)"
    )
    
    args = parser.parse_args()
    
    report = run_daily_report(args.property, args.days, args.format)
    
    if args.format == "console":
        output_console(report)
    elif args.format == "markdown":
        output_markdown(report)
    elif args.format == "json":
        print(json.dumps(report, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            if args.format == "json":
                json.dump(report, f, indent=2)
            elif args.format == "markdown":
                # Redirect stdout temporarily
                import io
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                output_markdown(report)
                f.write(sys.stdout.getvalue())
                sys.stdout = old_stdout
            else:
                f.write(json.dumps(report, indent=2))
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
