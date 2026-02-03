#!/usr/bin/env python3
"""
Monthly Deep-Dive Analysis Report Generator
Comprehensive monthly analytics with trends and insights.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from calendar import monthrange
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


def get_month_dates(year: int, month: int) -> tuple:
    """Get start and end dates for a given month."""
    start_date = f"{year}-{month:02d}-01"
    _, last_day = monthrange(year, month)
    end_date = f"{year}-{month:02d}-{last_day}"
    return start_date, end_date


def get_previous_month_dates(year: int, month: int) -> tuple:
    """Get start and end dates for the previous month."""
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1
    return get_month_dates(prev_year, prev_month)


def run_monthly_report(property_id: str, year: int = None, month: int = None) -> Dict[str, Any]:
    """Generate comprehensive monthly report."""
    
    if year is None or month is None:
        # Default to previous month
        today = datetime.now()
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1
    
    # Get date ranges
    start_date, end_date = get_month_dates(year, month)
    prev_start, prev_end = get_previous_month_dates(year, month)
    
    try:
        credentials = get_credentials()
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        # Core metrics
        metrics_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="returningUsers"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="engagementRate"),
                Metric(name="conversions"),
                Metric(name="sessionConversionRate"),
                Metric(name="totalAdRevenue"),
            ],
        )
        
        # Previous month for comparison
        prev_metrics_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=prev_start, end_date=prev_end)],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="conversions"),
            ],
        )
        
        # Geographic data
        geo_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="country"), Dimension(name="region")],
            metrics=[Metric(name="sessions"), Metric(name="totalUsers")],
            limit=20,
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        # Device breakdown
        device_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="deviceCategory")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews"),
                Metric(name="conversions"),
            ],
        )
        
        # Daily trend
        daily_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="sessions"), Metric(name="totalUsers"), Metric(name="conversions")],
            order_bys=[{"dimension": {"dimension_name": "date"}}],
        )
        
        # Top content
        content_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="averageEngagementTime"),
                Metric(name="conversions"),
            ],
            limit=20,
            order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
        )
        
        # Execute requests
        metrics_response = client.run_report(metrics_request)
        prev_metrics_response = client.run_report(prev_metrics_request)
        geo_response = client.run_report(geo_request)
        device_response = client.run_report(device_request)
        daily_response = client.run_report(daily_request)
        content_response = client.run_report(content_request)
        
        # Parse metrics
        metrics = {}
        if metrics_response.rows:
            row = metrics_response.rows[0]
            metrics = {
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "new_users": int(row.metric_values[2].value),
                "returning_users": int(row.metric_values[3].value),
                "pageviews": int(row.metric_values[4].value),
                "bounce_rate": float(row.metric_values[5].value) * 100,
                "avg_session_duration": float(row.metric_values[6].value),
                "engagement_rate": float(row.metric_values[7].value) * 100,
                "conversions": float(row.metric_values[8].value),
                "conversion_rate": float(row.metric_values[9].value) * 100,
                "ad_revenue": float(row.metric_values[10].value) if row.metric_values[10].value else 0,
            }
        
        # Parse previous month metrics
        prev_metrics = {}
        if prev_metrics_response.rows:
            row = prev_metrics_response.rows[0]
            prev_metrics = {
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "new_users": int(row.metric_values[2].value),
                "pageviews": int(row.metric_values[3].value),
                "conversions": float(row.metric_values[4].value),
            }
        
        # Parse geographic data
        geo_data = []
        for row in geo_response.rows:
            geo_data.append({
                "country": row.dimension_values[0].value,
                "region": row.dimension_values[1].value,
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
            })
        
        # Parse device data
        device_data = []
        for row in device_response.rows:
            device_data.append({
                "category": row.dimension_values[0].value,
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "pageviews": int(row.metric_values[2].value),
                "conversions": float(row.metric_values[3].value),
            })
        
        # Parse daily trends
        daily_trends = []
        for row in daily_response.rows:
            daily_trends.append({
                "date": row.dimension_values[0].value,
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "conversions": float(row.metric_values[2].value),
            })
        
        # Parse content performance
        content_data = []
        for row in content_response.rows:
            content_data.append({
                "title": row.dimension_values[0].value,
                "path": row.dimension_values[1].value,
                "pageviews": int(row.metric_values[0].value),
                "avg_engagement_time": float(row.metric_values[1].value),
                "conversions": float(row.metric_values[2].value),
            })
        
        # Calculate MoM changes
        changes = {}
        for key in ["sessions", "users", "new_users", "pageviews", "conversions"]:
            if key in prev_metrics and prev_metrics[key] > 0:
                change_pct = ((metrics.get(key, 0) - prev_metrics[key]) / prev_metrics[key]) * 100
                changes[key] = change_pct
            else:
                changes[key] = 0
        
        report = {
            "report_type": "monthly",
            "property_id": property_id,
            "month": f"{year}-{month:02d}",
            "date_range": {"start": start_date, "end": end_date},
            "previous_month": {"start": prev_start, "end": prev_end},
            "metrics": metrics,
            "previous_metrics": prev_metrics,
            "mom_changes": changes,
            "geographic_data": geo_data,
            "device_breakdown": device_data,
            "daily_trends": daily_trends,
            "top_content": content_data,
            "generated_at": datetime.now().isoformat(),
        }
        
        return report
        
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)


def output_console(report: Dict[str, Any]):
    """Output report in console format."""
    print("=" * 80)
    print("MONTHLY DEEP-DIVE ANALYSIS - FedBuyOut")
    print("=" * 80)
    print(f"Month: {report['month']}")
    print(f"Period: {report['date_range']['start']} to {report['date_range']['end']}")
    print("=" * 80)
    
    metrics = report.get("metrics", {})
    changes = report.get("mom_changes", {})
    
    print("\n📊 MONTH-OVER-MONTH COMPARISON")
    print("-" * 70)
    print(f"{'Metric':<25} {'This Month':>15} {'Last Month':>15} {'Change':>12}")
    print("-" * 70)
    
    mom_metrics = [
        ("Sessions", "sessions"),
        ("Users", "users"),
        ("New Users", "new_users"),
        ("Pageviews", "pageviews"),
        ("Conversions", "conversions"),
    ]
    
    for label, key in mom_metrics:
        cur = metrics.get(key, 0)
        prev = report.get("previous_metrics", {}).get(key, 0)
        chg = changes.get(key, 0)
        indicator = "📈" if chg > 0 else "📉" if chg < 0 else "➡️"
        print(f"{label:<25} {format_number(int(cur)):>15} {format_number(int(prev)):>15} "
              f"{format_percent(chg):>10} {indicator}")
    
    print("\n📈 DETAILED METRICS")
    print("-" * 50)
    print(f"  Returning Users:    {format_number(metrics.get('returning_users', 0))}")
    print(f"  Bounce Rate:        {format_percent(metrics.get('bounce_rate', 0))}")
    print(f"  Avg Session:        {format_duration(metrics.get('avg_session_duration', 0))}")
    print(f"  Engagement Rate:    {format_percent(metrics.get('engagement_rate', 0))}")
    print(f"  Conversion Rate:    {format_percent(metrics.get('conversion_rate', 0))}")
    
    print("\n🌍 TOP GEOGRAPHIC REGIONS")
    print("-" * 70)
    print(f"{'Country':<30} {'Region':<20} {'Sessions':>12} {'Users':>10}")
    print("-" * 70)
    for geo in report.get("geographic_data", [])[:10]:
        print(f"{geo['country']:<30} {geo['region']:<20} "
              f"{format_number(geo['sessions']):>12} {format_number(geo['users']):>10}")
    
    print("\n📱 DEVICE BREAKDOWN")
    print("-" * 70)
    print(f"{'Category':<15} {'Sessions':>12} {'Users':>12} {'Pageviews':>12} {'Conv.':>10}")
    print("-" * 70)
    for device in report.get("device_breakdown", []):
        print(f"{device['category']:<15} {format_number(device['sessions']):>12} "
              f"{format_number(device['users']):>12} {format_number(device['pageviews']):>12} "
              f"{format_number(int(device['conversions'])):>10}")
    
    print("\n📄 TOP CONTENT")
    print("-" * 80)
    print(f"{'Page':<45} {'Views':>12} {'Eng. Time':>12} {'Conversions':>12}")
    print("-" * 80)
    for content in report.get("top_content", [])[:10]:
        title = content['title'][:43] if content['title'] else "(untitled)"
        print(f"{title:<45} {format_number(content['pageviews']):>12} "
              f"{format_duration(content['avg_engagement_time']):>12} "
              f"{format_number(int(content['conversions'])):>12}")
    
    print("\n📈 DAILY TREND (Sessions)")
    print("-" * 50)
    trends = report.get("daily_trends", [])
    if trends:
        max_sessions = max(t['sessions'] for t in trends) if trends else 1
        for day in trends[::max(1, len(trends)//10)]:  # Sample ~10 days
            bar_len = int((day['sessions'] / max(max_sessions, 1)) * 30)
            bar = "█" * bar_len
            print(f"  {day['date']} {bar} {format_number(day['sessions'])}")
    
    print("\n" + "=" * 80)
    print(f"Generated: {report['generated_at']}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Generate monthly deep-dive report from Google Analytics 4"
    )
    parser.add_argument(
        "--property",
        default=DEFAULT_PROPERTY_ID,
        help=f"GA4 Property ID (default: {DEFAULT_PROPERTY_ID})"
    )
    parser.add_argument(
        "--month",
        help="Month to report (YYYY-MM format, default: previous month)"
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
    
    year, month = None, None
    if args.month:
        try:
            year, month = map(int, args.month.split("-"))
        except ValueError:
            print("Error: Month must be in YYYY-MM format", file=sys.stderr)
            sys.exit(1)
    
    report = run_monthly_report(args.property, year, month)
    
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
