#!/bin/bash
#
# View session history
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
LIMIT=20
SINCE=""
OUTPUT_FORMAT="table"
FILTER_STATUS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --limit|-n)
            LIMIT="$2"
            shift 2
            ;;
        --since)
            SINCE="$2"
            shift 2
            ;;
        --json|-j)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --status|-s)
            FILTER_STATUS="$2"
            shift 2
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager history [options]

View session history

Options:
    --limit, -n         Number of entries to show (default: 20)
    --since             Show sessions since duration (e.g., 1d, 24h)
    --json, -j          Output as JSON
    --status, -s        Filter by status (completed, running, error, etc.)
    --help, -h          Show this help

Examples:
    session-manager history
    session-manager history --limit 50
    session-manager history --since 7d
    session-manager history --status completed
EOF
            exit 0
            ;;
        *)
            warn "Unknown option: $1"
            shift
            ;;
    esac
done

# Calculate since timestamp
get_since_timestamp() {
    if [[ -n "$SINCE" ]]; then
        local seconds=$(parse_duration "$SINCE")
        local now=$(date +%s)
        echo $((now - seconds))
    else
        echo "0"
    fi
}

# Get all sessions sorted by time
get_sessions_sorted() {
    local since_ts=$(get_since_timestamp)
    local sessions=()
    
    for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
        [[ -f "$session_file" ]] || continue
        
        # Check since filter
        if [[ $since_ts -gt 0 ]]; then
            local mtime=$(stat -c %Y "$session_file" 2>/dev/null || stat -f %m "$session_file" 2>/dev/null)
            if [[ $mtime -lt $since_ts ]]; then
                continue
            fi
        fi
        
        # Check status filter
        if [[ -n "$FILTER_STATUS" ]]; then
            local status=$(jq -r '.status // "unknown"' "$session_file" 2>/dev/null)
            if [[ "$status" != "$FILTER_STATUS" ]]; then
                continue
            fi
        fi
        
        sessions+=("$session_file")
    done
    
    # Sort by modification time (newest first)
    printf '%s\n' "${sessions[@]}" | xargs -I{} stat -c '%Y %n' {} 2>/dev/null | sort -rn | cut -d' ' -f2-
}

# Output as table
output_table() {
    local count=0
    
    # Header
    printf "${CYAN}%-20s %-12s %-12s %-10s %-8s %-20s${NC}\n" \
        "STARTED" "SESSION ID" "TYPE" "STATUS" "DURATION" "TASK"
    printf "${GRAY}%-20s %-12s %-12s %-10s %-8s %-20s${NC}\n" \
        "--------------------" "------------" "------------" "----------" "--------" "--------------------"
    
    while IFS= read -r session_file && [[ $count -lt $LIMIT ]]; do
        [[ -f "$session_file" ]] || continue
        
        local session_id=$(basename "$session_file" .json)
        local info=$(cat "$session_file")
        local type=$(echo "$info" | jq -r '.type // "unknown"')
        local status=$(echo "$info" | jq -r '.status // "unknown"')
        local task=$(echo "$info" | jq -r '.task // "-"' | cut -c1-20)
        local created=$(echo "$info" | jq -r '.created_at // ""' | cut -d'T' -f1)
        local age_sec=$(get_session_age "$session_file")
        local duration=$(format_duration "$age_sec")
        
        # Color based on status
        local status_color="$NC"
        case "$status" in
            completed) status_color="$GREEN" ;;
            running|active) status_color="$BLUE" ;;
            error|failed|timeout) status_color="$RED" ;;
            *) status_color="$YELLOW" ;;
        esac
        
        printf "%-20s %-12s %-12s ${status_color}%-10s${NC} %-8s %-20s\n" \
            "$created" "$session_id" "$type" "$status" "$duration" "$task"
        
        count=$((count + 1))
    done
}

# Output as JSON
output_json() {
    local count=0
    local json_array="["
    local first=true
    
    while IFS= read -r session_file && [[ $count -lt $LIMIT ]]; do
        [[ -f "$session_file" ]] || continue
        
        local session_id=$(basename "$session_file" .json)
        local info=$(cat "$session_file")
        local age_sec=$(get_session_age "$session_file")
        
        info=$(echo "$info" | jq --arg id "$session_id" \
                                 --arg age "$age_sec" \
                                 '. + {session_id: $id, age_seconds: ($age | tonumber)}')
        
        if [[ "$first" == "true" ]]; then
            first=false
        else
            json_array+=","
        fi
        json_array+="$info"
        
        count=$((count + 1))
    done
    
    json_array+="]"
    echo "$json_array" | jq '.'
}

# Show statistics
show_stats() {
    local total=0
    local running=0
    local completed=0
    local failed=0
    
    for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
        [[ -f "$session_file" ]] || continue
        total=$((total + 1))
        
        local status=$(jq -r '.status // "unknown"' "$session_file" 2>/dev/null)
        case "$status" in
            running|active) running=$((running + 1)) ;;
            completed) completed=$((completed + 1)) ;;
            error|failed|timeout) failed=$((failed + 1)) ;;
        esac
    done
    
    echo ""
    echo -e "${CYAN}Summary:${NC}"
    echo "  Total sessions:   $total"
    echo -e "  ${BLUE}Running:${NC}          $running"
    echo -e "  ${GREEN}Completed:${NC}        $completed"
    echo -e "  ${RED}Failed:${NC}           $failed"
}

# Main
main() {
    local sessions=$(get_sessions_sorted)
    
    if [[ -z "$sessions" ]]; then
        info "No sessions found."
        exit 0
    fi
    
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo "$sessions" | output_json
    else
        echo "$sessions" | output_table
        show_stats
    fi
}

main
