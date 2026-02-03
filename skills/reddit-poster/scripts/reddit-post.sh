#!/bin/bash
# Reddit Posting Script
# Usage: ./reddit-post.sh "subreddit" "title" "content"

SUBREDDIT="$1"
TITLE="$2"
CONTENT="$3"

if [ -z "$SUBREDDIT" ] || [ -z "$TITLE" ] || [ -z "$CONTENT" ]; then
    echo "Usage: $0 <subreddit> <title> <content>"
    echo "Example: $0 fednews 'TSP Performance' 'Check out this calculator'"
    exit 1
fi

# Note: This requires Reddit credentials
# For now, output what would be posted
echo "=== REDDIT POST READY ==="
echo "Subreddit: r/$SUBREDDIT"
echo "Title: $TITLE"
echo "Content: $CONTENT"
echo ""
echo "To post manually:"
echo "1. Go to https://www.reddit.com/r/$SUBREDDIT/submit"
echo "2. Paste title: $TITLE"
echo "3. Paste content: $CONTENT"
echo "=========================="