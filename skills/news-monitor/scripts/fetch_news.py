#!/usr/bin/env python3
"""
Fetch and analyze federal buyout news from RSS feeds.
Monitors multiple sources and scores articles for relevance.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    os.system("pip3 install requests beautifulsoup4 -q")
    import requests
    from bs4 import BeautifulSoup

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
ARTICLES_FILE = DATA_DIR / "articles.json"

# RSS Feed sources
FEEDS = {
    "fedsmith": {
        "url": "https://www.fedsmith.com/feed/",
        "priority": "high",
        "name": "FedSmith"
    },
    "govexec": {
        "url": "https://www.govexec.com/rss/all-news.xml",
        "priority": "high",
        "name": "GovExec"
    },
    "federal-news-network": {
        "url": "https://federalnewsnetwork.com/feed/",
        "priority": "high",
        "name": "Federal News Network"
    },
    "federal-times": {
        "url": "https://www.federaltimes.com/arc/outboundfeeds/rss/?outputType=xml",
        "priority": "high",
        "name": "Federal Times"
    },
    "federal-soup": {
        "url": "https://www.federalsoup.com/rss/news",
        "priority": "medium",
        "name": "Federal Soup"
    },
    "opm": {
        "url": "https://www.opm.gov/news/releases/rss/releases.xml",
        "priority": "high",
        "name": "OPM"
    },
}

# Keywords with weights
KEYWORDS = {
    "high": {
        "weight": 30,
        "terms": [
            "VSIP", "Voluntary Separation Incentive",
            "federal buyout", "federal employee buyout",
            "early retirement", "Voluntary Early Retirement", "VER",
            "buyout offer", "separation incentive"
        ]
    },
    "medium": {
        "weight": 15,
        "terms": [
            "federal workforce reduction", "Reduction in Force", "RIF",
            "federal layoffs", "federal employee severance",
            "workforce restructuring", "federal downsizing",
            "federal employee departure", "federal retirement surge",
            "federal attrition", "federal hiring freeze",
            "federal job cuts", "federal position elimination"
        ]
    },
    "context": {
        "weight": 5,
        "terms": [
            "federal employee", "government worker", "civil service",
            "federal agency", "OPM", "federal budget", "government spending",
            "federal compensation", "federal benefits", "FERS", "CSRS", "TSP",
            "federal pension"
        ]
    }
}

EXCLUSION_TERMS = [
    "private sector buyout", "corporate buyout", "private equity",
    "defense contractor", "state employee", "municipal employee", "county worker"
]


def load_articles():
    """Load previously tracked articles."""
    if ARTICLES_FILE.exists():
        with open(ARTICLES_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_articles(articles):
    """Save articles to storage."""
    with open(ARTICLES_FILE, 'w') as f:
        json.dump(articles, f, indent=2)


def fetch_feed(feed_url, source_name):
    """Fetch and parse RSS feed."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)',
            'Accept': 'application/rss+xml,application/xml,*/*'
        }
        response = requests.get(feed_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Handle RSS 2.0 and Atom formats
        items = []
        channel = root.find('.//channel')
        if channel is not None:
            # RSS 2.0
            for item in channel.findall('item'):
                items.append(parse_rss_item(item, source_name))
        else:
            # Atom
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                items.append(parse_atom_entry(entry, source_name, ns))
        
        return items
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        return []


def parse_rss_item(item, source):
    """Parse RSS 2.0 item."""
    title = item.findtext('title', '')
    link = item.findtext('link', '')
    desc = item.findtext('description', '')
    pub_date = item.findtext('pubDate', '')
    
    # Try to get content if available
    content = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
    content_text = content.text if content is not None else desc
    
    return {
        'title': clean_text(title),
        'url': link,
        'description': clean_text(desc),
        'content': clean_text(content_text),
        'published': parse_date(pub_date),
        'source': source
    }


def parse_atom_entry(entry, source, ns):
    """Parse Atom entry."""
    title = entry.findtext('atom:title', '', ns)
    link_elem = entry.find('atom:link', ns)
    link = link_elem.get('href', '') if link_elem is not None else ''
    content = entry.findtext('atom:content', '', ns) or entry.findtext('atom:summary', '', ns)
    pub_date = entry.findtext('atom:published', '', ns) or entry.findtext('atom:updated', '', ns)
    
    return {
        'title': clean_text(title),
        'url': link,
        'description': clean_text(content)[:500],
        'content': clean_text(content),
        'published': parse_date(pub_date),
        'source': source
    }


def clean_text(text):
    """Clean HTML and normalize text."""
    if not text:
        return ''
    # Remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text(separator=' ')
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()


def parse_date(date_str):
    """Parse various date formats."""
    if not date_str:
        return datetime.now().isoformat()
    
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str[:25], fmt)
            return dt.isoformat()
        except:
            continue
    
    return datetime.now().isoformat()


def score_article(article):
    """Calculate relevance score for article."""
    score = 0
    title_lower = article['title'].lower()
    content_lower = article['content'].lower() if article['content'] else ''
    
    # Check exclusion terms
    for term in EXCLUSION_TERMS:
        if term.lower() in title_lower or term.lower() in content_lower:
            score -= 20
    
    # Score keywords in title
    for category, data in KEYWORDS.items():
        weight = data['weight']
        for term in data['terms']:
            term_lower = term.lower()
            if term_lower in title_lower:
                score += weight
            if term_lower in content_lower:
                score += weight // 3
    
    # Source bonus
    source_priority = FEEDS.get(article['source'], {}).get('priority', 'low')
    if source_priority == 'high':
        score += 10
    elif source_priority == 'medium':
        score += 5
    else:
        score += 2
    
    # Recency bonus
    try:
        pub_date = datetime.fromisoformat(article['published'].replace('Z', '+00:00'))
        age = datetime.now() - pub_date.replace(tzinfo=None)
        if age < timedelta(hours=1):
            score += 5
        elif age < timedelta(hours=4):
            score += 3
        elif age < timedelta(hours=24):
            score += 1
    except:
        pass
    
    return min(100, max(0, score))


def fetch_article_content(url):
    """Fetch full article content from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content
        article = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        if article:
            return clean_text(article.get_text())
        
        # Fallback to body
        return clean_text(soup.get_text())[:5000]
    except Exception as e:
        return ''


def check_news(sources=None, full_fetch=False, json_output=False):
    """Main function to check for news."""
    articles_db = load_articles()
    new_articles = []
    
    feed_list = [(k, v) for k, v in FEEDS.items() if sources is None or k in sources]
    
    for source_key, feed_info in feed_list:
        print(f"Fetching from {feed_info['name']}...")
        items = fetch_feed(feed_info['url'], source_key)
        
        for item in items:
            # Skip if already tracked
            if item['url'] in articles_db:
                continue
            
            # Fetch full content if requested
            if full_fetch and not item['content']:
                item['content'] = fetch_article_content(item['url'])
            
            # Score the article
            item['score'] = score_article(item)
            item['fetched_at'] = datetime.now().isoformat()
            
            # Store in database
            articles_db[item['url']] = item
            new_articles.append(item)
        
        time.sleep(2)  # Be nice to servers
    
    save_articles(articles_db)
    
    # Sort by score
    new_articles.sort(key=lambda x: x['score'], reverse=True)
    
    if json_output:
        print(json.dumps(new_articles, indent=2))
    else:
        # Print summary
        high_relevance = [a for a in new_articles if a['score'] >= 70]
        medium_relevance = [a for a in new_articles if 40 <= a['score'] < 70]
        low_relevance = [a for a in new_articles if a['score'] < 40]
        
        print(f"\n{'='*60}")
        print(f"Found {len(new_articles)} new articles")
        print(f"{'='*60}")
        
        if high_relevance:
            print(f"\n🔴 HIGH RELEVANCE (Score 70+): {len(high_relevance)}")
            for art in high_relevance[:5]:
                print(f"\n  [{art['score']}] {art['title']}")
                print(f"      Source: {FEEDS.get(art['source'], {}).get('name', art['source'])}")
                print(f"      URL: {art['url']}")
        
        if medium_relevance:
            print(f"\n🟡 MEDIUM RELEVANCE (Score 40-69): {len(medium_relevance)}")
            for art in medium_relevance[:5]:
                print(f"\n  [{art['score']}] {art['title']}")
                print(f"      Source: {FEEDS.get(art['source'], {}).get('name', art['source'])}")
        
        if low_relevance:
            print(f"\n🟢 LOW RELEVANCE (Score <40): {len(low_relevance)}")
    
    return new_articles


def main():
    parser = argparse.ArgumentParser(description='Fetch federal buyout news')
    parser.add_argument('--check', action='store_true', help='Check for new articles')
    parser.add_argument('--full', action='store_true', help='Fetch full article content')
    parser.add_argument('--source', help='Fetch from specific source only')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--since', help='Only show articles since date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    sources = [args.source] if args.source else None
    
    if args.check or args.full:
        check_news(sources=sources, full_fetch=args.full, json_output=args.json)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
