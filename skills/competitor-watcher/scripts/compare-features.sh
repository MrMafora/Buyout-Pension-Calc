#!/bin/bash
#
# compare-features.sh - Feature comparison and gap analysis
# Usage: ./compare-features.sh [--update|--gap-analysis]
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
MATRIX_FILE="$REFS_DIR/feature-matrix.csv"
GAP_FILE="$REFS_DIR/feature-gaps.md"

UPDATE_MODE=false
GAP_MODE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --update)
            UPDATE_MODE=true
            ;;
        --gap-analysis)
            GAP_MODE=true
            ;;
    esac
done

# Feature categories to track
FEATURES=(
    "FERS_Calculator"
    "CSRS_Calculator"
    "TSP_Projection"
    "Social_Security_Integration"
    "FEHB_Analysis"
    "FLTCIP_Calculator"
    "Survivor_Benefits"
    "Military_Service_Credit"
    "Deposit_Redeposit"
    "Retirement_Date_Optimization"
    "Tax_Implications"
    "State_Tax_Calculator"
    "PDF_Reports"
    "Mobile_Friendly"
    "API_Access"
    "Consulting_Services"
    "Free_Tier"
)

# Initialize feature matrix if it doesn't exist
init_matrix() {
    if [[ ! -f "$MATRIX_FILE" ]]; then
        # Create header
        header="Competitor"
        for feature in "${FEATURES[@]}"; do
            header="$header,$feature"
        done
        echo "$header" > "$MATRIX_FILE"
        
        # Add FedBuyOut row as reference
        row="FedBuyOut"
        for feature in "${FEATURES[@]}"; do
            row="$row,Yes"
        done
        echo "$row" >> "$MATRIX_FILE"
        
        echo -e "${GREEN}✓ Created feature matrix template${NC}"
    fi
}

# Update matrix with current competitors
update_matrix() {
    echo -e "${YELLOW}Updating feature matrix...${NC}"
    
    # Read current competitors
    local competitors=$(jq -r '.competitors[] | "\(.id)|\(.name)"' "$COMPETITOR_FILE")
    
    # Create new matrix
    local temp_file="$MATRIX_FILE.tmp"
    
    # Write header
    header="Competitor"
    for feature in "${FEATURES[@]}"; do
        header="$header,$feature"
    done
    echo "$header" > "$temp_file"
    
    # Add FedBuyOut
    row="FedBuyOut"
    for feature in "${FEATURES[@]}"; do
        row="$row,Yes"
    done
    echo "$row" >> "$temp_file"
    
    # Add competitors (preserve existing data if available)
    while IFS='|' read -r id name; do
        local existing=$(grep "^$name," "$MATRIX_FILE" 2>/dev/null)
        if [[ -n "$existing" ]]; then
            echo "$existing" >> "$temp_file"
        else
            # New competitor - add empty row
            row="$name"
            for feature in "${FEATURES[@]}"; do
                row="$row,?"
            done
            echo "$row" >> "$temp_file"
        fi
    done <<< "$competitors"
    
    mv "$temp_file" "$MATRIX_FILE"
    echo -e "${GREEN}✓ Feature matrix updated${NC}"
}

# Generate gap analysis report
generate_gap_analysis() {
    echo -e "${YELLOW}Generating gap analysis...${NC}"
    
    if [[ ! -f "$MATRIX_FILE" ]]; then
        echo -e "${RED}Error: Feature matrix not found. Run with --update first.${NC}"
        exit 1
    fi
    
    cat > "$GAP_FILE" << EOF
# Feature Gap Analysis

**Generated:** $(date +%Y-%m-%d)

## Overview

This analysis compares FedBuyOut's feature set against competitors to identify gaps and opportunities.

## Feature Coverage by Competitor

EOF

    # Count features per competitor
    while IFS= read -r line; do
        if [[ "$line" == "Competitor,"* ]]; then
            continue
        fi
        
        local competitor=$(echo "$line" | cut -d',' -f1)
        local yes_count=$(echo "$line" | tr ',' '\n' | grep -c "^Yes$" || echo "0")
        local no_count=$(echo "$line" | tr ',' '\n' | grep -c "^No$" || echo "0")
        local unknown_count=$(echo "$line" | tr ',' '\n' | grep -c "^?$" || echo "0")
        local total=$((yes_count + no_count + unknown_count))
        
        if [[ "$total" -gt 0 ]]; then
            local coverage=$((yes_count * 100 / total))
            echo "- **$competitor**: $yes_count/$total features ($coverage% coverage)" >> "$GAP_FILE"
        fi
    done < "$MATRIX_FILE"
    
    cat >> "$GAP_FILE" << 'EOF'

## FedBuyOut Strengths

Features unique to or exceptionally strong in FedBuyOut:

- [Document strengths based on analysis]

## Competitor Advantages

Features offered by competitors that FedBuyOut may want to consider:

### High Priority Gaps

Features present in multiple competitors:

- [List features found in 3+ competitors that FedBuyOut lacks]

### Nice-to-Have Features

Features present in 1-2 competitors:

- [List potential differentiating features]

## Recommendations

1. **Immediate:** Address high-priority gaps
2. **Short-term:** Evaluate nice-to-have features for roadmap
3. **Long-term:** Monitor emerging features in the market

EOF

    echo -e "${GREEN}✓ Gap analysis saved to: $GAP_FILE${NC}"
}

# Display current matrix
show_matrix() {
    echo "=========================================="
    echo "  Feature Comparison Matrix"
    echo "=========================================="
    echo ""
    
    if [[ ! -f "$MATRIX_FILE" ]]; then
        echo -e "${YELLOW}No feature matrix exists yet${NC}"
        init_matrix
    fi
    
    # Display in a readable format
    column -s',' -t "$MATRIX_FILE" | head -20
    
    echo ""
    echo -e "${BLUE}Matrix location: $MATRIX_FILE${NC}"
    echo ""
    echo "To edit features, modify the CSV file directly."
    echo "Values: Yes, No, ? (unknown)"
}

# Main
echo "=========================================="
echo "  Feature Comparison Tool"
echo "=========================================="
echo ""

if [[ "$UPDATE_MODE" == true ]]; then
    init_matrix
    update_matrix
elif [[ "$GAP_MODE" == true ]]; then
    generate_gap_analysis
else
    show_matrix
fi

echo ""
echo "=========================================="
