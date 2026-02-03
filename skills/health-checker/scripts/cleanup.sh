#!/bin/bash
#
# Health Checker - Cleanup utility
# Cleans temporary files and old logs
#

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Config
CONFIG_FILE="${OPENCLAW_CONFIG:-$HOME/.openclaw}/config/health-checker.json"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

# Default settings
DRY_RUN=false
CLEAN_TEMP=false
CLEAN_LOGS=false
CLEAN_ALL=false
TEMP_MAX_AGE_HOURS=24
LOG_MAX_AGE_DAYS=7

# Load config
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        TEMP_MAX_AGE_HOURS=$(jq -r '.temp.max_age_hours // 24' "$CONFIG_FILE" 2>/dev/null || echo 24)
        LOG_MAX_AGE_DAYS=$(jq -r '.logs.max_age_days // 7' "$CONFIG_FILE" 2>/dev/null || echo 7)
    fi
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run|-n)
                DRY_RUN=true
                shift
                ;;
            --temp|-t)
                CLEAN_TEMP=true
                shift
                ;;
            --logs|-l)
                CLEAN_LOGS=true
                shift
                ;;
            --all|-a)
                CLEAN_ALL=true
                shift
                ;;
            --force|-f)
                DRY_RUN=false
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
    
    # If nothing specified, default to dry-run all
    if [[ "$CLEAN_TEMP" == "false" && "$CLEAN_LOGS" == "false" && "$CLEAN_ALL" == "false" ]]; then
        CLEAN_ALL=true
        DRY_RUN=true
    fi
}

show_help() {
    cat << EOF
Health Checker Cleanup - Clean temporary files and old logs

Usage: cleanup.sh [OPTIONS]

Options:
    --dry-run, -n        Show what would be cleaned (default)
    --temp, -t           Clean temporary files
    --logs, -l           Clean old log files
    --all, -a            Clean everything
    --force, -f          Actually delete (not dry run)
    --help, -h           Show this help

Examples:
    cleanup.sh                    # Dry run - show what would be cleaned
    cleanup.sh --all --force      # Actually clean everything
    cleanup.sh --temp --force     # Clean only temp files
    cleanup.sh --logs -n          # Show what log files would be cleaned
EOF
}

# Output helpers
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_action() {
    echo -e "${BLUE}[CLEAN]${NC} $1"
}

# Format bytes to human readable
human_readable() {
    local bytes=$1
    if [[ $bytes -gt 1073741824 ]]; then
        echo "$(echo "scale=2; $bytes/1073741824" | bc)GB"
    elif [[ $bytes -gt 1048576 ]]; then
        echo "$(echo "scale=2; $bytes/1048576" | bc)MB"
    elif [[ $bytes -gt 1024 ]]; then
        echo "$(echo "scale=2; $bytes/1024" | bc)KB"
    else
        echo "${bytes}B"
    fi
}

# Clean temporary files
clean_temp() {
    echo -e "\n=== Temporary Files ==="
    
    local temp_dirs=(
        "/tmp"
        "/var/tmp"
        "$WORKSPACE/tmp"
        "$HOME/tmp"
        "$HOME/.cache"
    )
    
    local total_freed=0
    local total_files=0
    
    for temp_dir in "${temp_dirs[@]}"; do
        if [[ -d "$temp_dir" ]]; then
            log_info "Scanning: $temp_dir"
            
            # Find old files
            while IFS= read -r -d '' file; do
                local size=$(stat -c %s "$file" 2>/dev/null || echo 0)
                total_freed=$((total_freed + size))
                total_files=$((total_files + 1))
                
                if [[ "$DRY_RUN" == "true" ]]; then
                    log_warn "Would delete: $file ($(human_readable $size))"
                else
                    rm -f "$file" 2>/dev/null && log_action "Deleted: $file ($(human_readable $size))" || log_warn "Failed to delete: $file"
                fi
            done < <(find "$temp_dir" -type f -atime +$((TEMP_MAX_AGE_HOURS/24)) -print0 2>/dev/null || true)
            
            # Clean empty directories
            if [[ "$DRY_RUN" == "false" ]]; then
                find "$temp_dir" -type d -empty -delete 2>/dev/null || true
            fi
        fi
    done
    
    echo "Files: $total_files, Space: $(human_readable $total_freed)"
}

# Clean old log files
clean_logs() {
    echo -e "\n=== Log Files ==="
    
    local log_dirs=(
        "$WORKSPACE/logs"
        "$HOME/.openclaw/logs"
        "/var/log/openclaw"
    )
    
    local total_freed=0
    local total_files=0
    
    for log_dir in "${log_dirs[@]}"; do
        if [[ -d "$log_dir" ]]; then
            log_info "Scanning: $log_dir"
            
            # Find old log files
            while IFS= read -r -d '' file; do
                local size=$(stat -c %s "$file" 2>/dev/null || echo 0)
                total_freed=$((total_freed + size))
                total_files=$((total_files + 1))
                
                if [[ "$DRY_RUN" == "true" ]]; then
                    log_warn "Would delete: $file ($(human_readable $size))"
                else
                    rm -f "$file" 2>/dev/null && log_action "Deleted: $file ($(human_readable $size))" || log_warn "Failed to delete: $file"
                fi
            done < <(find "$log_dir" -type f \( -name "*.log.*" -o -name "*.log.old" \) -mtime +$LOG_MAX_AGE_DAYS -print0 2>/dev/null || true)
        fi
    done
    
    # Truncate current logs if they're too large
    for log_dir in "${log_dirs[@]}"; do
        if [[ -d "$log_dir" ]]; then
            while IFS= read -r -d '' file; do
                local size=$(stat -c %s "$file" 2>/dev/null || echo 0)
                
                if [[ $size -gt 104857600 ]]; then  # 100MB
                    if [[ "$DRY_RUN" == "true" ]]; then
                        log_warn "Would truncate: $file ($(human_readable $size))"
                    else
                        tail -n 10000 "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
                        local new_size=$(stat -c %s "$file" 2>/dev/null || echo 0)
                        log_action "Truncated: $file ($(human_readable $size) → $(human_readable $new_size))"
                    fi
                fi
            done < <(find "$log_dir" -type f -name "*.log" -size +100M -print0 2>/dev/null || true)
        fi
    done
    
    echo "Files: $total_files, Space: $(human_readable $total_freed)"
}

# Clean package cache
clean_package_cache() {
    echo -e "\n=== Package Cache ==="
    
    if command -v apt-get &> /dev/null; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_warn "Would clean apt cache"
        else
            apt-get autoclean -qq 2>/dev/null && log_action "Cleaned apt cache" || log_warn "apt autoclean failed (may need sudo)"
        fi
    fi
    
    if command -v snap &> /dev/null; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_warn "Would clean snap revisions"
        else
            # Remove old snap revisions
            snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do
                snap remove "$snapname" --revision="$revision" 2>/dev/null && log_action "Removed $snapname revision $revision" || true
            done
        fi
    fi
}

# Main
main() {
    load_config
    parse_args "$@"
    
    echo "OpenClaw Health Cleanup"
    echo "======================="
    echo "Time: $(date)"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}DRY RUN - No files will be deleted${NC}"
    fi
    
    if [[ "$CLEAN_ALL" == "true" ]] || [[ "$CLEAN_TEMP" == "true" ]]; then
        clean_temp
    fi
    
    if [[ "$CLEAN_ALL" == "true" ]] || [[ "$CLEAN_LOGS" == "true" ]]; then
        clean_logs
    fi
    
    if [[ "$CLEAN_ALL" == "true" ]]; then
        clean_package_cache
    fi
    
    echo -e "\n======================="
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${BLUE}Use --force to actually clean these files${NC}"
    else
        echo -e "${GREEN}✓ Cleanup complete${NC}"
    fi
}

main "$@"
