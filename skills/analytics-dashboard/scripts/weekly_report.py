#!/usr/bin/env python3
"""
Weekly Performance Report Generator
Generates week-over-week comparison reports from Google Analytics 4.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension,
)
from google.oauth2 import service_account

DEFAULT_PROPERTY_ID = "G-07WYT2HRDW"
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
    return f"{num:,}"


def format_duration(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def calculate_change(current: float, previous: float) -> tuple:
    """Calculate change and percentage."""
    if previous == 0:
        return current, 100.0 if current > 0 else 0.0
    change = current - previous
    pct_change = ((current - previous) / previous) * 100
    return change, pct_change


def run_weekly_report(property_id: str, weeks: int = 1) -> Dict[str, Any]:
    """Generate weekly performance report with week-over-week comparison."""
    
    # Calculate date ranges
    today = datetime.now()
    
    # This week (ending yesterday)
    this_week_end = today - timedelta(days=1)
    this_week_start = this_week_end - timedelta(days=6)
    
    # Previous week
    prev_week_end = this_week_start - timedelta(days=1)
    prev_week_start = prev_week_end - timedelta(days=6)
    
    try:
        credentials = get_credentials()
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        # Current week metrics
        current_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(
                start_date=this_week_start.strftime("%Y-%m-%d"),
                end_date=this_week_end.strftime("%Y-%m-%d")
            )],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="engagementRate"),
                Metric(name="conversions"),
                Metric(name="sessionConversionRate"),
            ],
        )
        
        # Previous week metrics
        previous_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(
                start_date=prev_week_start.strftime("%Y-%m-%d"),
                end_date=prev_week_end.strftime("%Y-%m-%d")
            )],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="engagementRate"),
                Metric(name="conversions"),
                Metric(name="sessionConversionRate"),
            ],
        )
        
        # Traffic sources for current week
        sources_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(
                start_date=this_week_start.strftime("%Y-%m-%d"),
                end_date=this_week_end.strftime("%Y-%m-%d")
            )],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[Metric(name="sessions"), Metric(name="screenPageViews"), Metric(name="conversions")],
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        # Top pages
        pages_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(
                start_date=this_week_start.strftime("%Y-%m-%d"),
                end_date=this_week_end.strftime("%Y-%m-%d")
            )],
            dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews"), Metric(name="engagementRate")],
            limit=10,
            order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
        )
        
        current_response = client.run_report(current_request)
        previous_response = client.run_report(previous_request)
        sources_response = client.run_report(sources_request)
        pages_response = client.run_report(pages_request)
        
        # Parse current week metrics
        current_metrics = {}
        if current_response.rows:
            row = current_response.rows[0]
            current_metrics = {
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "new_users": int(row.metric_values[2].value),
                "pageviews": int(row.metric_values[3].value),
                "bounce_rate": float(row.metric_values[4].value) * 100,
                "avg_session_duration": float(row.metric_values[5].value),
                "engagement_rate": float(row.metric_values[6].value) * 100,
                "conversions": float(row.metric_values[7].value),
                "conversion_rate": float(row.metric_values[8].value) * 100,
            }
        
        # Parse previous week metrics
        previous_metrics = {}
        if previous_response.rows:
            row = previous_response.rows[0]
            previous_metrics = {
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "new_users": int(row.metric_values[2].value),
                "pageviews": int(row.metric_values[3].value),
                "bounce_rate": float(row.metric_values[4].value) * 100,
                "avg_session_duration": float(row.metric_values[5].value),
                "engagement_rate": float(row.metric_values[6].value) * 100,
                "conversions": float(row.metric_values[7].value),
                "conversion_rate": float(row.metric_values[8].value) * 100,
            }
        
        # Calculate changes
        changes = {}
        for key in current_metrics:
            if key in previous_metrics:
                change, pct = calculate_change(current_metrics[key], previous_metrics[key])
                changes[key] = {"value": change, "percent": pct}
        
        # Parse traffic sources
        sources = []
        for row in sources_response.rows:
            sources.append({
                "channel": row.dimension_values[0].value,
                "sessions": int(row.metric_values[0].value),
                "pageviews": int(row.metric_values[1].value),
                "conversions": float(row.metric_values[2].value),
            })
        
        # Parse top pages
        top_pages = []
        for row in pages_response.rows:
            top_pages.append({
                "title": row.dimension_values[0].value,
                "path": row.dimension_values[1].value,
                "pageviews": int(row.metric_values[0].value),
                "engagement_rate": float(row.metric_values[1].value) * 100,
            })
        
        report = {
            "report_type": "weekly",
            "property_id": property_id,
            "current_week": {
                "start": this_week_start.strftime("%Y-%m-%d"),
                "end": this_week_end.strftime("%Y-%m-%d"),
            },
            "previous_week": {
                "start": prev_week_start.strftime("%Y-%m-%d"),
                "end": prev_week_end.strftime("%Y-%m-%d"),
            },
            "current_metrics": current_metrics,
            "previous_metrics": previous_metrics,
            "changes": changes,
            "traffic_sources": sources,
            "top_pages": top_pages,
            "generated_at": datetime.now().isoformat(),
        }
        
        return report
        
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)


def output_console(report: Dict[str, Any]):
    """Output report in console format."""
    print("=" * 70)
    print("WEEKLY PERFORMANCE REPORT - FedBuyOut")
    print("=" * 70)
    print(f"Current Week: {report['current_week']['start']} to {report['current_week']['end']}")
    print(f"Previous Week: {report['previous_week']['start']} to {report['previous_week']['end']}")
    print("=" * 70)
    
    print("\n📊 WEEK-OVER-WEEK COMPARISON")
    print("-" * 70)
    print(f"{'Metric':<25} {'Current':>12} {'Previous':>12} {'Change':>12} {'% Change':>10}")
    print("-" * 70)
    
    current = report.get("current_metrics", {})
    previous = report.get("previous_metrics", {})
    changes = report.get("changes", {})
    
    metrics_display = [
        ("Sessions", "sessions", "number"),
        ("Users", "users", "number"),
        ("New Users", "new_users", "number"),
        ("Pageviews", "pageviews", "number"),
        ("Bounce Rate", "bounce_rate", "percent"),
        ("Avg Session", "avg_session_duration", "duration"),
        ("Engagement Rate", "engagement_rate", "percent"),
        ("Conversions", "conversions", "number"),
        ("Conversion Rate", "conversion_rate", "percent"),
    ]
    
    for label, key, fmt in metrics_display:
        cur_val = current.get(key, 0)
        prev_val = previous.get(key, 0)
        change = changes.get(key, {}).get("value", 0)
        pct = changes.get(key, {}).get("percent", 0)
        
        if fmt == "number":
            cur_str = format_number(int(cur_val))
            prev_str = format_number(int(prev_val))
            change_str = format_number(int(change))
        elif fmt == "percent":
            cur_str = format_percent(cur_val)
            prev_str = format_percent(prev_val)
            change_str = f"{'+' if change >= 0 else ''}{format_percent(change)}"
        elif fmt == "duration":
            cur_str = format_duration(cur_val)
            prev_str = format_duration(prev_val)
            change_str = format_duration(change)
        
        pct_str = f"{'+' if pct >= 0 else ''}{format_percent(pct)}"
        indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        
        print(f"{label:<25} {cur_str:>12} {prev_str:>12} {change_str:>12} {pct_str:>9} {indicator}")
    
    print("\n🌐 TRAFFIC SOURCES (Current Week)")
    print("-" * 70)
    print(f"{'Channel':<25} {'Sessions':>12} {'Pageviews':>12} {'Conversions':>12}")
    print("-" * 70)
    for source in report.get("traffic_sources", []):
        print(f"{source['channel']:<25} {format_number(source['sessions']):>12} "
              f"{format_number(source['pageviews']):>12} {format_number(int(source['conversions'])):>12}")
    
    print("\n📄 TOP PAGES (Current Week)")
    print("-" * 70)
    print(f"{'Page':<40} {'Views':>12} {'Engagement':>12}")
    print("-" * 70)
    for page in report.get("top_pages", [])[:10]:
        print(f"{page['title'][:38]:<40} {format_number(page['pageviews']):>12} "
              f"{format_percent(page['engagement_rate']):>12}")
    
    print("\n" + "=" * 70)
    print(f"Generated: {report['generated_at']}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Generate weekly performance report from Google Analytics 4"
    )
    parser.add_argument(
        "--property",
        default=DEFAULT_PROPERTY_ID,
        help=f"GA4 Property ID (default: {DEFAULT_PROPERTY_ID})"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=1,
        help="Number of weeks to report (default: 1)"
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
    
    report = run_weekly_report(args.property, args.weeks)
    
    if args.format == "console":
        output_console(report)
    elif args.format == "json":
        print(json.dumps(report, indent=2))
    
    if args.output and args.format == "json":
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
