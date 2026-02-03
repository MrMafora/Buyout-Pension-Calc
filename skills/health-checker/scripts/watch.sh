#!/bin/bash
#
# Health Checker - Watch mode
# Continuous monitoring with alerts
#

set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Settings
INTERVAL=300  # 5 minutes
ALERT_ONLY=false
ALERT_COOLDOWN=3600  # 1 hour between same alerts
LAST_ALERT_FILE="/tmp/health-checker-alerts"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --interval|-i)
                INTERVAL=$(($2 * 60))  # Convert minutes to seconds
                shift 2
                ;;
            --alert-only|-a)
                ALERT_ONLY=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
Health Checker Watch - Continuous monitoring

Usage: watch.sh [OPTIONS]

Options:
    --interval, -i MIN   Check interval in minutes (default: 5)
    --alert-only, -a     Only show output on alerts
    --help, -h           Show this help

Examples:
    watch.sh                    # Watch with 5 min interval
    watch.sh -i 10              # Watch with 10 min interval
    watch.sh --alert-only       # Only alert on issues

Press Ctrl+C to stop
EOF
}

# Initialize alert tracking
init_alerts() {
    mkdir -p "$(dirname "$LAST_ALERT_FILE")"
    touch "$LAST_ALERT_FILE"
}

# Check if we should alert (cooldown)
should_alert() {
    local alert_type="$1"
    local now=$(date +%s)
    
    if [[ -f "$LAST_ALERT_FILE.$alert_type" ]]; then
        local last_alert=$(cat "$LAST_ALERT_FILE.$alert_type")
        local elapsed=$((now - last_alert))
        
        if [[ $elapsed -lt $ALERT_COOLDOWN ]]; then
            return 1  # Don't alert yet
        fi
    fi
    
    echo "$now" > "$LAST_ALERT_FILE.$alert_type"
    return 0  # OK to alert
}

# Send notification
send_notification() {
    local level="$1"
    local message="$2"
    
    # Desktop notification if available
    if command -v notify-send &> /dev/null; then
        local icon="dialog-information"
        [[ "$level" == "warning" ]] && icon="dialog-warning"
        [[ "$level" == "critical" ]] && icon="dialog-error"
        notify-send -i "$icon" "OpenClaw Health" "$message" 2>/dev/null || true
    fi
    
    # Log to syslog if available
    if command -v logger &> /dev/null; then
        logger -t "health-checker" "[$level] $message"
    fi
    
    # Write to health-checker log
    echo "[$(date -Iseconds)] [$level] $message" >> "$WORKSPACE/logs/health-checker-watch.log" 2>/dev/null || true
}

# Run check and handle results
run_check() {
    local check_output
    local exit_code=0
    
    # Run the check script quietly
    if ! check_output=$("$SKILL_DIR/check.sh" --quiet 2>&1); then
        exit_code=$?
    fi
    
    # Parse results from specific checks
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    local mem_usage=$(free | awk '/^Mem:/{printf("%.0f", $3/$2 * 100.0)}')
    
    local alerts=()
    
    # Check thresholds
    if [[ $disk_usage -ge 90 ]]; then
        if should_alert "disk_critical"; then
            alerts+=("CRITICAL: Disk usage at ${disk_usage}%")
            send_notification "critical" "Disk usage critical: ${disk_usage}%"
        fi
    elif [[ $disk_usage -ge 80 ]]; then
        if should_alert "disk_warning"; then
            alerts+=("WARNING: Disk usage at ${disk_usage}%")
            send_notification "warning" "Disk usage high: ${disk_usage}%"
        fi
    fi
    
    if [[ $mem_usage -ge 95 ]]; then
        if should_alert "mem_critical"; then
            alerts+=("CRITICAL: Memory usage at ${mem_usage}%")
            send_notification "critical" "Memory usage critical: ${mem_usage}%"
        fi
    elif [[ $mem_usage -ge 85 ]]; then
        if should_alert "mem_warning"; then
            alerts+=("WARNING: Memory usage at ${mem_usage}%")
            send_notification "warning" "Memory usage high: ${mem_usage}%"
        fi
    fi
    
    # Check if gateway is running
    if ! "$SKILL_DIR/check.sh" --component services --quiet 2>/dev/null; then
        if should_alert "service"; then
            alerts+=("WARNING: OpenClaw services issue detected")
            send_notification "warning" "OpenClaw service issue"
        fi
    fi
    
    # Output
    if [[ ${#alerts[@]} -gt 0 ]]; then
        echo -e "${RED}[ALERT]$(date '+%Y-%m-%d %H:%M:%S')${NC}"
        for alert in "${alerts[@]}"; do
            echo "  - $alert"
        done
        return 1
    elif [[ "$ALERT_ONLY" == "false" ]]; then
        echo -e "${GREEN}[OK] $(date '+%Y-%m-%d %H:%M:%S')${NC} Disk: ${disk_usage}% | Mem: ${mem_usage}%"
    fi
    
    return 0
}

# Main watch loop
main() {
    parse_args "$@"
    init_alerts
    
    echo "OpenClaw Health Watch"
    echo "====================="
    echo "Interval: $((INTERVAL / 60)) minutes"
    echo "Mode: $([[ "$ALERT_ONLY" == "true" ]] && echo "Alert only" || echo "Verbose")"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    
    # Create logs directory
    mkdir -p "$WORKSPACE/logs"
    
    # Initial check
    run_check
    
    # Watch loop
    while true; do
        sleep $INTERVAL
        run_check
    done
}

# Handle Ctrl+C
trap 'echo -e "\n\nWatch stopped."; exit 0' INT

main "$@"
