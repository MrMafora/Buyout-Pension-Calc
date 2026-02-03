#!/bin/bash
#
# Health Checker - Report generator
# Generates detailed health reports in various formats
#

set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
CONFIG_FILE="${OPENCLAW_CONFIG:-$HOME/.openclaw}/config/health-checker.json"
OUTPUT_FILE=""
VERBOSE=false
FORMAT="text"

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --output|-o)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --format|-f)
                FORMAT="$2"
                shift 2
                ;;
            --json|-j)
                FORMAT="json"
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
Health Checker Report - Generate system health reports

Usage: report.sh [OPTIONS]

Options:
    --output, -o FILE    Save report to file
    --verbose, -v        Include detailed metrics
    --format, -f FMT     Output format: text|json (default: text)
    --json, -j           Shortcut for --format json
    --help, -h           Show this help

Examples:
    report.sh                    # Print report to stdout
    report.sh -o report.json -j  # Save JSON report
    report.sh -v                 # Detailed text report
EOF
}

# Collect system info
collect_system_info() {
    local hostname=$(hostname)
    local os=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Unknown")
    local kernel=$(uname -r)
    local uptime=$(uptime -p 2>/dev/null || uptime | awk -F',' '{print $1}')
    local timestamp=$(date -Iseconds)
    
    echo "{"
    echo "  \"timestamp\": \"$timestamp\","
    echo "  \"hostname\": \"$hostname\","
    echo "  \"os\": \"$os\","
    echo "  \"kernel\": \"$kernel\","
    echo "  \"uptime\": \"$uptime\","
    echo "  \"checks\": {"
}

# Collect disk info
collect_disk_info() {
    local json=$1
    
    if [[ "$json" == "true" ]]; then
        echo "    \"disk\": ["
        local first=true
        while read -r filesystem size used avail percent mount; do
            [[ "$filesystem" == "Filesystem" ]] && continue
            [[ "$filesystem" =~ ^tmpfs|^devtmpfs|^overlay|^squashfs ]] && continue
            
            [[ "$first" == "true" ]] || echo ","
            first=false
            
            local usage_num=${percent%%%}
            local status="OK"
            [[ $usage_num -ge 80 ]] && status="WARNING"
            [[ $usage_num -ge 90 ]] && status="CRITICAL"
            
            echo -n "      {\"mount\": \"$mount\", \"size\": \"$size\", \"used\": \"$used\", \"available\": \"$avail\", \"usage_percent\": $usage_num, \"status\": \"$status\"}"
        done < <(df -h)
        echo ""
        echo "    ],"
    else
        echo ""
        echo "DISK USAGE"
        echo "=========="
        df -h | grep -vE '^tmpfs|^devtmpfs|^overlay|^Filesystem'
    fi
}

# Collect memory info
collect_memory_info() {
    local json=$1
    
    if [[ "$json" == "true" ]]; then
        local total=$(free -m | awk '/^Mem:/{print $2}')
        local used=$(free -m | awk '/^Mem:/{print $3}')
        local free=$(free -m | awk '/^Mem:/{print $4}')
        local shared=$(free -m | awk '/^Mem:/{print $5}')
        local buffers=$(free -m | awk '/^Mem:/{print $6}')
        local available=$(free -m | awk '/^Mem:/{print $7}')
        local usage_percent=0
        [[ $total -gt 0 ]] && usage_percent=$(( (used * 100) / total ))
        
        local status="OK"
        [[ $usage_percent -ge 85 ]] && status="WARNING"
        [[ $usage_percent -ge 95 ]] && status="CRITICAL"
        
        echo "    \"memory\": {"
        echo "      \"total_mb\": $total,"
        echo "      \"used_mb\": $used,"
        echo "      \"free_mb\": $free,"
        echo "      \"available_mb\": $available,"
        echo "      \"usage_percent\": $usage_percent,"
        echo "      \"status\": \"$status\""
        echo "    },"
    else
        echo ""
        echo "MEMORY"
        echo "======"
        free -h
    fi
}

# Collect CPU info
collect_cpu_info() {
    local json=$1
    
    if [[ "$json" == "true" ]]; then
        local load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
        local cores=$(nproc)
        local load_percent=$(echo "scale=2; ($load / $cores) * 100" | bc 2>/dev/null || echo "0")
        
        echo "    \"cpu\": {"
        echo "      \"load_average\": \"$load\","
        echo "      \"cores\": $cores,"
        echo "      \"load_percent\": $load_percent"
        echo "    },"
    else
        echo ""
        echo "CPU LOAD"
        echo "========"
        uptime
        echo "Cores: $(nproc)"
    fi
}

# Collect service info
collect_service_info() {
    local json=$1
    
    if [[ "$json" == "true" ]]; then
        echo "    \"services\": {"
        
        # OpenClaw gateway
        echo -n "      \"openclaw-gateway\": "
        if command -v openclaw &> /dev/null && openclaw gateway status &> /dev/null; then
            echo "\"running\""
        else
            echo "\"stopped\""
        fi
        
        echo "    },"
    else
        echo ""
        echo "SERVICES"
        echo "========"
        
        if command -v openclaw &> /dev/null; then
            if openclaw gateway status &> /dev/null; then
                echo "openclaw-gateway: RUNNING"
            else
                echo "openclaw-gateway: STOPPED"
            fi
        else
            echo "openclaw-gateway: NOT INSTALLED"
        fi
    fi
}

# Collect network info
collect_network_info() {
    local json=$1
    
    local connected=false
    ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1 && connected=true
    
    if [[ "$json" == "true" ]]; then
        local dns_works=false
        nslookup google.com > /dev/null 2>&1 && dns_works=true
        
        echo "    \"network\": {"
        echo "      \"internet_connected\": $connected,"
        echo "      \"dns_working\": $dns_works"
        echo "    }"
    else
        echo ""
        echo "NETWORK"
        echo "======="
        if [[ "$connected" == "true" ]]; then
            echo "Internet: CONNECTED"
        else
            echo "Internet: DISCONNECTED"
        fi
        
        if command -v ip &> /dev/null; then
            echo ""
            echo "Interfaces:"
            ip -brief addr show 2>/dev/null | grep -v "lo" || true
        fi
    fi
}

# Generate text report
generate_text_report() {
    echo "OpenClaw Health Report"
    echo "======================"
    echo "Generated: $(date)"
    echo "Hostname: $(hostname)"
    echo "OS: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Unknown")"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $(uptime -p 2>/dev/null || uptime | awk -F',' '{print $1}')"
    
    collect_disk_info false
    collect_memory_info false
    collect_cpu_info false
    collect_service_info false
    collect_network_info false
    
    echo ""
    echo "======================"
    echo "Report Complete"
}

# Generate JSON report
generate_json_report() {
    collect_system_info
    collect_disk_info true
    collect_memory_info true
    collect_cpu_info true
    collect_service_info true
    collect_network_info true
    echo "  }"
    echo "}"
}

# Main
main() {
    parse_args "$@"
    
    local report=""
    
    if [[ "$FORMAT" == "json" ]]; then
        report=$(generate_json_report)
    else
        report=$(generate_text_report)
    fi
    
    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$report" > "$OUTPUT_FILE"
        echo "Report saved to: $OUTPUT_FILE"
    else
        echo "$report"
    fi
}

main "$@"
