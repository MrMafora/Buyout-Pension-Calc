#!/usr/bin/env python3
"""
Share federal buyout articles to social media platforms.
Supports Twitter/X, LinkedIn, and generic webhook sharing.
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:
    os.system("pip3 install python-dotenv -q")
    from dotenv import load_dotenv

# Load environment
DATA_DIR = Path(__file__).parent.parent / "data"
load_dotenv(DATA_DIR.parent / '.env')


def load_article(url):
    """Load article from database."""
    articles_file = DATA_DIR / "articles.json"
    if articles_file.exists():
        with open(articles_file, 'r') as f:
            articles = json.load(f)
            return articles.get(url)
    return None


def shorten_text(text, max_len, suffix='...'):
    """Shorten text to fit within limit."""
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def share_to_twitter(article, custom_message=None):
    """Share article to Twitter/X."""
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_secret = os.getenv('TWITTER_ACCESS_SECRET')
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("❌ Twitter credentials not configured")
        return False
    
    try:
        import tweepy
        
        # Authenticate
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
        # Build tweet
        title = article.get('title', '')
        url = article.get('url', '')
        
        if custom_message:
            text = f"{custom_message} {title} {url}"
        else:
            text = f"📰 Federal Buyout News: {title} {url}"
        
        # Twitter limit is 280 chars
        text = shorten_text(text, 280)
        
        # Post tweet
        response = client.create_tweet(text=text)
        
        if response and response.data:
            tweet_id = response.data['id']
            print(f"✅ Posted to Twitter: https://twitter.com/i/web/status/{tweet_id}")
            return True
        
    except ImportError:
        print("Installing tweepy...")
        os.system("pip3 install tweepy -q")
        return share_to_twitter(article, custom_message)
    except Exception as e:
        print(f"❌ Twitter error: {e}")
        return False


def share_to_linkedin(article, custom_message=None):
    """Share article to LinkedIn."""
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ LinkedIn access token not configured")
        return False
    
    try:
        import requests
        
        title = article.get('title', '')
        url = article.get('url', '')
        desc = article.get('description', '')[:200]
        
        # Build share text
        if custom_message:
            text = f"{custom_message}\n\n{title}\n{desc}"
        else:
            text = f"📰 Federal Buyout Update:\n\n{title}\n\n{desc}"
        
        # LinkedIn API v2 share
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Get user ID first
        me_response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers
        )
        
        if me_response.status_code != 200:
            print(f"❌ LinkedIn auth failed: {me_response.text}")
            return False
        
        user_id = me_response.json().get('id')
        
        # Create share
        share_data = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": url,
                        "title": {"text": title[:200]},
                        "description": {"text": desc}
                    }]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=share_data
        )
        
        if response.status_code in [200, 201]:
            post_id = response.headers.get('X-RestLi-Id', 'unknown')
            print(f"✅ Posted to LinkedIn: {post_id}")
            return True
        else:
            print(f"❌ LinkedIn post failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ LinkedIn error: {e}")
        return False


def share_to_bluesky(article, custom_message=None):
    """Share article to Bluesky."""
    handle = os.getenv('BLUESKY_HANDLE')
    password = os.getenv('BLUESKY_PASSWORD')
    
    if not handle or not password:
        print("❌ Bluesky credentials not configured")
        return False
    
    try:
        import requests
        
        # Authenticate
        auth_response = requests.post(
            'https://bsky.social/xrpc/com.atproto.server.createSession',
            json={'identifier': handle, 'password': password}
        )
        
        if auth_response.status_code != 200:
            print(f"❌ Bluesky auth failed")
            return False
        
        session = auth_response.json()
        access_token = session['accessJwt']
        did = session['did']
        
        # Build post
        title = article.get('title', '')
        url = article.get('url', '')
        
        if custom_message:
            text = f"{custom_message} {title} {url}"
        else:
            text = f"📰 Federal Buyout News: {title}\n\n{url}"
        
        text = shorten_text(text, 300)
        
        # Create post
        post_response = requests.post(
            'https://bsky.social/xrpc/com.atproto.repo.createRecord',
            headers={'Authorization': f'Bearer {access_token}'},
            json={
                'repo': did,
                'collection': 'app.bsky.feed.post',
                'record': {
                    '$type': 'app.bsky.feed.post',
                    'text': text,
                    'createdAt': datetime.now().isoformat()
                }
            }
        )
        
        if post_response.status_code == 200:
            print(f"✅ Posted to Bluesky")
            return True
        else:
            print(f"❌ Bluesky post failed: {post_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Bluesky error: {e}")
        return False


def generate_share_text(article, platform='generic'):
    """Generate platform-appropriate share text."""
    title = article.get('title', '')
    url = article.get('url', '')
    source = article.get('source', '')
    
    templates = {
        'twitter': f"📰 Federal Buyout News: {title} via @{source} {url}",
        'linkedin': f"📰 Federal Buyout Update\n\n{title}\n\nRead more: {url}",
        'bluesky': f"📰 Federal Buyout News: {title}\n\n{url}",
        'generic': f"Federal Buyout News: {title}\n{url}"
    }
    
    return templates.get(platform, templates['generic'])


def share_article(article_url, platforms=None, custom_message=None):
    """Share article to specified platforms."""
    # Load article
    article = load_article(article_url)
    if not article:
        # Try to fetch from URL
        print(f"Article not in database, fetching...")
        article = {
            'title': article_url.split('/')[-1].replace('-', ' ').title(),
            'url': article_url,
            'source': urlparse(article_url).netloc,
            'description': ''
        }
    
    # Default to all available platforms
    if not platforms:
        platforms = ['twitter', 'linkedin', 'bluesky']
    else:
        platforms = [p.strip().lower() for p in platforms.split(',')]
    
    results = {}
    
    print(f"Sharing: {article['title']}")
    print(f"Platforms: {', '.join(platforms)}\n")
    
    for platform in platforms:
        if platform == 'twitter':
            results['twitter'] = share_to_twitter(article, custom_message)
        elif platform == 'linkedin':
            results['linkedin'] = share_to_linkedin(article, custom_message)
        elif platform == 'bluesky':
            results['bluesky'] = share_to_bluesky(article, custom_message)
        else:
            print(f"❌ Unknown platform: {platform}")
            results[platform] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("Share Summary:")
    for platform, success in results.items():
        status = '✅' if success else '❌'
        print(f"  {status} {platform}")
    print(f"{'='*50}")
    
    return results


def preview_share(article_url):
    """Preview what would be shared without posting."""
    article = load_article(article_url)
    if not article:
        print(f"Article not found: {article_url}")
        return
    
    print(f"\n{'='*60}")
    print("SHARE PREVIEW")
    print(f"{'='*60}\n")
    
    print("TWITTER/X:")
    twitter_text = generate_share_text(article, 'twitter')
    print(f"  {twitter_text}")
    print(f"  Length: {len(twitter_text)}/280\n")
    
    print("LINKEDIN:")
    linkedin_text = generate_share_text(article, 'linkedin')
    print(f"  {linkedin_text}\n")
    
    print("BLUESKY:")
    bluesky_text = generate_share_text(article, 'bluesky')
    print(f"  {bluesky_text}")
    print(f"  Length: {len(bluesky_text)}/300\n")


def main():
    parser = argparse.ArgumentParser(description='Share articles to social media')
    parser.add_argument('--article', '-a', required=True, help='Article URL to share')
    parser.add_argument('--platforms', '-p', help='Comma-separated list: twitter,linkedin,bluesky')
    parser.add_argument('--message', '-m', help='Custom message prefix')
    parser.add_argument('--preview', action='store_true', help='Preview without posting')
    
    args = parser.parse_args()
    
    if args.preview:
        preview_share(args.article)
    else:
        share_article(args.article, args.platforms, args.message)


if __name__ == '__main__':
    main()
