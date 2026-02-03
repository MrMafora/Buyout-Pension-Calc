#!/bin/bash
#
# Health Checker - Main health check script
# Checks system health: disk, memory, services, logs, network
#

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Default thresholds
DISK_WARNING=80
DISK_CRITICAL=90
MEMORY_WARNING=85
MEMORY_CRITICAL=95
LOG_MAX_MB=100
TEMP_MAX_AGE_HOURS=24

# Config file path
CONFIG_FILE="${OPENCLAW_CONFIG:-$HOME/.openclaw}/config/health-checker.json"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

# Load config if exists
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        DISK_WARNING=$(jq -r '.disk.warning_percent // 80' "$CONFIG_FILE" 2>/dev/null || echo 80)
        DISK_CRITICAL=$(jq -r '.disk.critical_percent // 90' "$CONFIG_FILE" 2>/dev/null || echo 90)
        MEMORY_WARNING=$(jq -r '.memory.warning_percent // 85' "$CONFIG_FILE" 2>/dev/null || echo 85)
        MEMORY_CRITICAL=$(jq -r '.memory.critical_percent // 95' "$CONFIG_FILE" 2>/dev/null || echo 95)
        LOG_MAX_MB=$(jq -r '.logs.max_size_mb // 100' "$CONFIG_FILE" 2>/dev/null || echo 100)
        TEMP_MAX_AGE_HOURS=$(jq -r '.temp.max_age_hours // 24' "$CONFIG_FILE" 2>/dev/null || echo 24)
    fi
}

# Quiet mode
QUIET=false
FIX=false
COMPONENT="all"
EXIT_CODE=0

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quiet|-q)
                QUIET=true
                shift
                ;;
            --fix|-f)
                FIX=true
                shift
                ;;
            --component|-c)
                COMPONENT="$2"
                shift 2
                ;;
            --disk)
                COMPONENT="disk"
                shift
                ;;
            --memory)
                COMPONENT="memory"
                shift
                ;;
            --services)
                COMPONENT="services"
                shift
                ;;
            --logs)
                COMPONENT="logs"
                shift
                ;;
            --network)
                COMPONENT="network"
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
Health Checker - System health monitoring for OpenClaw

Usage: check.sh [OPTIONS]

Options:
    --quiet, -q          Suppress output (exit code only)
    --fix, -f            Attempt to fix issues automatically
    --component, -c      Check specific component (disk|memory|services|logs|network)
    --disk               Check disk space only
    --memory             Check memory usage only
    --services           Check services only
    --logs               Check log files only
    --network            Check network only
    --help, -h           Show this help

Examples:
    check.sh                    # Check everything
    check.sh --disk             # Check disk only
    check.sh --fix              # Check and fix issues
    check.sh --quiet            # Silent, exit code only
EOF
}

# Output helpers
log_info() {
    [[ "$QUIET" == "false" ]] && echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    [[ "$QUIET" == "false" ]] && echo -e "${YELLOW}[WARN]${NC} $1"
    EXIT_CODE=1
}

log_error() {
    [[ "$QUIET" == "false" ]] && echo -e "${RED}[CRIT]${NC} $1"
    EXIT_CODE=2
}

# Check disk space
check_disk() {
    [[ "$QUIET" == "false" ]] && echo -e "\n=== Disk Space ==="
    
    local issues=0
    
    # Get disk usage (excluding tmpfs, devtmpfs, etc.)
    while read -r filesystem size used avail percent mount; do
        # Skip header and non-physical filesystems
        [[ "$filesystem" == "Filesystem" ]] && continue
        [[ "$filesystem" =~ ^tmpfs|^devtmpfs|^overlay|^squashfs ]] && continue
        [[ "$mount" =~ ^/snap|^/boot/efi ]] && continue
        
        # Remove % sign
        local usage_num=${percent%%%}
        
        if [[ $usage_num -ge $DISK_CRITICAL ]]; then
            log_error "CRITICAL: $mount is at ${usage_num}% (${avail} available)"
            issues=$((issues + 1))
        elif [[ $usage_num -ge $DISK_WARNING ]]; then
            log_warn "WARNING: $mount is at ${usage_num}% (${avail} available)"
            issues=$((issues + 1))
        else
            log_info "$mount: ${usage_num}% used (${avail} available)"
        fi
    done < <(df -h)
    
    if [[ $issues -eq 0 ]]; then
        log_info "All filesystems healthy"
    fi
    
    return $issues
}

# Check memory usage
check_memory() {
    [[ "$QUIET" == "false" ]] && echo -e "\n=== Memory Usage ==="
    
    # Get memory info
    local total=$(free -m | awk '/^Mem:/{print $2}')
    local used=$(free -m | awk '/^Mem:/{print $3}')
    local available=$(free -m | awk '/^Mem:/{print $7}')
    
    if [[ $total -gt 0 ]]; then
        local usage_percent=$(( (used * 100) / total ))
        
        if [[ $usage_percent -ge $MEMORY_CRITICAL ]]; then
            log_error "CRITICAL: Memory usage at ${usage_percent}% (${used}MB / ${total}MB)"
            return 2
        elif [[ $usage_percent -ge $MEMORY_WARNING ]]; then
            log_warn "WARNING: Memory usage at ${usage_percent}% (${used}MB / ${total}MB)"
            return 1
        else
            log_info "Memory: ${usage_percent}% used (${used}MB / ${total}MB, ${available}MB available)"
            return 0
        fi
    fi
}

# Check service status
check_services() {
    [[ "$QUIET" == "false" ]] && echo -e "\n=== Service Status ==="
    
    local issues=0
    local services=("openclaw-gateway")
    
    # Load services from config if available
    if [[ -f "$CONFIG_FILE" ]]; then
        local config_services=$(jq -r '.services[]?' "$CONFIG_FILE" 2>/dev/null)
        [[ -n "$config_services" ]] && services=($config_services)
    fi
    
    # Check OpenClaw gateway
    if command -v openclaw &> /dev/null; then
        if openclaw gateway status &> /dev/null; then
            log_info "openclaw-gateway: running"
        else
            log_error "openclaw-gateway: NOT RUNNING"
            issues=$((issues + 1))
            
            if [[ "$FIX" == "true" ]]; then
                log_info "Attempting to start openclaw-gateway..."
                openclaw gateway start &> /dev/null && log_info "openclaw-gateway: started" || log_error "Failed to start openclaw-gateway"
            fi
        fi
    else
        log_warn "openclaw command not found - skipping service check"
    fi
    
    # Check for WhatsApp/bridge processes
    if pgrep -f "whatsapp" > /dev/null 2>&1; then
        log_info "whatsapp-bridge: running"
    else
        log_warn "whatsapp-bridge: not detected (may be optional)"
    fi
    
    # Check common system services
    if systemctl is-active --quiet systemd-journald 2>/dev/null; then
        log_info "systemd-journald: running"
    fi
    
    return $issues
}

# Check log file sizes
check_logs() {
    [[ "$QUIET" == "false" ]] && echo -e "\n=== Log Files ==="
    
    local issues=0
    local log_dirs=(
        "$WORKSPACE/logs"
        "/var/log"
        "$HOME/.openclaw/logs"
    )
    
    for log_dir in "${log_dirs[@]}"; do
        if [[ -d "$log_dir" ]]; then
            while IFS= read -r -d '' file; do
                local size_mb=$(stat -c %s "$file" 2>/dev/null | awk '{print int($1/1024/1024)}')
                
                if [[ $size_mb -gt $LOG_MAX_MB ]]; then
                    log_warn "Large log file: $file (${size_mb}MB)"
                    issues=$((issues + 1))
                    
                    if [[ "$FIX" == "true" ]]; then
                        # Rotate/truncate large log
                        tail -n 1000 "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
                        log_info "Truncated $file to last 1000 lines"
                    fi
                fi
            done < <(find "$log_dir" -type f -name "*.log" -size +${LOG_MAX_MB}M -print0 2>/dev/null)
        fi
    done
    
    if [[ $issues -eq 0 ]]; then
        log_info "Log files within size limits"
    fi
    
    return $issues
}

# Check network connectivity
check_network() {
    [[ "$QUIET" == "false" ]] && echo -e "\n=== Network Connectivity ==="
    
    local issues=0
    local ping_targets=("8.8.8.8" "1.1.1.1")
    local timeout=5
    
    # Load from config
    if [[ -f "$CONFIG_FILE" ]]; then
        local config_targets=$(jq -r '.network.ping_targets[]?' "$CONFIG_FILE" 2>/dev/null)
        [[ -n "$config_targets" ]] && ping_targets=($config_targets)
        timeout=$(jq -r '.network.timeout_seconds // 5' "$CONFIG_FILE" 2>/dev/null || echo 5)
    fi
    
    # Check internet connectivity
    local connected=false
    for target in "${ping_targets[@]}"; do
        if ping -c 1 -W $timeout "$target" > /dev/null 2>&1; then
            log_info "Internet connectivity OK (via $target)"
            connected=true
            break
        fi
    done
    
    if [[ "$connected" == "false" ]]; then
        log_error "No internet connectivity"
        issues=$((issues + 1))
    fi
    
    # Check DNS resolution
    if nslookup google.com > /dev/null 2>&1 || host google.com > /dev/null 2>&1; then
        log_info "DNS resolution: OK"
    else
        log_warn "DNS resolution: issues detected"
    fi
    
    return $issues
}

# Check temporary files
check_temp() {
    [[ "$QUIET" == "false" ]] && echo -e "\n=== Temporary Files ==="
    
    local issues=0
    local temp_dirs=(
        "/tmp"
        "/var/tmp"
        "$WORKSPACE/tmp"
    )
    
    for temp_dir in "${temp_dirs[@]}"; do
        if [[ -d "$temp_dir" ]]; then
            local count=$(find "$temp_dir" -type f -atime +$((TEMP_MAX_AGE_HOURS/24)) 2>/dev/null | wc -l)
            
            if [[ $count -gt 0 ]]; then
                log_warn "$count old temp files in $temp_dir"
                issues=$((issues + 1))
                
                if [[ "$FIX" == "true" ]]; then
                    find "$temp_dir" -type f -atime +$((TEMP_MAX_AGE_HOURS/24)) -delete 2>/dev/null
                    log_info "Cleaned old temp files from $temp_dir"
                fi
            fi
        fi
    done
    
    if [[ $issues -eq 0 ]]; then
        log_info "Temporary files: OK"
    fi
    
    return $issues
}

# Main execution
main() {
    load_config
    parse_args "$@"
    
    [[ "$QUIET" == "false" ]] && echo "OpenClaw Health Check"
    [[ "$QUIET" == "false" ]] && echo "====================="
    [[ "$QUIET" == "false" ]] && echo "Time: $(date)"
    
    case "$COMPONENT" in
        all)
            check_disk
            check_memory
            check_services
            check_logs
            check_temp
            check_network
            ;;
        disk)
            check_disk
            ;;
        memory)
            check_memory
            ;;
        services)
            check_services
            ;;
        logs)
            check_logs
            ;;
        temp)
            check_temp
            ;;
        network)
            check_network
            ;;
        *)
            echo "Unknown component: $COMPONENT"
            show_help
            exit 1
            ;;
    esac
    
    [[ "$QUIET" == "false" ]] && echo -e "\n====================="
    
    if [[ $EXIT_CODE -eq 0 ]]; then
        [[ "$QUIET" == "false" ]] && echo -e "${GREEN}✓ All checks passed${NC}"
    elif [[ $EXIT_CODE -eq 1 ]]; then
        [[ "$QUIET" == "false" ]] && echo -e "${YELLOW}⚠ Warnings detected${NC}"
    else
        [[ "$QUIET" == "false" ]] && echo -e "${RED}✗ Critical issues detected${NC}"
    fi
    
    exit $EXIT_CODE
}

main "$@"
