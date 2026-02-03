#!/bin/bash
#
# Monitor long-running tasks
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
ALERT_THRESHOLD=3600  # 1 hour in seconds
CHECK_INTERVAL=30
WATCH_MODE=true
NOTIFY_CMD=""
OUTPUT_FORMAT="table"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --alert|-a)
            ALERT_THRESHOLD=$(parse_duration "$2")
            shift 2
            ;;
        --interval|-i)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        --notify|-n)
            NOTIFY_CMD="$2"
            shift 2
            ;;
        --once)
            WATCH_MODE=false
            shift
            ;;
        --json|-j)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager watch [options]

Monitor long-running tasks and alert on extended execution

Options:
    --alert, -a         Alert threshold duration (default: 1h)
    --interval, -i      Check interval in seconds (default: 30)
    --notify, -n        Command to run for notifications
    --once              Run check once and exit
    --json, -j          Output as JSON
    --help, -h          Show this help

Examples:
    session-manager watch
    session-manager watch --alert 30m
    session-manager watch --notify "notify-send 'Long Task'"
    session-manager watch --once --json
EOF
            exit 0
            ;;
        *)
            warn "Unknown option: $1"
            shift
            ;;
    esac
done

# Get long-running sessions
get_long_running() {
    local threshold="$1"
    local long_running=()
    
    for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
        [[ -f "$session_file" ]] || continue
        
        local age_sec=$(get_session_age "$session_file")
        if [[ $age_sec -gt $threshold ]]; then
            local info=$(cat "$session_file")
            local status=$(echo "$info" | jq -r '.status // "unknown"')
            local pid=$(echo "$info" | jq -r '.pid // "null"')
            
            # Only include running processes
            if [[ "$status" == "running" ]] || [[ "$status" == "active" ]]; then
                if [[ "$pid" != "null" ]] && kill -0 "$pid" 2>/dev/null; then
                    local session_id=$(basename "$session_file" .json)
                    long_running+=("$session_id:$age_sec")
                fi
            fi
        fi
    done
    
    printf '%s\n' "${long_running[@]}"
}

# Send notification
send_notification() {
    local message="$1"
    
    if [[ -n "$NOTIFY_CMD" ]]; then
        eval "$NOTIFY_CMD '$message'"
    else
        # Try common notification methods
        if command -v notify-send &>/dev/null; then
            notify-send "Session Manager" "$message"
        elif command -v osascript &>/dev/null; then
            osascript -e "display notification \"$message\" with title \"Session Manager\""
        fi
    fi
    
    log "ALERT" "$message"
}

# Output as table
output_table() {
    local sessions=("$@")
    
    if [[ ${#sessions[@]} -eq 0 ]] || [[ -z "${sessions[0]}" ]]; then
        return
    fi
    
    echo -e "${YELLOW}⚠ Long-running sessions detected:${NC}"
    printf "${CYAN}%-24s %-12s %-15s %-20s${NC}\n" \
        "SESSION ID" "STATUS" "DURATION" "TASK"
    
    for entry in "${sessions[@]}"; do
        [[ -n "$entry" ]] || continue
        
        local session_id=$(echo "$entry" | cut -d: -f1)
        local age_sec=$(echo "$entry" | cut -d: -f2)
        local duration=$(format_duration "$age_sec")
        
        local session_file="$SESSION_DIR/${session_id}.json"
        local info=$(cat "$session_file" 2>/dev/null || echo '{}')
        local status=$(echo "$info" | jq -r '.status // "unknown"')
        local task=$(echo "$info" | jq -r '.task // "-"' | cut -c1-20)
        
        printf "%-24s %-12s %-15s %-20s\n" \
            "$session_id" "$status" "$duration" "$task"
    done
}

# Output as JSON
output_json() {
    local sessions=("$@")
    local json_array="["
    local first=true
    
    for entry in "${sessions[@]}"; do
        [[ -n "$entry" ]] || continue
        
        local session_id=$(echo "$entry" | cut -d: -f1)
        local age_sec=$(echo "$entry" | cut -d: -f2)
        local session_file="$SESSION_DIR/${session_id}.json"
        
        if [[ -f "$session_file" ]]; then
            local info=$(cat "$session_file")
            info=$(echo "$info" | jq --arg id "$session_id" \
                                     --arg age "$age_sec" \
                                     '. + {session_id: $id, age_seconds: ($age | tonumber)}')
            
            if [[ "$first" == "true" ]]; then
                first=false
            else
                json_array+=","
            fi
            json_array+="$info"
        fi
    done
    
    json_array+="]"
    echo "$json_array" | jq '.'
}

# Check and report
check_and_report() {
    local long_running=($(get_long_running "$ALERT_THRESHOLD"))
    
    if [[ ${#long_running[@]} -eq 0 ]] || [[ -z "${long_running[0]}" ]]; then
        if [[ "$OUTPUT_FORMAT" != "json" ]]; then
            success "No long-running sessions detected (threshold: $(format_duration $ALERT_THRESHOLD))"
        else
            echo '[]'
        fi
        return 0
    fi
    
    # Alert if new long-running sessions detected
    for entry in "${long_running[@]}"; do
        [[ -n "$entry" ]] || continue
        local session_id=$(echo "$entry" | cut -d: -f1)
        local age_sec=$(echo "$entry" | cut -d: -f2)
        local duration=$(format_duration "$age_sec")
        
        send_notification "Session $session_id has been running for $duration"
    done
    
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        output_json "${long_running[@]}"
    else
        output_table "${long_running[@]}"
    fi
    
    return 1  # Return error code to indicate alerts were triggered
}

# Watch mode
watch_mode_func() {
    while true; do
        clear
        echo -e "${CYAN}=== Long-Running Task Monitor ===${NC}"
        echo -e "${GRAY}Alert threshold: $(format_duration $ALERT_THRESHOLD) | Check interval: ${CHECK_INTERVAL}s${NC}"
        echo -e "${GRAY}Press Ctrl+C to exit${NC}"
        echo ""
        
        check_and_report
        
        sleep "$CHECK_INTERVAL"
    done
}

# Main
main() {
    if [[ "$WATCH_MODE" == "true" ]]; then
        watch_mode_func
    else
        check_and_report
    fi
}

main
