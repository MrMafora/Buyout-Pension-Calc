#!/bin/bash
#
# List active sessions
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
OUTPUT_FORMAT="table"
FILTER_TYPE=""
SHOW_ALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --json|-j)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --subagents|--subagent|-s)
            FILTER_TYPE="subagent"
            shift
            ;;
        --main|-m)
            FILTER_TYPE="main"
            shift
            ;;
        --all|-a)
            SHOW_ALL=true
            shift
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager list [options]

List active OpenClaw sessions

Options:
    --json, -j          Output as JSON
    --subagents, -s     Show only sub-agents
    --main, -m          Show only main sessions
    --all, -a           Include completed sessions
    --help, -h          Show this help

Examples:
    session-manager list
    session-manager list --json
    session-manager list --subagents
EOF
            exit 0
            ;;
        *)
            warn "Unknown option: $1"
            shift
            ;;
    esac
done

# Get sessions from process tool or session directory
get_sessions() {
    local sessions=()
    
    # Try to get from OpenClaw process list
    if command -v openclaw &>/dev/null; then
        while IFS= read -r line; do
            sessions+=("$line")
        done < <(openclaw process list --json 2>/dev/null | jq -r '.[] | @base64' 2>/dev/null)
    fi
    
    # Also check session directory
    if [[ -d "$SESSION_DIR" ]]; then
        for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
            [[ -f "$session_file" ]] || continue
            local session_id=$(basename "$session_file" .json)
            if [[ ! " ${sessions[*]} " =~ " ${session_id} " ]]; then
                sessions+=("$session_id")
            fi
        done
    fi
    
    echo "${sessions[@]}"
}

# Get session info from file
get_session_info() {
    local session_id="$1"
    local session_file="$SESSION_DIR/${session_id}.json"
    
    if [[ -f "$session_file" ]]; then
        cat "$session_file"
    else
        echo '{}'
    fi
}

# Output as table
output_table() {
    local sessions=("$@")
    
    if [[ ${#sessions[@]} -eq 0 ]]; then
        info "No active sessions found."
        return
    fi
    
    # Header
    printf "${CYAN}%-24s %-12s %-10s %-8s %-20s${NC}\n" \
        "SESSION ID" "TYPE" "STATUS" "AGE" "LABEL"
    printf "${GRAY}%-24s %-12s %-10s %-8s %-20s${NC}\n" \
        "------------------------" "------------" "----------" "--------" "--------------------"
    
    for session_id in "${sessions[@]}"; do
        local info=$(get_session_info "$session_id")
        local type=$(echo "$info" | jq -r '.type // "unknown"')
        local status=$(echo "$info" | jq -r '.status // "unknown"')
        local label=$(echo "$info" | jq -r '.label // "-"' | cut -c1-20)
        local age="-"
        
        local session_file="$SESSION_DIR/${session_id}.json"
        if [[ -f "$session_file" ]]; then
            local age_sec=$(get_session_age "$session_file")
            age=$(format_duration "$age_sec")
        fi
        
        # Filter by type if specified
        if [[ -n "$FILTER_TYPE" ]] && [[ "$type" != "$FILTER_TYPE" ]]; then
            continue
        fi
        
        # Color based on status
        local status_color="$NC"
        case "$status" in
            running|active) status_color="$GREEN" ;;
            completed|done) status_color="$BLUE" ;;
            error|failed) status_color="$RED" ;;
            *) status_color="$YELLOW" ;;
        esac
        
        printf "%-24s %-12s ${status_color}%-10s${NC} %-8s %-20s\n" \
            "$session_id" "$type" "$status" "$age" "$label"
    done
}

# Output as JSON
output_json() {
    local sessions=("$@")
    local json_array="["
    local first=true
    
    for session_id in "${sessions[@]}"; do
        local info=$(get_session_info "$session_id")
        local session_file="$SESSION_DIR/${session_id}.json"
        
        if [[ -f "$session_file" ]]; then
            local age_sec=$(get_session_age "$session_file")
            info=$(echo "$info" | jq --arg age "$age_sec" '. + {age_seconds: ($age | tonumber)}')
        fi
        
        if [[ "$first" == "true" ]]; then
            first=false
        else
            json_array+=","
        fi
        json_array+=$(echo "$info" | jq --arg id "$session_id" '. + {session_id: $id}')
    done
    
    json_array+="]"
    echo "$json_array" | jq '.'
}

# Main
main() {
    local sessions=()
    
    # Collect all session files
    if [[ -d "$SESSION_DIR" ]]; then
        for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
            [[ -f "$session_file" ]] || continue
            local session_id=$(basename "$session_file" .json)
            
            # Skip completed unless --all
            if [[ "$SHOW_ALL" == "false" ]]; then
                local status=$(jq -r '.status // "unknown"' "$session_file" 2>/dev/null)
                [[ "$status" == "completed" ]] && continue
            fi
            
            sessions+=("$session_id")
        done
    fi
    
    if [[ ${#sessions[@]} -eq 0 ]]; then
        info "No active sessions found."
        exit 0
    fi
    
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        output_json "${sessions[@]}"
    else
        output_table "${sessions[@]}"
    fi
}

main
