#!/usr/bin/env python3
"""
Summarize article content using extractive summarization.
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import os
    os.system("pip3 install requests beautifulsoup4 -q")
    import requests
    from bs4 import BeautifulSoup


def fetch_article(url):
    """Fetch article content from URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.content


def extract_content(html):
    """Extract readable content from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove unwanted elements
    for elem in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
        elem.decompose()
    
    # Try to find main content
    selectors = [
        'article',
        'main',
        '[role="main"]',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.content',
        '#content'
    ]
    
    content = None
    for selector in selectors:
        content = soup.select_one(selector)
        if content:
            break
    
    if not content:
        content = soup.find('body')
    
    # Get paragraphs
    paragraphs = content.find_all('p')
    text = '\n\n'.join(p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50)
    
    # Get title
    title = soup.find('h1')
    title_text = title.get_text().strip() if title else ''
    
    return {
        'title': title_text,
        'text': text,
        'paragraphs': [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30]
    }


def score_sentences(paragraphs):
    """Score sentences based on position and keywords."""
    sentences = []
    word_freq = {}
    
    # Build word frequency
    all_text = ' '.join(paragraphs).lower()
    words = re.findall(r'\b[a-z]{4,}\b', all_text)
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences
    for i, para in enumerate(paragraphs):
        para_sentences = re.split(r'(?<=[.!?])\s+', para)
        for j, sent in enumerate(para_sentences):
            if len(sent) < 30:
                continue
            
            score = 0
            # Position bonus (earlier sentences score higher)
            if i == 0:
                score += 3
            elif i < 3:
                score += 2
            
            # First sentence of paragraph
            if j == 0:
                score += 1
            
            # Keyword density
            sent_words = re.findall(r'\b[a-z]{4,}\b', sent.lower())
            for word in sent_words:
                score += word_freq.get(word, 0) * 0.01
            
            # Length penalty (avoid very long sentences)
            if len(sent) > 200:
                score -= 0.5
            
            sentences.append({
                'text': sent,
                'score': score,
                'position': (i, j)
            })
    
    return sentences


def summarize(text, paragraphs, num_sentences=5):
    """Generate extractive summary."""
    sentences = score_sentences(paragraphs)
    sentences.sort(key=lambda x: x['score'], reverse=True)
    
    # Take top sentences
    top_sentences = sentences[:num_sentences]
    # Sort by original position
    top_sentences.sort(key=lambda x: x['position'])
    
    summary = ' '.join(s['text'] for s in top_sentences)
    return summary


def extract_key_points(paragraphs):
    """Extract key points from article."""
    key_points = []
    
    # Look for important patterns
    patterns = [
        r'(?:announced?|said|stated|reported)\s+[^.]*\d[^.]*\.',
        r'\$\d[\d,]*\s*(?:million|billion)?',
        r'\d+%',
        r'(?:will|plans? to|expected to)\s+[^.]{10,100}\.',
        r'(?:VSIP|buyout|early retirement|RIF|workforce)[^.]*\.',
    ]
    
    for para in paragraphs[:10]:  # Check first 10 paragraphs
        for pattern in patterns:
            matches = re.findall(pattern, para, re.IGNORECASE)
            for match in matches:
                if len(match) > 20 and match not in key_points:
                    key_points.append(match)
                    if len(key_points) >= 5:
                        break
    
    return key_points[:5]


def summarize_article(url=None, file_path=None, sentences=5):
    """Main summarization function."""
    if url:
        html = fetch_article(url)
        source = urlparse(url).netloc
    elif file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        source = file_path
    else:
        print("Error: Provide --url or --file")
        return
    
    article = extract_content(html)
    
    if not article['paragraphs']:
        print("Could not extract article content")
        return
    
    # Generate summary
    summary = summarize(article['text'], article['paragraphs'], sentences)
    key_points = extract_key_points(article['paragraphs'])
    
    # Output
    result = {
        'title': article['title'],
        'source': source,
        'summary': summary,
        'key_points': key_points,
        'word_count': len(article['text'].split()),
        'summary_length': len(summary.split())
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Summarize article content')
    parser.add_argument('--url', help='Article URL to summarize')
    parser.add_argument('--file', help='HTML file to summarize')
    parser.add_argument('--sentences', type=int, default=5, help='Number of sentences in summary')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.url and not args.file:
        parser.print_help()
        sys.exit(1)
    
    result = summarize_article(args.url, args.file, args.sentences)
    
    if not result:
        sys.exit(1)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"TITLE: {result['title']}")
        print(f"SOURCE: {result['source']}")
        print(f"{'='*60}\n")
        
        print("SUMMARY:")
        print(result['summary'])
        
        if result['key_points']:
            print(f"\n{'='*60}")
            print("KEY POINTS:")
            for i, point in enumerate(result['key_points'], 1):
                print(f"  {i}. {point}")
        
        print(f"\n{'='*60}")
        print(f"Original: {result['word_count']} words | Summary: {result['summary_length']} words")


if __name__ == '__main__':
    main()
