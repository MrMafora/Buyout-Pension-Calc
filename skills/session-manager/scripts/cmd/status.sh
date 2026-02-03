#!/bin/bash
#
# Check session/sub-agent status
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
SESSION_ID=""
SHOW_ALL=false
WATCH_MODE=false
WATCH_INTERVAL=5
OUTPUT_FORMAT="table"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --all|-a)
            SHOW_ALL=true
            shift
            ;;
        --watch|-w)
            WATCH_MODE=true
            shift
            ;;
        --interval|-i)
            WATCH_INTERVAL="$2"
            shift 2
            ;;
        --json|-j)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager status [session-id] [options]

Check session or sub-agent status

Options:
    --all, -a           Check all sub-agents
    --watch, -w         Continuous monitoring
    --interval, -i      Watch interval in seconds (default: 5)
    --json, -j          Output as JSON
    --help, -h          Show this help

Examples:
    session-manager status abc123
    session-manager status --all
    session-manager status --watch
    session-manager status --all --watch --interval 10
EOF
            exit 0
            ;;
        -*)
            warn "Unknown option: $1"
            shift
            ;;
        *)
            SESSION_ID="$1"
            shift
            ;;
    esac
done

# Get status for a specific session
get_session_status() {
    local session_id="$1"
    local session_file="$SESSION_DIR/${session_id}.json"
    
    if [[ ! -f "$session_file" ]]; then
        echo '{"error": "Session not found"}'
        return 1
    fi
    
    local info=$(cat "$session_file")
    local age_sec=$(get_session_age "$session_file")
    local pid=$(echo "$info" | jq -r '.pid // "null"')
    local is_running=false
    
    # Check if process is actually running
    if [[ "$pid" != "null" ]] && [[ -n "$pid" ]]; then
        if kill -0 "$pid" 2>/dev/null; then
            is_running=true
        fi
    fi
    
    # Get resource usage if available
    local cpu="-"
    local mem="-"
    if [[ "$is_running" == "true" ]] && [[ "$pid" != "null" ]]; then
        local stats=$(ps -p "$pid" -o %cpu,%mem --no-headers 2>/dev/null || echo "0.0 0.0")
        cpu=$(echo "$stats" | awk '{print $1}')
        mem=$(echo "$stats" | awk '{print $2}')
    fi
    
    echo "$info" | jq --arg age "$age_sec" \
                      --argjson running "$is_running" \
                      --arg cpu "$cpu" \
                      --arg mem "$mem" \
                      '. + {
                          age_seconds: ($age | tonumber),
                          process_running: $running,
                          cpu_percent: $cpu,
                          memory_percent: $mem
                      }'
}

# Display status as table
display_status_table() {
    local status="$1"
    local session_id=$(echo "$status" | jq -r '.session_id // "unknown"')
    local type=$(echo "$status" | jq -r '.type // "unknown"')
    local label=$(echo "$status" | jq -r '.label // "-"')
    local status_text=$(echo "$status" | jq -r '.status // "unknown"')
    local age=$(echo "$status" | jq -r '.age_seconds // 0' | xargs -I{} format_duration {})
    local running=$(echo "$status" | jq -r '.process_running // false')
    local cpu=$(echo "$status" | jq -r '.cpu_percent // "-"')
    local mem=$(echo "$status" | jq -r '.memory_percent // "-"')
    local progress=$(echo "$status" | jq -r '.progress // "-"')
    local parent=$(echo "$status" | jq -r '.parent_session // "-"')
    local task=$(echo "$status" | jq -r '.task // "-"' | cut -c1-50)
    
    echo -e "${CYAN}Session:${NC} $session_id"
    echo -e "${CYAN}Type:${NC} $type"
    echo -e "${CYAN}Label:${NC} $label"
    echo -e "${CYAN}Status:${NC} $status_text $( [[ "$running" == "true" ]] && echo -e "${GREEN}(running)${NC}" || echo -e "${RED}(not running)${NC}" )"
    echo -e "${CYAN}Age:${NC} $age"
    echo -e "${CYAN}Parent:${NC} $parent"
    echo -e "${CYAN}Progress:${NC} $progress"
    echo -e "${CYAN}CPU:${NC} ${cpu}%  ${CYAN}Memory:${NC} ${mem}%"
    echo -e "${CYAN}Task:${NC} $task"
    
    # Show recent log entries if available
    local log_file="$LOG_DIR/${session_id}.log"
    if [[ -f "$log_file" ]]; then
        echo ""
        echo -e "${CYAN}Recent Log Entries:${NC}"
        tail -n 5 "$log_file" | while IFS= read -r line; do
            echo "  $line"
        done
    fi
}

# Display all statuses
display_all_statuses() {
    local sessions=()
    
    for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
        [[ -f "$session_file" ]] || continue
        local session_id=$(basename "$session_file" .json)
        sessions+=("$session_id")
    done
    
    if [[ ${#sessions[@]} -eq 0 ]]; then
        info "No sessions found."
        return
    fi
    
    # Header
    printf "${CYAN}%-24s %-12s %-12s %-10s %-8s %-8s %-12s${NC}\n" \
        "SESSION ID" "TYPE" "STATUS" "RUNNING" "AGE" "CPU" "MEMORY"
    printf "${GRAY}%-24s %-12s %-12s %-10s %-8s %-8s %-12s${NC}\n" \
        "------------------------" "------------" "------------" "----------" "--------" "--------" "------------"
    
    for session_id in "${sessions[@]}"; do
        local status=$(get_session_status "$session_id" 2>/dev/null)
        [[ -z "$status" ]] && continue
        
        local type=$(echo "$status" | jq -r '.type // "unknown"')
        local status_text=$(echo "$status" | jq -r '.status // "unknown"')
        local running=$(echo "$status" | jq -r '.process_running // false')
        local age_sec=$(echo "$status" | jq -r '.age_seconds // 0')
        local age=$(format_duration "$age_sec")
        local cpu=$(echo "$status" | jq -r '.cpu_percent // "-"')
        local mem=$(echo "$status" | jq -r '.memory_percent // "-"')
        
        local running_text="no"
        [[ "$running" == "true" ]] && running_text="${GREEN}yes${NC}"
        
        printf "%-24s %-12s %-12s %-10b %-8s %-8s %-12s\n" \
            "$session_id" "$type" "$status_text" "$running_text" "$age" "${cpu}%" "${mem}%"
    done
}

# Watch mode
watch_mode() {
    while true; do
        clear
        echo -e "${CYAN}=== Session Status Monitor ===${NC}"
        echo -e "${GRAY}Press Ctrl+C to exit${NC}"
        echo ""
        display_all_statuses
        sleep "$WATCH_INTERVAL"
    done
}

# Main
main() {
    if [[ "$WATCH_MODE" == "true" ]]; then
        watch_mode
        return
    fi
    
    if [[ "$SHOW_ALL" == "true" ]]; then
        if [[ "$OUTPUT_FORMAT" == "json" ]]; then
            local json_output="["
            local first=true
            for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
                [[ -f "$session_file" ]] || continue
                local session_id=$(basename "$session_file" .json)
                local status=$(get_session_status "$session_id" 2>/dev/null)
                [[ -z "$status" ]] && continue
                
                if [[ "$first" == "true" ]]; then
                    first=false
                else
                    json_output+=","
                fi
                json_output+=$(echo "$status" | jq --arg id "$session_id" '. + {session_id: $id}')
            done
            json_output+="]"
            echo "$json_output" | jq '.'
        else
            display_all_statuses
        fi
        return
    fi
    
    if [[ -z "$SESSION_ID" ]]; then
        error_exit "Session ID required. Use --all to check all sessions."
    fi
    
    local status=$(get_session_status "$SESSION_ID")
    
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        echo "$status" | jq '.'
    else
        display_status_table "$status"
    fi
}

main
