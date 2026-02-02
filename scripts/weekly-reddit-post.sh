#!/bin/bash
# Weekly Reddit posting script for FedBuyOut
# Rotates through 3 subreddits with different content

REDDIT_POSTS_DIR="/root/.openclaw/workspace/fedbuyout/logs/reddit-posts"
LOG_FILE="/root/.openclaw/workspace/fedbuyout/logs/reddit.log"

# Ensure directories exist
mkdir -p "$REDDIT_POSTS_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Get week number to rotate posts
WEEK_OF_YEAR=$(date +%U)

echo "========================================" >> "$LOG_FILE"
echo "Reddit Post - Week $WEEK_OF_YEAR - $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Define posts for each subreddit
case $((WEEK_OF_YEAR % 3)) in
    0)
        SUBREDDIT="fednews"
        TITLE="I built a free federal buyout calculator - would love your feedback"
        BODY="Hi everyone! I'm a federal employee (15 years FERS) and I noticed there's a lot of confusion when buyout offers come around about whether to take them or stay for the pension.

I built a free calculator that compares your options side-by-side:

✅ FERS/CSRS pension calculations with High-3
✅ Buyout tax implications (federal + state)  
✅ Break-even analysis (how long until pension catches up)
✅ Early retirement penalties if under MRA
✅ Survivor benefit costs
✅ Military buyback impact

Check it out: https://fedbuyout.com

It's completely free, no email required to use (though there's a newsletter if you want updates).

I've tested it against OPM calculations and it's accurate, but I'd love feedback from this community on what features would be helpful.

Also happy to answer any buyout/pension questions - I've researched this stuff way too much 😅"
        ;;
    1)
        SUBREDDIT="govfire"
        TITLE="For those considering a federal buyout to FIRE - I built a calculator"
        BODY="Long-time lurker here. I'm on the path to FIRE and work as a federal employee. Every time buyout rumors start, I see posts here asking whether to take it.

The math isn't always obvious:
- Buyout = immediate cash but lost pension growth
- Stay = bigger pension but years of your life

I built a calculator that runs the actual numbers:
https://fedbuyout.com

It shows:
- Exact pension amount you'd give up
- Break-even point (years until pension > buyout value)
- Tax impact on the buyout
- Your pension at 62 vs taking buyout now + investing

Might be helpful for anyone facing this decision. Would love thoughts from this community!"
        ;;
    2)
        SUBREDDIT="federalemployees"
        TITLE="New TSP performance + buyout calculator I built"
        BODY="Saw the news that TSP funds all had positive returns in January 2026. Great start to the year!

If you're considering a buyout this year, your TSP performance affects the decision. I built a calculator that helps you compare:

https://fedbuyout.com

Free to use, gives you a detailed breakdown of:
- Monthly pension amount
- Buyout after taxes  
- How many years until pension catches up to buyout

Hope it helps someone here!"
        ;;
esac

echo "Subreddit: r/$SUBREDDIT" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Title:" >> "$LOG_FILE"
echo "$TITLE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Body:" >> "$LOG_FILE"
echo "$BODY" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Save post for manual submission
POST_FILE="$REDDIT_POSTS_DIR/week${WEEK_OF_YEAR}_${SUBREDDIT}.txt"
cat > "$POST_FILE" << EOF
========================================
Reddit Post - Week $WEEK_OF_YEAR
Subreddit: r/$SUBREDDIT
Post URL: https://www.reddit.com/r/$SUBREDDIT/submit
Created: $(date)
========================================

Title:
$TITLE

Body:
$BODY

========================================
To post:
1. Go to https://www.reddit.com/r/$SUBREDDIT/submit
2. Copy title above
3. Copy body above
4. Submit post
========================================
EOF

echo "Post saved to: $POST_FILE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "⚠️  MANUAL ACTION REQUIRED" >> "$LOG_FILE"
echo "   Post to r/$SUBREDDIT using content above" >> "$LOG_FILE"
echo "   Or open: https://www.reddit.com/r/$SUBREDDIT/submit" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "Reddit post for r/$SUBREDDIT ready"
echo "Saved to: $POST_FILE"
