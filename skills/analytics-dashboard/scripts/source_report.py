#!/usr/bin/env python3
"""
Traffic Source Breakdown Report Generator
Detailed analysis of traffic channels and sources.
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


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def run_source_report(property_id: str, days: int = 7) -> Dict[str, Any]:
    """Generate traffic source breakdown report."""
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")
    
    try:
        credentials = get_credentials()
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        # Default channel grouping
        channel_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
                Metric(name="engagementRate"),
                Metric(name="conversions"),
            ],
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        # Source/Medium breakdown
        source_medium_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="sessionSource"), Dimension(name="sessionMedium")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="conversions"),
            ],
            limit=20,
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        # Referral sources
        referral_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="pageReferrer")],
            metrics=[Metric(name="sessions"), Metric(name="totalUsers")],
            limit=15,
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        # Search terms (if available)
        search_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="searchTerm")],
            metrics=[Metric(name="sessions")],
            limit=15,
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        # Campaign performance (if campaigns exist)
        campaign_request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name="sessionCampaign")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="conversions"),
            ],
            limit=10,
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        )
        
        # Execute requests
        channel_response = client.run_report(channel_request)
        source_medium_response = client.run_report(source_medium_request)
        referral_response = client.run_report(referral_request)
        search_response = client.run_report(search_request)
        campaign_response = client.run_report(campaign_request)
        
        # Parse channel data
        channels = []
        total_sessions = 0
        for row in channel_response.rows:
            sessions = int(row.metric_values[0].value)
            total_sessions += sessions
            channels.append({
                "channel": row.dimension_values[0].value,
                "sessions": sessions,
                "users": int(row.metric_values[1].value),
                "new_users": int(row.metric_values[2].value),
                "pageviews": int(row.metric_values[3].value),
                "avg_session_duration": float(row.metric_values[4].value),
                "bounce_rate": float(row.metric_values[5].value) * 100,
                "engagement_rate": float(row.metric_values[6].value) * 100,
                "conversions": float(row.metric_values[7].value),
            })
        
        # Add percentage to channels
        for ch in channels:
            ch["share"] = (ch["sessions"] / total_sessions * 100) if total_sessions > 0 else 0
        
        # Parse source/medium
        source_medium = []
        for row in source_medium_response.rows:
            source_medium.append({
                "source": row.dimension_values[0].value,
                "medium": row.dimension_values[1].value,
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "conversions": float(row.metric_values[2].value),
            })
        
        # Parse referrals
        referrals = []
        for row in referral_response.rows:
            referrer = row.dimension_values[0].value
            if referrer and referrer != "(direct)":
                referrals.append({
                    "referrer": referrer,
                    "sessions": int(row.metric_values[0].value),
                    "users": int(row.metric_values[1].value),
                })
        
        # Parse search terms
        search_terms = []
        for row in search_response.rows:
            term = row.dimension_values[0].value
            if term and term != "(not set)":
                search_terms.append({
                    "term": term,
                    "sessions": int(row.metric_values[0].value),
                })
        
        # Parse campaigns
        campaigns = []
        for row in campaign_response.rows:
            campaign = row.dimension_values[0].value
            if campaign and campaign != "(not set)":
                campaigns.append({
                    "campaign": campaign,
                    "sessions": int(row.metric_values[0].value),
                    "users": int(row.metric_values[1].value),
                    "conversions": float(row.metric_values[2].value),
                })
        
        report = {
            "report_type": "source_breakdown",
            "property_id": property_id,
            "date_range": {"start": start_date, "end": end_date, "days": days},
            "total_sessions": total_sessions,
            "channels": channels,
            "source_medium": source_medium,
            "referrals": referrals,
            "search_terms": search_terms,
            "campaigns": campaigns,
            "generated_at": datetime.now().isoformat(),
        }
        
        return report
        
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        sys.exit(1)


def output_console(report: Dict[str, Any]):
    """Output report in console format."""
    print("=" * 80)
    print("TRAFFIC SOURCE BREAKDOWN - FedBuyOut")
    print("=" * 80)
    print(f"Period: {report['date_range']['start']} to {report['date_range']['end']}")
    print(f"Total Sessions: {format_number(report['total_sessions'])}")
    print("=" * 80)
    
    print("\n📊 CHANNEL PERFORMANCE")
    print("-" * 90)
    print(f"{'Channel':<20} {'Sessions':>12} {'Share':>8} {'Users':>10} {'Bounce':>8} "
          f"{'Engage':>8} {'Conv.':>10}")
    print("-" * 90)
    
    for ch in report.get("channels", []):
        print(f"{ch['channel']:<20} {format_number(ch['sessions']):>12} "
              f"{format_percent(ch['share']):>8} {format_number(ch['users']):>10} "
              f"{format_percent(ch['bounce_rate']):>8} {format_percent(ch['engagement_rate']):>8} "
              f"{format_number(int(ch['conversions'])):>10}")
    
    print("\n🔗 TOP SOURCE/MEDIUM COMBINATIONS")
    print("-" * 70)
    print(f"{'Source':<25} {'Medium':<15} {'Sessions':>12} {'Users':>10}")
    print("-" * 70)
    for sm in report.get("source_medium", [])[:10]:
        print(f"{sm['source']:<25} {sm['medium']:<15} "
              f"{format_number(sm['sessions']):>12} {format_number(sm['users']):>10}")
    
    if report.get("referrals"):
        print("\n🌐 TOP REFERRAL SOURCES")
        print("-" * 60)
        print(f"{'Referrer':<45} {'Sessions':>10}")
        print("-" * 60)
        for ref in report.get("referrals", [])[:10]:
            domain = ref['referrer'][:43] if len(ref['referrer']) > 43 else ref['referrer']
            print(f"{domain:<45} {format_number(ref['sessions']):>10}")
    
    if report.get("search_terms"):
        print("\n🔍 TOP SEARCH TERMS")
        print("-" * 50)
        print(f"{'Search Term':<35} {'Sessions':>10}")
        print("-" * 50)
        for term in report.get("search_terms", [])[:10]:
            display_term = term['term'][:33] if len(term['term']) > 33 else term['term']
            print(f"{display_term:<35} {format_number(term['sessions']):>10}")
    
    if report.get("campaigns"):
        print("\n📢 CAMPAIGN PERFORMANCE")
        print("-" * 70)
        print(f"{'Campaign':<35} {'Sessions':>12} {'Users':>10} {'Conversions':>10}")
        print("-" * 70)
        for camp in report.get("campaigns", []):
            name = camp['campaign'][:33] if len(camp['campaign']) > 33 else camp['campaign']
            print(f"{name:<35} {format_number(camp['sessions']):>12} "
                  f"{format_number(camp['users']):>10} {format_number(int(camp['conversions'])):>10}")
    
    # Channel visualization
    print("\n📈 CHANNEL DISTRIBUTION")
    print("-" * 50)
    for ch in report.get("channels", []):
        bar_len = int(ch['share'] / 2)
        bar = "█" * bar_len
        print(f"  {ch['channel']:<20} {bar} {format_percent(ch['share'])}")
    
    print("\n" + "=" * 80)
    print(f"Generated: {report['generated_at']}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Generate traffic source breakdown report from Google Analytics 4"
    )
    parser.add_argument(
        "--property",
        default=DEFAULT_PROPERTY_ID,
        help=f"GA4 Property ID (default: {DEFAULT_PROPERTY_ID})"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to report (default: 7)"
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
    
    report = run_source_report(args.property, args.days)
    
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
