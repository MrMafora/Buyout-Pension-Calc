#!/bin/bash
# Daily Twitter posting script for FedBuyOut
# Rotates through 10 pre-written tweets
# Logs tweets for manual posting until bird CLI is configured

TWEETS=(
    "Built a free calculator for federal employees considering buyout offers. Compares FERS/CSRS pension vs buyout with tax implications. Check it out: https://fedbuyout.com #FederalEmployee #FERS #Retirement"
    
    "TSP funds had positive returns! 📈 If you're considering a buyout, your retirement savings trajectory matters. Calculate your break-even: https://fedbuyout.com #TSP #FederalEmployee"
    
    "PSA for feds: Don't take a buyout without running the numbers first. Free tool does the math for you - pension vs buyout, tax implications, break-even analysis: https://fedbuyout.com"
    
    "FERS vs CSRS buyout math is complicated. High-3, multipliers, early retirement penalties... Our free calculator handles it all: https://fedbuyout.com #FERS #CSRS #FederalRetirement"
    
    "Considering a federal buyout? That $25,000 is actually closer to $16,000 after taxes. Calculate your real after-tax buyout: https://fedbuyout.com #BuyoutTaxes #FederalEmployee"
    
    "New on the blog: Should I Take the Federal Buyout? Complete decision guide with real examples and break-even analysis. Read it: https://fedbuyout.com/blog #FederalRetirement"
    
    "Military buyback can add thousands to your federal pension. Our calculator includes military service years in the calculation. Try it: https://fedbuyout.com #MilitaryBuyback #FERS"
    
    "Early retirement penalties are 5% per year under age 62. That adds up fast. See how much it costs you: https://fedbuyout.com #EarlyRetirement #FERS"
    
    "Survivor benefits cost 10% of your pension but protect your spouse. Calculate the cost vs benefit: https://fedbuyout.com #SurvivorBenefits #FederalRetirement"
    
    "Free federal buyout calculator updated for 2026 OPM rates. FERS, CSRS, tax implications, state taxes, early retirement penalties - all in one tool: https://fedbuyout.com"
)

# Get day of year to rotate through tweets (0-9)
DAY_OF_YEAR=$(date +%j)
INDEX=$((DAY_OF_YEAR % 10))
SELECTED_TWEET="${TWEETS[$INDEX]}"

LOG_DIR="/root/.openclaw/workspace/fedbuyout/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/twitter-posts.log"
QUEUE_FILE="$LOG_DIR/twitter-queue.txt"

echo "========================================" >> "$LOG_FILE"
echo "Twitter Post - $(date)" >> "$LOG_FILE"
echo "Day $DAY_OF_YEAR, Tweet #$INDEX" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "$SELECTED_TWEET" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Save to queue for manual posting
echo "$(date '+%Y-%m-%d %H:%M') - Tweet #$INDEX" >> "$QUEUE_FILE"
echo "$SELECTED_TWEET" >> "$QUEUE_FILE"
echo "" >> "$QUEUE_FILE"

# Try bird CLI if available
if command -v bird &> /dev/null; then
    echo "Attempting to post via bird CLI..." >> "$LOG_FILE"
    if bird tweet "$SELECTED_TWEET" 2>&1 >> "$LOG_FILE"; then
        echo "✅ Successfully posted via bird CLI" >> "$LOG_FILE"
    else
        echo "⚠️  Bird CLI failed - tweet queued for manual posting" >> "$LOG_FILE"
        echo "   To post manually: Copy tweet from $QUEUE_FILE" >> "$LOG_FILE"
    fi
else
    echo "ℹ️  Bird CLI not installed - tweet logged for manual posting" >> "$LOG_FILE"
    echo "   To post: Go to https://twitter.com/compose/tweet" >> "$LOG_FILE"
    echo "   Tweet saved in: $QUEUE_FILE" >> "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "Tweet #$INDEX ready for posting"
