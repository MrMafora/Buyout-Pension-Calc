#!/bin/bash
#
# Cleanup completed/stale sessions
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
FORCE=false
OLDER_THAN=""
DRY_RUN=false
CLEAN_LOGS=false
CLEAN_ALL_COMPLETED=false
MAX_AGE_DAYS=7

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force|-f)
            FORCE=true
            shift
            ;;
        --older|-o)
            OLDER_THAN="$2"
            shift 2
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --logs|-l)
            CLEAN_LOGS=true
            shift
            ;;
        --completed|-c)
            CLEAN_ALL_COMPLETED=true
            shift
            ;;
        --max-age)
            MAX_AGE_DAYS="$2"
            shift 2
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager cleanup [options]

Remove completed, stale, or old sessions

Options:
    --force, -f         Force cleanup of stuck/running sessions
    --older, -o         Remove sessions older than duration (e.g., 7d, 24h)
    --dry-run, -n       Show what would be removed without deleting
    --logs, -l          Also clean old log files
    --completed, -c     Clean all completed sessions
    --max-age           Maximum age in days for logs (default: 7)
    --help, -h          Show this help

Examples:
    session-manager cleanup
    session-manager cleanup --older 7d
    session-manager cleanup --force --dry-run
    session-manager cleanup --completed --logs
EOF
            exit 0
            ;;
        *)
            warn "Unknown option: $1"
            shift
            ;;
    esac
done

# Calculate cutoff time for age-based cleanup
get_cutoff_seconds() {
    if [[ -n "$OLDER_THAN" ]]; then
        parse_duration "$OLDER_THAN"
    else
        echo $((MAX_AGE_DAYS * 86400))
    fi
}

# Check if session should be cleaned
should_clean_session() {
    local session_file="$1"
    local session_id=$(basename "$session_file" .json)
    local status=$(jq -r '.status // "unknown"' "$session_file" 2>/dev/null)
    local age_sec=$(get_session_age "$session_file")
    local cutoff=$(get_cutoff_seconds)
    local pid=$(jq -r '.pid // "null"' "$session_file" 2>/dev/null)
    
    # If force mode, consider all sessions
    if [[ "$FORCE" == "true" ]]; then
        # Check if process is actually dead
        if [[ "$pid" != "null" ]] && [[ -n "$pid" ]]; then
            if ! kill -0 "$pid" 2>/dev/null; then
                return 0  # Process is dead, clean it
            fi
        else
            return 0
        fi
        return 1
    fi
    
    # Clean completed sessions
    if [[ "$CLEAN_ALL_COMPLETED" == "true" ]] && [[ "$status" == "completed" ]]; then
        return 0
    fi
    
    # Clean old sessions by age
    if [[ $age_sec -gt $cutoff ]]; then
        # Only clean completed/error/timeout sessions unless forced
        if [[ "$status" =~ ^(completed|error|failed|timeout|unknown)$ ]]; then
            return 0
        fi
    fi
    
    return 1
}

# Clean a session
clean_session() {
    local session_file="$1"
    local session_id=$(basename "$session_file" .json)
    local status=$(jq -r '.status // "unknown"' "$session_file" 2>/dev/null)
    local age_sec=$(get_session_age "$session_file")
    local pid=$(jq -r '.pid // "null"' "$session_file" 2>/dev/null)
    
    # Kill process if running
    if [[ "$pid" != "null" ]] && [[ -n "$pid" ]]; then
        if kill -0 "$pid" 2>/dev/null; then
            if [[ "$FORCE" == "true" ]]; then
                log "INFO" "Killing process $pid for session $session_id"
                if [[ "$DRY_RUN" == "false" ]]; then
                    kill -TERM "$pid" 2>/dev/null
                    sleep 2
                    kill -KILL "$pid" 2>/dev/null
                fi
            fi
        fi
    fi
    
    # Remove session file
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY-RUN] Would remove: $session_file (status: $status, age: $(format_duration $age_sec))"
    else
        rm -f "$session_file"
        log "INFO" "Cleaned session: $session_id"
    fi
    
    # Clean associated log file if requested
    local log_file="$LOG_DIR/${session_id}.log"
    if [[ "$CLEAN_LOGS" == "true" ]] && [[ -f "$log_file" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "[DRY-RUN] Would remove: $log_file"
        else
            rm -f "$log_file"
            log "INFO" "Cleaned log: $session_id"
        fi
    fi
}

# Clean old log files
clean_old_logs() {
    local cutoff_days="${1:-$MAX_AGE_DAYS}"
    
    info "Checking for log files older than ${cutoff_days} days..."
    
    find "$LOG_DIR" -name "*.log" -type f -mtime +$cutoff_days 2>/dev/null | while read -r log_file; do
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "[DRY-RUN] Would remove old log: $log_file"
        else
            rm -f "$log_file"
            log "INFO" "Cleaned old log: $(basename "$log_file")"
        fi
    done
}

# Main cleanup function
main() {
    local total_sessions=0
    local cleaned=0
    local to_clean=()
    
    # Collect sessions to clean
    for session_file in "$SESSION_DIR"/*.json 2>/dev/null; do
        [[ -f "$session_file" ]] || continue
        total_sessions=$((total_sessions + 1))
        
        if should_clean_session "$session_file"; then
            to_clean+=("$session_file")
        fi
    done
    
    if [[ ${#to_clean[@]} -eq 0 ]]; then
        success "No sessions need cleanup."
        
        # Still clean old logs if requested
        if [[ "$CLEAN_LOGS" == "true" ]]; then
            clean_old_logs
        fi
        
        exit 0
    fi
    
    # Report what we're doing
    echo -e "${CYAN}Found ${#to_clean[@]} session(s) to clean out of $total_sessions total${NC}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}DRY RUN - No changes will be made${NC}"
    fi
    
    echo ""
    
    # Clean each session
    for session_file in "${to_clean[@]}"; do
        clean_session "$session_file"
        cleaned=$((cleaned + 1))
    done
    
    # Clean old logs
    if [[ "$CLEAN_LOGS" == "true" ]]; then
        clean_old_logs
    fi
    
    echo ""
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN complete. $cleaned sessions would be cleaned."
    else
        success "Cleanup complete. $cleaned session(s) removed."
    fi
    
    log "INFO" "Cleanup completed: $cleaned sessions cleaned"
}

main
