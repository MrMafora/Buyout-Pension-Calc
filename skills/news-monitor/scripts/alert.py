#!/usr/bin/env python3
"""
Send alerts for high-relevance federal buyout news.
Supports email notifications and webhook integrations.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    os.system("pip3 install python-dotenv -q")
    from dotenv import load_dotenv

# Load environment
DATA_DIR = Path(__file__).parent.parent / "data"
load_dotenv(DATA_DIR.parent / '.env')

ALERTS_FILE = DATA_DIR / "alerts.json"


def load_alerts():
    """Load alert history."""
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return {'sent': [], 'errors': []}


def save_alerts(alerts):
    """Save alert history."""
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)


def load_article(url):
    """Load article from database."""
    articles_file = DATA_DIR / "articles.json"
    if articles_file.exists():
        with open(articles_file, 'r') as f:
            articles = json.load(f)
            return articles.get(url)
    return None


def format_alert_message(article, test=False):
    """Format alert message for an article."""
    prefix = "🧪 TEST ALERT" if test else "🚨 BREAKING"
    
    title = article.get('title', 'Unknown')
    url = article.get('url', '')
    score = article.get('score', 0)
    source = article.get('source', 'Unknown')
    desc = article.get('description', '')
    
    message = f"""{prefix}: Federal Buyout News

{title}

Relevance Score: {score}/100
Source: {source}

{desc[:500] if desc else ''}

Read more: {url}

---
FedBuyOut News Monitor
{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"""
    
    return message


def send_email_alert(article, test=False):
    """Send email alert using Resend API."""
    api_key = os.getenv('RESEND_API_KEY')
    to_email = os.getenv('ALERT_EMAIL', 'clark@fedbuyout.com')
    from_email = os.getenv('FROM_EMAIL', 'alerts@fedbuyout.com')
    
    if not api_key:
        print("Error: RESEND_API_KEY not set in .env")
        return False
    
    try:
        import requests
        
        title = article.get('title', 'Unknown')
        message = format_alert_message(article, test)
        
        response = requests.post(
            'https://api.resend.com/emails',
            headers={'Authorization': f'Bearer {api_key}'},
            json={
                'from': f'FedBuyOut Alerts <{from_email}>',
                'to': [to_email],
                'subject': f'{"TEST: " if test else ""}Federal Buyout Alert - {title[:50]}...',
                'text': message
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Email alert sent to {to_email}")
            return True
        else:
            print(f"❌ Email failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


def send_webhook_alert(article, test=False):
    """Send alert to webhook (for Slack, Discord, etc.)."""
    webhook_url = os.getenv('ALERT_WEBHOOK')
    
    if not webhook_url:
        return False
    
    try:
        import requests
        
        title = article.get('title', 'Unknown')
        url = article.get('url', '')
        score = article.get('score', 0)
        source = article.get('source', 'Unknown')
        
        # Try Slack format first
        payload = {
            'text': f"{'TEST: ' if test else ''}Federal Buyout Alert",
            'attachments': [{
                'title': title,
                'title_link': url,
                'fields': [
                    {'title': 'Source', 'value': source, 'short': True},
                    {'title': 'Relevance Score', 'value': f'{score}/100', 'short': True}
                ],
                'color': 'danger' if score >= 80 else 'warning'
            }]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code in [200, 204]:
            print(f"✅ Webhook alert sent")
            return True
        else:
            # Try Discord format
            discord_payload = {
                'content': f"{'**TEST** ' if test else ''}🚨 **Federal Buyout Alert**",
                'embeds': [{
                    'title': title[:256],
                    'url': url,
                    'fields': [
                        {'name': 'Source', 'value': source, 'inline': True},
                        {'name': 'Score', 'value': f'{score}/100', 'inline': True}
                    ],
                    'color': 0xff0000 if score >= 80 else 0xffaa00
                }]
            }
            
            response = requests.post(webhook_url, json=discord_payload, timeout=10)
            if response.status_code in [200, 204]:
                print(f"✅ Webhook alert sent (Discord format)")
                return True
            
            print(f"❌ Webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False


def send_alert(article_url, score=None, test=False):
    """Send alert for an article."""
    if test:
        # Create test article
        article = {
            'title': 'Test Alert - Federal Buyout News Monitor',
            'url': 'https://fedbuyout.com',
            'score': score or 85,
            'source': 'Test',
            'description': 'This is a test alert to verify the notification system is working correctly.'
        }
    else:
        article = load_article(article_url)
        if not article:
            print(f"Error: Article not found: {article_url}")
            return False
        
        if score:
            article['score'] = score
    
    results = {
        'article': article.get('title'),
        'timestamp': datetime.now().isoformat(),
        'email': False,
        'webhook': False
    }
    
    # Send email
    results['email'] = send_email_alert(article, test)
    
    # Send webhook
    results['webhook'] = send_webhook_alert(article, test)
    
    # Record alert
    if not test:
        alerts = load_alerts()
        alerts['sent'].append(results)
        save_alerts(alerts)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Alert Summary:")
    print(f"  Article: {article['title'][:60]}...")
    print(f"  Email: {'✅' if results['email'] else '❌'}")
    print(f"  Webhook: {'✅' if results['webhook'] else '❌'}")
    print(f"{'='*50}")
    
    return results['email'] or results['webhook']


def check_and_alert():
    """Check for high-priority articles and send alerts."""
    articles_file = DATA_DIR / "articles.json"
    if not articles_file.exists():
        print("No articles database found")
        return
    
    with open(articles_file, 'r') as f:
        articles = json.load(f)
    
    # Find unscored high-priority articles
    high_priority = []
    for url, art in articles.items():
        if art.get('score', 0) >= 70 and not art.get('alerted', False):
            high_priority.append((url, art))
    
    if not high_priority:
        print("No new high-priority articles to alert")
        return
    
    print(f"Found {len(high_priority)} high-priority articles")
    
    for url, art in high_priority:
        print(f"\nAlerting for: {art['title'][:60]}...")
        success = send_alert(url)
        if success:
            art['alerted'] = True
            articles[url] = art
    
    # Save updated articles
    with open(articles_file, 'w') as f:
        json.dump(articles, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Send alerts for federal buyout news')
    parser.add_argument('--article', '-a', help='Article URL to alert about')
    parser.add_argument('--score', '-s', type=int, help='Override relevance score')
    parser.add_argument('--check', '-c', action='store_true', help='Check for articles needing alerts')
    parser.add_argument('--test', '-t', action='store_true', help='Send test alert')
    
    args = parser.parse_args()
    
    if args.test:
        send_alert(None, args.score, test=True)
    elif args.check:
        check_and_alert()
    elif args.article:
        send_alert(args.article, args.score)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
