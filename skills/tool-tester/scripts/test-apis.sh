#!/bin/bash
#
# test-apis.sh - Test API connectivity
# Usage: ./test-apis.sh [options]
# Options:
#   --api <name>    Test specific API
#   --retry <n>     Number of retries (default: 1)
#   --timeout <sec> Set timeout (default: 10)
#   --verbose       Show detailed output
#   --quiet         Minimal output
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
SPECIFIC_API=""
RETRY=1
TIMEOUT=10
VERBOSE=0
QUIET=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --api) SPECIFIC_API="$2"; shift 2 ;;
    --retry) RETRY="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --verbose) VERBOSE=1; shift ;;
    --quiet) QUIET=1; shift ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done

log() {
  if [[ $QUIET -eq 0 ]]; then
    echo -e "$@"
  fi
}

detail() {
  if [[ $VERBOSE -eq 1 ]]; then
    echo -e "$@"
  fi
}

# Load config if available
CONFIG_FILE="$SKILL_DIR/references/test-config.json"
if [[ -f "$CONFIG_FILE" ]]; then
  detail "${BLUE}Loading config from $CONFIG_FILE${NC}"
fi

# API endpoint definitions
declare -A API_ENDPOINTS
declare -A API_DESCRIPTIONS

API_ENDPOINTS[brave]="https://api.search.brave.com"
API_DESCRIPTIONS[brave]="Brave Search API"

API_ENDPOINTS[resend]="https://api.resend.com"
API_DESCRIPTIONS[resend]="Resend Email API"

API_ENDPOINTS[gateway]="http://localhost:3000"
API_DESCRIPTIONS[gateway]="OpenClaw Gateway"

API_ENDPOINTS[browser]="http://localhost:9222"
API_DESCRIPTIONS[browser]="Browser Control Server"

# Test a single API
test_api() {
  local name="$1"
  local endpoint="${API_ENDPOINTS[$name]}"
  local desc="${API_DESCRIPTIONS[$name]}"
  
  detail "${BLUE}Testing $name...${NC}"
  detail "  Description: $desc"
  detail "  Endpoint: $endpoint"
  
  local attempt=1
  local success=0
  
  while [[ $attempt -le $RETRY && $success -eq 0 ]]; do
    if [[ $attempt -gt 1 ]]; then
      detail "  Retry attempt $attempt..."
    fi
    
    # Use curl to test connectivity
    local response
    local http_code
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$endpoint" 2>/dev/null || echo "000")
    
    case "$response" in
      200|201|204)
        detail "  ${GREEN}✓ Connected (HTTP $response)${NC}"
        success=1
        ;;
      401|403)
        detail "  ${YELLOW}⚡ Authentication required (HTTP $response)${NC}"
        success=1  # Endpoint is reachable, auth is separate issue
        ;;
      000)
        detail "  ${RED}✗ Connection failed${NC}"
        ;;
      *)
        detail "  ${YELLOW}⚠ Unexpected response (HTTP $response)${NC}"
        success=1  # Endpoint responded
        ;;
    esac
    
    attempt=$((attempt + 1))
  done
  
  if [[ $success -eq 1 ]]; then
    return 0
  else
    return 1
  fi
}

# Test with ping fallback
test_connectivity() {
  local endpoint="$1"
  local host=$(echo "$endpoint" | sed -E 's|https?://||' | sed -E 's|:[0-9]+.*||')
  
  # Try ping as fallback
  if ping -c 1 -W 2 "$host" > /dev/null 2>&1; then
    return 0
  fi
  
  return 1
}

# Main execution
PASS_COUNT=0
FAIL_COUNT=0

if [[ -n "$SPECIFIC_API" ]]; then
  if [[ -z "${API_ENDPOINTS[$SPECIFIC_API]}" ]]; then
    echo "Unknown API: $SPECIFIC_API"
    exit 2
  fi
  
  if test_api "$SPECIFIC_API"; then
    echo "${GREEN}✓ $SPECIFIC_API is reachable${NC}"
    exit 0
  else
    echo "${RED}✗ $SPECIFIC_API is not reachable${NC}"
    exit 1
  fi
fi

log "${BLUE}Testing API Connectivity...${NC}"
log ""

for api in "${!API_ENDPOINTS[@]}"; do
  if test_api "$api"; then
    log "${GREEN}✓${NC} $api"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${RED}✗${NC} $api"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

log ""
log "Results: ${GREEN}$PASS_COUNT reachable${NC}, ${RED}$FAIL_COUNT unreachable${NC}"

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
else
  exit 0
fi
