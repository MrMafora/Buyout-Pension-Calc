#!/bin/bash
#
# Show detailed session information
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
SESSION_ID=""
OUTPUT_FORMAT="text"
SHOW_LOGS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --json|-j)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --logs|-l)
            SHOW_LOGS=true
            shift
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager info <session-id> [options]

Show detailed information about a session

Options:
    --json, -j          Output as JSON
    --logs, -l          Include recent log entries
    --help, -h          Show this help

Examples:
    session-manager info abc123
    session-manager info abc123 --logs
    session-manager info abc123 --json
EOF
            exit 0
            ;;
        -*)
            warn "Unknown option: $1"
            shift
            ;;
        *)
            if [[ -z "$SESSION_ID" ]]; then
                SESSION_ID="$1"
            fi
            shift
            ;;
    esac
done

# Validate
if [[ -z "$SESSION_ID" ]]; then
    error_exit "Session ID required"
fi

# Get detailed info
get_session_details() {
    local session_id="$1"
    local session_file="$SESSION_DIR/${session_id}.json"
    local log_file="$LOG_DIR/${session_id}.log"
    
    if [[ ! -f "$session_file" ]]; then
        error_exit "Session not found: $session_id"
    fi
    
    local info=$(cat "$session_file")
    local age_sec=$(get_session_age "$session_file")
    local pid=$(echo "$info" | jq -r '.pid // "null"')
    local is_running=false
    
    # Check if process is running
    if [[ "$pid" != "null" ]] && [[ -n "$pid" ]]; then
        if kill -0 "$pid" 2>/dev/null; then
            is_running=true
        fi
    fi
    
    # Get resource usage
    local cpu="-"
    local mem="-"
    local rss="-"
    local threads="-"
    if [[ "$is_running" == "true" ]]; then
        local stats=$(ps -p "$pid" -o %cpu,%mem,rss,nlwp --no-headers 2>/dev/null)
        if [[ -n "$stats" ]]; then
            cpu=$(echo "$stats" | awk '{print $1}')
            mem=$(echo "$stats" | awk '{print $2}')
            rss=$(echo "$stats" | awk '{print $3}')
            threads=$(echo "$stats" | awk '{print $4}')
        fi
    fi
    
    # Get log stats
    local log_size=0
    local log_lines=0
    if [[ -f "$log_file" ]]; then
        log_size=$(stat -c %s "$log_file" 2>/dev/null || stat -f %z "$log_file" 2>/dev/null)
        log_lines=$(wc -l < "$log_file" 2>/dev/null || echo "0")
    fi
    
    # Build full details
    echo "$info" | jq --arg age "$age_sec" \
                      --argjson running "$is_running" \
                      --arg cpu "$cpu" \
                      --arg mem "$mem" \
                      --arg rss "$rss" \
                      --arg threads "$threads" \
                      --arg log_size "$log_size" \
                      --arg log_lines "$log_lines" \
                      '. + {
                          age_seconds: ($age | tonumber),
                          process_running: $running,
                          cpu_percent: $cpu,
                          memory_percent: $mem,
                          memory_rss_kb: $rss,
                          threads: $threads,
                          log_size_bytes: ($log_size | tonumber),
                          log_lines: ($log_lines | tonumber)
                      }'
}

# Display as text
display_text() {
    local details="$1"
    local session_id=$(echo "$details" | jq -r '.session_id // "unknown"')
    local log_file="$LOG_DIR/${session_id}.log"
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  Session: $session_id"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Basic Info
    echo -e "${CYAN}Basic Information:${NC}"
    echo "  Type:         $(echo "$details" | jq -r '.type // "unknown"')"
    echo "  Label:        $(echo "$details" | jq -r '.label // "-"')"
    echo "  Status:       $(echo "$details" | jq -r '.status // "unknown"')"
    echo "  Progress:     $(echo "$details" | jq -r '.progress // "-"')"
    echo "  Priority:     $(echo "$details" | jq -r '.priority // "normal"')"
    echo ""
    
    # Timing
    echo -e "${CYAN}Timing:${NC}"
    echo "  Created:      $(echo "$details" | jq -r '.created_at // "-"')"
    echo "  Age:          $(format_duration $(echo "$details" | jq -r '.age_seconds // 0'))"
    echo "  Timeout:      $(echo "$details" | jq -r '.timeout // 0') seconds"
    echo ""
    
    # Process
    echo -e "${CYAN}Process:${NC}"
    echo "  PID:          $(echo "$details" | jq -r '.pid // "N/A"')"
    echo "  Running:      $(echo "$details" | jq -r '.process_running // false')"
    echo "  CPU:          $(echo "$details" | jq -r '.cpu_percent // "-"')%"
    echo "  Memory:       $(echo "$details" | jq -r '.memory_percent // "-"')%"
    echo "  RSS:          $(echo "$details" | jq -r '.memory_rss_kb // "-"') KB"
    echo "  Threads:      $(echo "$details" | jq -r '.threads // "-"')"
    echo ""
    
    # Relationships
    echo -e "${CYAN}Relationships:${NC}"
    echo "  Parent:       $(echo "$details" | jq -r '.parent_session // "-"')"
    echo ""
    
    # Task
    echo -e "${CYAN}Task:${NC}"
    echo "  $(echo "$details" | jq -r '.task // "-"')"
    echo ""
    
    # Working Directory
    echo -e "${CYAN}Working Directory:${NC}"
    echo "  $(echo "$details" | jq -r '.working_directory // "-"')"
    echo ""
    
    # Environment
    echo -e "${CYAN}Environment Variables:${NC}"
    echo "$details" | jq -r '.environment | to_entries[] | "  \(.key)=\(.value)"' 2>/dev/null || echo "  (none)"
    echo ""
    
    # Logs
    echo -e "${CYAN}Logs:${NC}"
    echo "  File:         $log_file"
    echo "  Size:         $(echo "$details" | jq -r '.log_size_bytes // 0') bytes"
    echo "  Lines:        $(echo "$details" | jq -r '.log_lines // 0')"
    
    # Show log entries if requested
    if [[ "$SHOW_LOGS" == "true" ]] && [[ -f "$log_file" ]]; then
        echo ""
        echo -e "${CYAN}Recent Log Entries (last 20 lines):${NC}"
        echo -e "${GRAY}────────────────────────────────────────────────────────${NC}"
        tail -n 20 "$log_file" | while IFS= read -r line; do
            echo "  $line"
        done
        echo -e "${GRAY}────────────────────────────────────────────────────────${NC}"
    fi
    
    # Files
    echo ""
    echo -e "${CYAN}Files:${NC}"
    echo "  Session:      $SESSION_DIR/${session_id}.json"
    echo "  Log:          $log_file"
}

# Main
main() {
    local details=$(get_session_details "$SESSION_ID")
    
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo "$details" | jq '.'
    else
        display_text "$details"
    fi
}

main
