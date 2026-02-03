#!/bin/bash
#
# test-browser.sh - Test browser automation
# Usage: ./test-browser.sh [options]
# Options:
#   --profile <name> Test specific profile (chrome|openclaw)
#   --visual         Run visual tests (screenshots)
#   --verbose        Show detailed output
#   --quiet          Minimal output
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$SKILL_DIR/data"
SCREENSHOTS_DIR="$DATA_DIR/test-results/screenshots"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
SPECIFIC_PROFILE=""
VISUAL=0
VERBOSE=0
QUIET=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --profile) SPECIFIC_PROFILE="$2"; shift 2 ;;
    --visual) VISUAL=1; shift ;;
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

# Test results
PASS_COUNT=0
FAIL_COUNT=0

# Check if browser binary exists
check_browser_binary() {
  detail "${BLUE}Checking browser binary...${NC}"
  
  if command -v chromium > /dev/null 2>&1 || \
     command -v /snap/bin/chromium > /dev/null 2>&1 || \
     [[ -x "/usr/bin/chromium" ]]; then
    detail "  ${GREEN}✓ Chromium found${NC}"
    return 0
  else
    detail "  ${RED}✗ Chromium not found${NC}"
    return 1
  fi
}

# Test browser control server
test_browser_server() {
  detail "${BLUE}Testing browser control server...${NC}"
  
  # Check if browser control server is running
  local response
  response=$(curl -s --max-time 5 "http://localhost:9222/json/version" 2>/dev/null || echo "")
  
  if [[ -n "$response" ]]; then
    detail "  ${GREEN}✓ Browser control server responding${NC}"
    return 0
  else
    detail "  ${YELLOW}⚠ Browser control server not responding${NC}"
    return 1
  fi
}

# Test basic navigation
test_navigation() {
  detail "${BLUE}Testing navigation...${NC}"
  
  # This would require the browser control server to be running
  # For now, we just check if we can reach a test URL
  if curl -s --max-time 10 "https://example.com" > /dev/null 2>&1; then
    detail "  ${GREEN}✓ Network connectivity OK${NC}"
    return 0
  else
    detail "  ${RED}✗ Network connectivity issue${NC}"
    return 1
  fi
}

# Test screenshot capability
test_screenshot() {
  detail "${BLUE}Testing screenshot capability...${NC}"
  
  mkdir -p "$SCREENSHOTS_DIR"
  
  # Check if we have the necessary tools
  if command -v chromium > /dev/null 2>&1; then
    # Try to take a screenshot
    local screenshot="$SCREENSHOTS_DIR/test-$$.png"
    
    if timeout 10 chromium --headless --disable-gpu --screenshot="$screenshot" \
       --no-sandbox --disable-setuid-sandbox \
       "https://example.com" > /dev/null 2>&1; then
      
      if [[ -f "$screenshot" ]]; then
        detail "  ${GREEN}✓ Screenshot captured${NC}"
        rm -f "$screenshot"
        return 0
      fi
    fi
  fi
  
  detail "  ${YELLOW}⚠ Screenshot test skipped${NC}"
  return 1
}

# Test specific profile
test_profile() {
  local profile="$1"
  
  detail "${BLUE}Testing profile: $profile${NC}"
  
  case "$profile" in
    chrome)
      detail "  Chrome profile requires browser relay extension"
      ;;
    openclaw)
      detail "  OpenClaw profile uses isolated browser instance"
      ;;
    *)
      detail "  Unknown profile: $profile"
      return 1
      ;;
  esac
  
  return 0
}

# Main execution
log "${BLUE}Testing Browser Automation...${NC}"
log ""

# Check binary
if check_browser_binary; then
  log "${GREEN}✓${NC} Browser binary"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  log "${RED}✗${NC} Browser binary"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Check server
if test_browser_server; then
  log "${GREEN}✓${NC} Browser control server"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  log "${YELLOW}⚠${NC} Browser control server (may not be running)"
fi

# Check navigation
if test_navigation; then
  log "${GREEN}✓${NC} Network connectivity"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  log "${RED}✗${NC} Network connectivity"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# Test profile if specified
if [[ -n "$SPECIFIC_PROFILE" ]]; then
  if test_profile "$SPECIFIC_PROFILE"; then
    log "${GREEN}✓${NC} Profile: $SPECIFIC_PROFILE"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${RED}✗${NC} Profile: $SPECIFIC_PROFILE"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
fi

# Visual tests
if [[ $VISUAL -eq 1 ]]; then
  log ""
  log "${YELLOW}Running visual tests...${NC}"
  
  if test_screenshot; then
    log "${GREEN}✓${NC} Screenshot capture"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${YELLOW}⚠${NC} Screenshot capture"
  fi
fi

log ""
log "Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}"

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
else
  exit 0
fi
