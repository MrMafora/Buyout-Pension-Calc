#!/bin/bash
#
# discover.sh - Discover new competitors
# Usage: ./discover.sh [--review|--add]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REFS_DIR="$SKILL_DIR/references"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COMPETITOR_FILE="$REFS_DIR/competitor-list.json"
CANDIDATES_FILE="$REFS_DIR/candidates.json"
REVIEW_MODE=false
ADD_MODE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --review)
            REVIEW_MODE=true
            ;;
        --add)
            ADD_MODE=true
            ;;
    esac
done

# Ensure candidates file exists
if [[ ! -f "$CANDIDATES_FILE" ]]; then
    echo '{"candidates": []}' > "$CANDIDATES_FILE"
fi

# Search queries for competitor discovery
SEARCH_QUERIES=(
    "federal retirement calculator"
    "FERS retirement calculator"
    "CSRS retirement calculator"
    "federal employee benefits calculator"
    "fedcalc alternative"
    "federal pension calculator"
    "TSP calculator federal employee"
    "federal retirement planning software"
)

# Function to search and find candidates
search_candidates() {
    echo -e "${YELLOW}Searching for new competitors...${NC}"
    echo ""
    
    # This is a simulated search - in production, you'd use web search API
    # For now, we'll check against known patterns and user suggestions
    
    echo "Search queries that would be executed:"
    for query in "${SEARCH_QUERIES[@]}"; do
        echo "  - $query"
    done
    
    echo ""
    echo -e "${BLUE}To add a new competitor manually, use:${NC}"
    echo "  ./discover.sh --add"
    echo ""
    echo -e "${YELLOW}Note: Automated web search requires API integration${NC}"
}

# Function to review candidates
review_candidates() {
    local candidates=$(jq -r '.candidates[] | "\(.id)|\(.name)|\(.url)|\(.source)"' "$CANDIDATES_FILE" 2>/dev/null)
    
    if [[ -z "$candidates" ]]; then
        echo -e "${YELLOW}No candidates to review${NC}"
        return
    fi
    
    echo "=========================================="
    echo "  Candidate Review"
    echo "=========================================="
    
    while IFS='|' read -r id name url source; do
        echo ""
        echo "ID:     $id"
        echo "Name:   $name"
        echo "URL:    $url"
        echo "Source: $source"
        echo ""
        echo -n "Approve this candidate? (y/n/skip): "
        
        # In automated mode, we'd have different logic
        # For now, just display
        echo "[Manual approval required - edit $COMPETITOR_FILE to add]"
    done <<< "$candidates"
}

# Function to add new competitor interactively
add_competitor() {
    echo "=========================================="
    echo "  Add New Competitor"
    echo "=========================================="
    
    read -p "Competitor ID (lowercase, no spaces): " id
    read -p "Competitor Name: " name
    read -p "Website URL: " url
    read -p "Priority (high/medium/low): " priority
    read -p "Category (calculator/advisor/tool/resource): " category
    read -p "Track pricing? (true/false): " track_pricing
    read -p "Pricing URL (optional): " pricing_url
    
    # Validate inputs
    if [[ -z "$id" || -z "$name" || -z "$url" ]]; then
        echo -e "${RED}Error: ID, Name, and URL are required${NC}"
        exit 1
    fi
    
    # Check if ID already exists
    local exists=$(jq -r ".competitors[] | select(.id == \"$id\") | .id" "$COMPETITOR_FILE")
    if [[ -n "$exists" ]]; then
        echo -e "${RED}Error: Competitor with ID '$id' already exists${NC}"
        exit 1
    fi
    
    # Build competitor entry
    local new_entry=$(jq -n \
        --arg id "$id" \
        --arg name "$name" \
        --arg url "$url" \
        --arg priority "${priority:-medium}" \
        --arg category "${category:-tool}" \
        --argjson track_pricing "${track_pricing:-false}" \
        --arg pricing_url "$pricing_url" \
        '{
            id: $id,
            name: $name,
            url: $url,
            priority: $priority,
            category: $category,
            track_pricing: $track_pricing,
            pricing_url: (if $pricing_url == "" then null else $pricing_url end),
            date_added: now | todate,
            notes: ""
        }')
    
    # Add to competitor list
    jq --argjson entry "$new_entry" '.competitors += [$entry]' "$COMPETITOR_FILE" > "$COMPETITOR_FILE.tmp" && \
        mv "$COMPETITOR_FILE.tmp" "$COMPETITOR_FILE"
    
    echo -e "${GREEN}✓ Added competitor: $name${NC}"
    
    # Take initial snapshot
    echo "Taking initial snapshot..."
    "$SCRIPT_DIR/monitor.sh" "$id"
}

# Function to list all current competitors
list_competitors() {
    echo "=========================================="
    echo "  Current Competitors"
    echo "=========================================="
    echo ""
    
    jq -r '.competitors[] | "[\(.priority)] \(.name) (\(.id)) - \(.url)"' "$COMPETITOR_FILE" | \
        sort | \
        while read line; do
            if [[ "$line" == *"[high]"* ]]; then
                echo -e "${RED}$line${NC}"
            elif [[ "$line" == *"[medium]"* ]]; then
                echo -e "${YELLOW}$line${NC}"
            else
                echo "$line"
            fi
        done
    
    local count=$(jq '.competitors | length' "$COMPETITOR_FILE")
    echo ""
    echo "Total competitors: $count"
}

# Main
echo "=========================================="
echo "  Competitor Discovery"
echo "=========================================="
echo ""

if [[ "$REVIEW_MODE" == true ]]; then
    review_candidates
elif [[ "$ADD_MODE" == true ]]; then
    add_competitor
else
    list_competitors
    echo ""
    search_candidates
fi

echo ""
echo "=========================================="
