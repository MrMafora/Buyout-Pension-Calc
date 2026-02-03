#!/bin/bash
#
# generate-report.sh - Generate competitive analysis reports
# Usage: ./generate-report.sh [q1|q2|q3|q4|annual]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REFS_DIR="$SKILL_DIR/references"
REPORTS_DIR="$SKILL_DIR/reports"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COMPETITOR_FILE="$REFS_DIR/competitor-list.json"
PRICING_FILE="$REFS_DIR/pricing-history.json"
SNAPSHOTS_DIR="$REFS_DIR/tracking-snapshots"

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Parse arguments
REPORT_TYPE="${1:-quarterly}"
YEAR=$(date +%Y)

# Determine quarter if not specified
if [[ "$REPORT_TYPE" == "quarterly" ]]; then
    MONTH=$(date +%m)
    case $MONTH in
        01|02|03) REPORT_TYPE="q1" ;;
        04|05|06) REPORT_TYPE="q2" ;;
        07|08|09) REPORT_TYPE="q3" ;;
        10|11|12) REPORT_TYPE="q4" ;;
    esac
fi

# Function to generate executive summary
generate_summary() {
    local report_file="$1"
    
    local total_competitors=$(jq '.competitors | length' "$COMPETITOR_FILE")
    local high_priority=$(jq '[.competitors[] | select(.priority == "high")] | length' "$COMPETITOR_FILE")
    local changes_count=$(wc -l < "$SNAPSHOTS_DIR/changes.log" 2>/dev/null || echo "0")
    
    cat >> "$report_file" << EOF
## Executive Summary

| Metric | Value |
|--------|-------|
| Total Competitors Tracked | $total_competitors |
| High Priority Competitors | $high_priority |
| Changes Detected This Period | $changes_count |
| Report Generated | $(date +%Y-%m-%d) |

### Key Findings

EOF

    # Add recent changes summary
    if [[ -f "$SNAPSHOTS_DIR/changes.log" && -s "$SNAPSHOTS_DIR/changes.log" ]]; then
        echo "**Recent Activity:**" >> "$report_file"
        echo "" >> "$report_file"
        tail -10 "$SNAPSHOTS_DIR/changes.log" | while read line; do
            echo "- $line" >> "$report_file"
        done
        echo "" >> "$report_file"
    else
        echo "No significant changes detected in this period." >> "$report_file"
        echo "" >> "$report_file"
    fi
}

# Function to list competitors by category
list_by_category() {
    local report_file="$1"
    
    echo "## Competitors by Category" >> "$report_file"
    echo "" >> "$report_file"
    
    local categories=("calculator" "advisor" "tool" "resource")
    
    for category in "${categories[@]}"; do
        local count=$(jq "[.competitors[] | select(.category == \"$category\")] | length" "$COMPETITOR_FILE")
        if [[ "$count" -gt 0 ]]; then
            echo "### ${category^}s ($count)" >> "$report_file"
            echo "" >> "$report_file"
            jq -r ".competitors[] | select(.category == \"$category\") | \"- **\(.name)** (\(.priority) priority) - [\(.url)](\(.url))\"" "$COMPETITOR_FILE" >> "$report_file"
            echo "" >> "$report_file"
        fi
    done
}

# Function to analyze pricing trends
analyze_pricing() {
    local report_file="$1"
    
    echo "## Pricing Analysis" >> "$report_file"
    echo "" >> "$report_file"
    
    if [[ ! -f "$PRICING_FILE" || ! -s "$PRICING_FILE" ]]; then
        echo "*No pricing data available for analysis.*" >> "$report_file"
        echo "" >> "$report_file"
        return
    fi
    
    echo "| Competitor | Current Pricing | Last Updated |" >> "$report_file"
    echo "|------------|-----------------|--------------|" >> "$report_file"
    
    jq -r 'to_entries[] | select(.value.history | length > 0) | 
           "| \(.key) | \(.value.history[-1].prices | join(", ")) | \(.value.history[-1].timestamp[:10]) |"' "$PRICING_FILE" >> "$report_file"
    
    echo "" >> "$report_file"
}

# Function to list new competitors
list_new_competitors() {
    local report_file="$1"
    local period_start=""
    
    case $REPORT_TYPE in
        q1) period_start="${YEAR}-01-01" ;;
        q2) period_start="${YEAR}-04-01" ;;
        q3) period_start="${YEAR}-07-01" ;;
        q4) period_start="${YEAR}-10-01" ;;
        annual) period_start="${YEAR}-01-01" ;;
    esac
    
    echo "## New Competitors This Period" >> "$report_file"
    echo "" >> "$report_file"
    
    local new_count=$(jq "[.competitors[] | select(.date_added >= \"$period_start\")] | length" "$COMPETITOR_FILE")
    
    if [[ "$new_count" -gt 0 ]]; then
        jq -r ".competitors[] | select(.date_added >= \"$period_start\") | \"- **\(.name)** - Added \(.date_added[:10])\"" "$COMPETITOR_FILE" >> "$report_file"
    else
        echo "*No new competitors added this period.*" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
}

# Function to generate recommendations
generate_recommendations() {
    local report_file="$1"
    
    echo "## Recommendations" >> "$report_file"
    echo "" >> "$report_file"
    
    cat >> "$report_file" << 'EOF'
1. **Monitor high-priority competitors closely** - Weekly checks recommended for direct competitors
2. **Review pricing monthly** - Track any pricing changes in the market
3. **Update feature matrix quarterly** - Ensure competitive positioning is accurate
4. **Watch for new entrants** - Federal retirement space may see new tools

### Action Items

- [ ] Review all high-priority competitor websites for recent changes
- [ ] Update FedBuyOut pricing strategy based on competitive landscape
- [ ] Identify feature gaps vs. top 3 competitors
- [ ] Schedule next competitive review

EOF
}

# Function to generate feature comparison
generate_feature_comparison() {
    local report_file="$1"
    
    echo "## Feature Comparison Matrix" >> "$report_file"
    echo "" >> "$report_file"
    
    # Reference the feature matrix file
    local matrix_file="$REFS_DIR/feature-matrix.csv"
    
    if [[ -f "$matrix_file" ]]; then
        echo "See detailed feature matrix: [feature-matrix.csv](../references/feature-matrix.csv)" >> "$report_file"
        echo "" >> "$report_file"
        
        # Add summary
        echo "### Key Features Tracked" >> "$report_file"
        echo "" >> "$report_file"
        head -1 "$matrix_file" | tr ',' '\n' | tail -n +2 | sed 's/^/- /' >> "$report_file"
    else
        echo "*Feature matrix not yet created. Run compare-features.sh to generate.*" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
}

# Main report generation
echo "=========================================="
echo "  Generating $REPORT_TYPE Report"
echo "=========================================="

# Determine output filename
REPORT_FILE="$REPORTS_DIR/competitive-analysis-${REPORT_TYPE}-${YEAR}.md"

# Generate report header
cat > "$REPORT_FILE" << EOF
# Competitive Analysis Report

**Report Period:** ${REPORT_TYPE^^} ${YEAR}  
**Generated:** $(date +%Y-%m-%d)  
**For:** FedBuyOut

---

EOF

# Generate sections
generate_summary "$REPORT_FILE"
list_new_competitors "$REPORT_FILE"
list_by_category "$REPORT_FILE"
analyze_pricing "$REPORT_FILE"
generate_feature_comparison "$REPORT_FILE"
generate_recommendations "$REPORT_FILE"

# Add appendix
cat >> "$REPORT_FILE" << EOF

---

## Appendix

### Tracked Competitors

Full list available in [competitor-list.json](../references/competitor-list.json)

### Change History

Full change log available in tracking snapshots directory.

### Methodology

- Website monitoring: Checksums compared every run
- Pricing tracking: Direct page scraping with pattern matching
- Feature comparison: Manual analysis with structured data
- New discovery: Web search + manual curation

EOF

echo ""
echo -e "${GREEN}✓ Report generated: $REPORT_FILE${NC}"
echo ""
echo "To view the report:"
echo "  cat $REPORT_FILE"
echo ""
echo "=========================================="
