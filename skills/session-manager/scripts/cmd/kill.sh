#!/bin/bash
#
# Terminate/kill a session
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
SESSION_ID=""
FORCE=false
SIGNAL="TERM"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force|-f)
            FORCE=true
            SIGNAL="KILL"
            shift
            ;;
        --signal|-s)
            SIGNAL="$2"
            shift 2
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager kill <session-id> [options]

Terminate a running session

Options:
    --force, -f         Force kill (SIGKILL)
    --signal, -s        Signal to send (default: TERM)
    --help, -h          Show this help

Examples:
    session-manager kill abc123
    session-manager kill abc123 --force
    session-manager kill abc123 --signal HUP
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

# Kill session
kill_session() {
    local session_id="$1"
    local session_file="$SESSION_DIR/${session_id}.json"
    
    if [[ ! -f "$session_file" ]]; then
        error_exit "Session not found: $session_id"
    fi
    
    local info=$(cat "$session_file")
    local pid=$(echo "$info" | jq -r '.pid // "null"')
    local status=$(echo "$info" | jq -r '.status // "unknown"')
    local label=$(echo "$info" | jq -r '.label // "-"')
    
    info "Terminating session: $session_id"
    info "  Label: $label"
    info "  Status: $status"
    info "  PID: $pid"
    
    # Check if already stopped
    if [[ "$status" == "completed" ]] || [[ "$status" == "terminated" ]]; then
        warn "Session is already stopped (status: $status)"
        
        # Clean up file if requested
        if [[ "$FORCE" == "true" ]]; then
            rm -f "$session_file"
            success "Session file removed"
        fi
        return 0
    fi
    
    # Send signal to process
    if [[ "$pid" != "null" ]] && [[ -n "$pid" ]]; then
        if kill -0 "$pid" 2>/dev/null; then
            log "INFO" "Sending SIG$SIGNAL to process $pid"
            
            if kill -$SIGNAL "$pid" 2>/dev/null; then
                success "Signal SIG$SIGNAL sent to process $pid"
                
                # Wait a moment and check if process is still running
                if [[ "$SIGNAL" != "KILL" ]]; then
                    sleep 2
                    if kill -0 "$pid" 2>/dev/null; then
                        warn "Process still running, sending SIGKILL..."
                        kill -KILL "$pid" 2>/dev/null
                    fi
                fi
            else
                error_exit "Failed to send signal to process $pid"
            fi
        else
            warn "Process $pid is not running"
        fi
    else
        warn "No PID recorded for this session"
    fi
    
    # Update session status
    local tmp_file=$(mktemp)
    jq '.status = "terminated" | .progress = "killed by user"' "$session_file" > "$tmp_file"
    mv "$tmp_file" "$session_file"
    
    log "INFO" "Session $session_id terminated by user"
    success "Session terminated successfully"
}

# Main
main() {
    kill_session "$SESSION_ID"
}

main
