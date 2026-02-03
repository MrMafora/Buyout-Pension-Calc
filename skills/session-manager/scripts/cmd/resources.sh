#!/bin/bash
#
# Show resource usage for sessions
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
SESSION_ID=""
WATCH_MODE=false
WATCH_INTERVAL=2
OUTPUT_FORMAT="table"
SORT_BY="cpu"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --session|-s)
            SESSION_ID="$2"
            shift 2
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
        --sort)
            SORT_BY="$2"
            shift 2
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager resources [options]

Show resource usage for sessions

Options:
    --session, -s       Show resources for specific session
    --watch, -w         Real-time monitoring (top-like)
    --interval, -i      Update interval in seconds (default: 2)
    --json, -j          Output as JSON
    --sort              Sort by: cpu, mem, age, pid (default: cpu)
    --help, -h          Show this help

Examples:
    session-manager resources
    session-manager resources --session abc123
    session-manager resources --watch
    session-manager top
EOF
            exit 0
            ;;
        *)
            warn "Unknown option: $1"
            shift
            ;;
    esac
done

# Get resource usage for a session
get_session_resources() {
    local session_file="$1"
    local session_id=$(basename "$session_file" .json)
    local info=$(cat "$session_file" 2>/dev/null || echo '{}')
    local pid=$(echo "$info" | jq -r '.pid // "null"')
    local status=$(echo "$info" | jq -r '.status // "unknown"')
    local type=$(echo "$info" | jq -r '.type // "unknown"')
    local label=$(echo "$info" | jq -r '.label // "-"' | cut -c1-20)
    
    local cpu="0.0"
    local mem="0.0"
    local rss="0"
    local vsz="0"
    local threads="0"
    local is_running=false
    
    # Check if process is running and get stats
    if [[ "$pid" != "null" ]] && [[ -n "$pid" ]]; then
        if kill -0 "$pid" 2>/dev/null; then
            is_running=true
            local stats=$(ps -p "$pid" -o %cpu,%mem,rss,vsz,nlwp --no-headers 2>/dev/null)
            if [[ -n "$stats" ]]; then
                cpu=$(echo "$stats" | awk '{print $1}')
                mem=$(echo "$stats" | awk '{print $2}')
                rss=$(echo "$stats" | awk '{print $3}')
                vsz=$(echo "$stats" | awk '{print $4}')
                threads=$(echo "$stats" | awk '{print $5}')
            fi
        fi
    fi
    
    local age_sec=$(get_session_age "$session_file")
    
    echo "$info" | jq --arg id "$session_id" \
                      --argjson pid "${pid:-null}" \
                      --argjson cpu "$cpu" \
                      --argjson mem "$mem" \
                      --argjson rss "${rss:-0}" \
                      --argjson vsz "${vsz:-0}" \
                      --argjson threads "${threads:-0}" \
                      --argjson running "$is_running" \
                      --arg age "$age_sec" \
                      '. + {
                          session_id: $id,
                          pid: $pid,
                          cpu_percent: $cpu,
                          memory_percent: $mem,
                          memory_rss_kb: $rss,
                          memory_vsz_kb: $vsz,
                          threads: $threads,
                          running: $running,
                          age_seconds: ($age | tonumber)
                      }'
}

# Get all sessions with resources
get_all_resources() {
    local resources=()
    
    for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
        [[ -f "$session_file" ]] || continue
        local res=$(get_session_resources "$session_file")
        [[ -n "$res" ]] && resources+=("$res")
    done
    
    printf '%s\n' "${resources[@]}"
}

# Sort resources
sort_resources() {
    case "$SORT_BY" in
        cpu)
            jq -s 'sort_by(.cpu_percent) | reverse | .[]'
            ;;
        mem|memory)
            jq -s 'sort_by(.memory_percent) | reverse | .[]'
            ;;
        age)
            jq -s 'sort_by(.age_seconds) | reverse | .[]'
            ;;
        pid)
            jq -s 'sort_by(.pid // 0) | .[]'
            ;;
        *)
            jq -s 'sort_by(.cpu_percent) | reverse | .[]'
            ;;
    esac
}

# Output as table
output_table() {
    # Header
    printf "${CYAN}%-12s %-8s %-10s %-8s %-10s %-10s %-8s %-20s${NC}\n" \
        "SESSION" "PID" "CPU%" "MEM%" "RSS" "VSZ" "THR" "LABEL"
    printf "${GRAY}%-12s %-8s %-10s %-8s %-10s %-10s %-8s %-20s${NC}\n" \
        "------------" "--------" "----------" "--------" "----------" "----------" "--------" "--------------------"
    
    local total_cpu=0.0
    local total_mem=0.0
    local count=0
    
    while IFS= read -r res; do
        [[ -n "$res" ]] || continue
        
        local sid=$(echo "$res" | jq -r '.session_id // "-"' | cut -c1-12)
        local pid=$(echo "$res" | jq -r '.pid // "-"')
        local cpu=$(echo "$res" | jq -r '.cpu_percent // 0')
        local mem=$(echo "$res" | jq -r '.memory_percent // 0')
        local rss=$(echo "$res" | jq -r '.memory_rss_kb // 0')
        local vsz=$(echo "$res" | jq -r '.memory_vsz_kb // 0')
        local thr=$(echo "$res" | jq -r '.threads // 0')
        local label=$(echo "$res" | jq -r '.label // "-"' | cut -c1-20)
        local running=$(echo "$res" | jq -r '.running // false')
        
        # Format memory sizes
        rss=$(numfmt --to=iec-i --suffix=B "$((rss * 1024))" 2>/dev/null || echo "${rss}K")
        vsz=$(numfmt --to=iec-i --suffix=B "$((vsz * 1024))" 2>/dev/null || echo "${vsz}K")
        
        # Color code high usage
        local cpu_color="$NC"
        local mem_color="$NC"
        
        if (( $(echo "$cpu > 50" | bc -l 2>/dev/null || echo "0") )); then
            cpu_color="$RED"
        elif (( $(echo "$cpu > 20" | bc -l 2>/dev/null || echo "0") )); then
            cpu_color="$YELLOW"
        fi
        
        if (( $(echo "$mem > 10" | bc -l 2>/dev/null || echo "0") )); then
            mem_color="$RED"
        elif (( $(echo "$mem > 5" | bc -l 2>/dev/null || echo "0") )); then
            mem_color="$YELLOW"
        fi
        
        if [[ "$running" == "true" ]]; then
            printf "%-12s %-8s ${cpu_color}%-10s${NC} ${mem_color}%-8s${NC} %-10s %-10s %-8s %-20s\n" \
                "$sid" "$pid" "$cpu" "$mem" "$rss" "$vsz" "$thr" "$label"
            
            total_cpu=$(echo "$total_cpu + $cpu" | bc -l 2>/dev/null || echo "$total_cpu")
            total_mem=$(echo "$total_mem + $mem" | bc -l 2>/dev/null || echo "$total_mem")
            count=$((count + 1))
        fi
    done
    
    # Summary
    echo ""
    printf "${GRAY}Total: %d sessions | CPU: %.1f%% | Memory: %.1f%%${NC}\n" "$count" "$total_cpu" "$total_mem"
}

# Output as JSON
output_json() {
    jq -s '.'
}

# Watch mode (top-like)
watch_mode() {
    while true; do
        clear
        echo -e "${CYAN}=== Session Resource Monitor ===${NC}"
        echo -e "${GRAY}Press Ctrl+C to exit | Sort: $SORT_BY | Update: ${WATCH_INTERVAL}s${NC}"
        echo ""
        
        get_all_resources | sort_resources | output_table
        
        sleep "$WATCH_INTERVAL"
    done
}

# Main
main() {
    if [[ "$WATCH_MODE" == "true" ]]; then
        watch_mode
        return
    fi
    
    if [[ -n "$SESSION_ID" ]]; then
        # Single session mode
        local session_file="$SESSION_DIR/${SESSION_ID}.json"
        if [[ ! -f "$session_file" ]]; then
            error_exit "Session not found: $SESSION_ID"
        fi
        
        local res=$(get_session_resources "$session_file")
        
        if [[ "$OUTPUT_FORMAT" == "json" ]]; then
            echo "$res" | jq '.'
        else
            echo "$res" | jq -r '
                "Session:     \(.session_id)",
                "Type:        \(.type)",
                "Status:      \(.status)",
                "Running:     \(.running)",
                "PID:         \(.pid // "N/A")",
                "CPU:         \(.cpu_percent)%",
                "Memory:      \(.memory_percent)%",
                "RSS:         \(.memory_rss_kb) KB",
                "VSZ:         \(.memory_vsz_kb) KB",
                "Threads:     \(.threads)",
                "Age:         \(.age_seconds) seconds"
            '
        fi
    else
        # All sessions mode
        local resources=$(get_all_resources)
        
        if [[ -z "$resources" ]]; then
            info "No sessions found."
            exit 0
        fi
        
        if [[ "$OUTPUT_FORMAT" == "json" ]]; then
            echo "$resources" | sort_resources | output_json
        else
            echo "$resources" | sort_resources | output_table
        fi
    fi
}

main
