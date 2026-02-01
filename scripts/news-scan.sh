#!/bin/bash
# FedBuyOut News Scanner
# Scans federal employee news sources for content ideas
# Run this daily via cron

export PATH="/root/go/bin:/usr/local/go/bin:$PATH"

# Check if blogwatcher is installed
if ! command -v blogwatcher &> /dev/null; then
    echo "blogwatcher not installed yet. Skipping scan."
    exit 0
fi

echo "=== FedBuyOut News Scan - $(date) ===" >> /root/.openclaw/workspace/fedbuyout/logs/news-scan.log

# Scan all tracked blogs
blogwatcher scan 2>&1 | tee -a /root/.openclaw/workspace/fedbuyout/logs/news-scan.log

# Get new articles
NEW_ARTICLES=$(blogwatcher articles --unread 2>/dev/null | head -20)

if [ -n "$NEW_ARTICLES" ]; then
    echo "New articles found:" >> /root/.openclaw/workspace/fedbuyout/logs/news-scan.log
    echo "$NEW_ARTICLES" >> /root/.openclaw/workspace/fedbuyout/workspace/fedbuyout/logs/news-scan.log
    
    # Send notification (when email is configured)
    # echo "$NEW_ARTICLES" | mail -s "FedBuyOut Daily News" admin@fedbuyout.com
else
    echo "No new articles today." >> /root/.openclaw/workspace/fedbuyout/logs/news-scan.log
fi

echo "" >> /root/.openclaw/workspace/fedbuyout/logs/news-scan.log
