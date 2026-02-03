#!/bin/bash
#
# Spawn new sub-agents
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Defaults
TASK=""
LABEL=""
PARENT_SESSION=""
TIMEOUT=0
PRIORITY="normal"
ENV_VARS=()
WORKING_DIR=""

# Generate session ID
generate_session_id() {
    date +%s%N | sha256sum | head -c 16
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --label|-l)
            LABEL="$2"
            shift 2
            ;;
        --parent|-p)
            PARENT_SESSION="$2"
            shift 2
            ;;
        --timeout|-t)
            TIMEOUT="$2"
            shift 2
            ;;
        --priority)
            PRIORITY="$2"
            shift 2
            ;;
        --env|-e)
            ENV_VARS+=("$2")
            shift 2
            ;;
        --working-dir|-d)
            WORKING_DIR="$2"
            shift 2
            ;;
        --help|-h)
            cat << 'EOF'
Usage: session-manager spawn "task description" [options]

Spawn a new sub-agent session

Options:
    --label, -l         Custom label for the session
    --parent, -p        Parent session ID
    --timeout, -t       Timeout in seconds (0 = no timeout)
    --priority          Priority: low, normal, high (default: normal)
    --env, -e           Environment variable (can be used multiple times)
    --working-dir, -d   Working directory for the session
    --help, -h          Show this help

Examples:
    session-manager spawn "Analyze sales data"
    session-manager spawn "Cleanup old files" --label "cleanup-task"
    session-manager spawn "Build project" --timeout 3600 --priority high
EOF
            exit 0
            ;;
        -*)
            warn "Unknown option: $1"
            shift
            ;;
        *)
            if [[ -z "$TASK" ]]; then
                TASK="$1"
            else
                TASK="$TASK $1"
            fi
            shift
            ;;
    esac
done

# Validate
if [[ -z "$TASK" ]]; then
    error_exit "Task description required"
fi

# Generate session info
create_session() {
    local session_id=$(generate_session_id)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local session_file="$SESSION_DIR/${session_id}.json"
    
    # Default label from task
    if [[ -z "$LABEL" ]]; then
        LABEL=$(echo "$TASK" | cut -c1-30)
    fi
    
    # Parent session detection
    if [[ -z "$PARENT_SESSION" ]]; then
        PARENT_SESSION=$(get_current_session)
    fi
    
    # Working directory
    if [[ -z "$WORKING_DIR" ]]; then
        WORKING_DIR="$(pwd)"
    fi
    
    # Create session record
    cat > "$session_file" << EOF
{
    "session_id": "$session_id",
    "type": "subagent",
    "status": "spawning",
    "label": $(echo "$LABEL" | jq -Rs '.'),
    "task": $(echo "$TASK" | jq -Rs '.'),
    "parent_session": "$PARENT_SESSION",
    "created_at": "$timestamp",
    "timeout": $TIMEOUT,
    "priority": "$PRIORITY",
    "working_directory": "$WORKING_DIR",
    "environment": {},
    "progress": "initializing",
    "pid": null
}
EOF
    
    # Add environment variables
    for env_var in "${ENV_VARS[@]}"; do
        local key=$(echo "$env_var" | cut -d= -f1)
        local value=$(echo "$env_var" | cut -d= -f2-)
        local tmp_file=$(mktemp)
        jq --arg key "$key" --arg value "$value" '.environment[$key] = $value' "$session_file" > "$tmp_file"
        mv "$tmp_file" "$session_file"
    done
    
    echo "$session_id"
}

# Spawn the sub-agent process
spawn_subagent() {
    local session_id="$1"
    local session_file="$SESSION_DIR/${session_id}.json"
    local log_file="$LOG_DIR/${session_id}.log"
    
    # Update status to running
    local tmp_file=$(mktemp)
    jq '.status = "running" | .progress = "started"' "$session_file" > "$tmp_file"
    mv "$tmp_file" "$session_file"
    
    # Create the sub-agent script
    local agent_script=$(mktemp)
    cat > "$agent_script" << 'AGENT_SCRIPT'
#!/bin/bash
SESSION_ID="${1}"
TASK="${2}"
SESSION_FILE="${3}"
LOG_FILE="${4}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

update_status() {
    local status="$1"
    local progress="$2"
    local tmp=$(mktemp)
    jq ".status = \"$status\" | .progress = \"$progress\"" "$SESSION_FILE" > "$tmp" && mv "$tmp" "$SESSION_FILE"
}

log "Sub-agent starting: $SESSION_ID"
log "Task: $TASK"

# Mark as active
update_status "running" "executing"

# Set trap for cleanup
cleanup() {
    log "Sub-agent shutting down"
    update_status "completed" "finished"
    exit 0
}
trap cleanup EXIT

# Execute the task via openclaw
# Note: In a real implementation, this would use the OpenClaw API
log "Executing task via OpenClaw..."

# Simulate work for demo
sleep 1
update_status "running" "processing"

# Here you would typically call openclaw to process the task
# openclaw agent run --session "$SESSION_ID" --task "$TASK"

# Update final status
update_status "completed" "done"
log "Sub-agent completed successfully"
AGENT_SCRIPT
    
    chmod +x "$agent_script"
    
    # Launch the sub-agent in background
    (
        # Set environment
        export SESSION_ID="$session_id"
        export OPENCLAW_SESSION_ID="$session_id"
        export PARENT_SESSION_ID="$PARENT_SESSION"
        
        # Add custom environment variables
        for env_var in "${ENV_VARS[@]}"; do
            export "$env_var"
        done
        
        cd "$WORKING_DIR"
        
        # Execute agent
        exec bash "$agent_script" "$session_id" "$TASK" "$session_file" "$log_file" >> "$log_file" 2>&1
    ) &
    
    local pid=$!
    
    # Record PID
    local tmp_file=$(mktemp)
    jq --arg pid "$pid" '.pid = ($pid | tonumber)' "$session_file" > "$tmp_file"
    mv "$tmp_file" "$session_file"
    
    # Set up timeout if specified
    if [[ $TIMEOUT -gt 0 ]]; then
        (
            sleep "$TIMEOUT"
            if kill -0 "$pid" 2>/dev/null; then
                log "WARN" "Session $session_id timed out after ${TIMEOUT}s"
                kill -TERM "$pid" 2>/dev/null
                sleep 5
                kill -KILL "$pid" 2>/dev/null
                local tmp=$(mktemp)
                jq '.status = "timeout" | .progress = "timed out"' "$session_file" > "$tmp" && mv "$tmp" "$session_file"
            fi
        ) &
    fi
    
    # Cleanup temp script after process completes
    (
        wait "$pid" 2>/dev/null
        rm -f "$agent_script"
    ) &
    
    echo "$pid"
}

# Main
main() {
    log "INFO" "Spawning sub-agent for task: $TASK"
    
    # Create session record
    local session_id=$(create_session)
    success "Created session: $session_id"
    
    # Spawn the process
    local pid=$(spawn_subagent "$session_id")
    info "Started sub-agent process (PID: $pid)"
    
    # Output session info
    echo ""
    echo -e "${CYAN}Session Details:${NC}"
    echo "  ID:       $session_id"
    echo "  Label:    $LABEL"
    echo "  Task:     $TASK"
    echo "  Parent:   $PARENT_SESSION"
    echo "  PID:      $pid"
    echo "  Log:      $LOG_DIR/${session_id}.log"
    
    if [[ $TIMEOUT -gt 0 ]]; then
        echo "  Timeout:  ${TIMEOUT}s"
    fi
    
    echo ""
    echo "Monitor with: session-manager status $session_id"
    
    log "INFO" "Sub-agent spawned: $session_id (PID: $pid)"
}

main
