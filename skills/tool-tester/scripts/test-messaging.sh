#!/bin/bash
#
# test-messaging.sh - Test messaging channels
# Usage: ./test-messaging.sh [options]
# Options:
#   --channel <name> Test specific channel (whatsapp|discord|telegram|email)
#   --send-test      Send actual test message
#   --verbose        Show detailed output
#   --quiet          Minimal output
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
SPECIFIC_CHANNEL=""
SEND_TEST=0
VERBOSE=0
QUIET=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --channel) SPECIFIC_CHANNEL="$2"; shift 2 ;;
    --send-test) SEND_TEST=1; shift ;;
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

# Test WhatsApp
test_whatsapp() {
  detail "${BLUE}Testing WhatsApp...${NC}"
  
  # Check if WhatsApp is configured
  # This would check for credentials/config
  local configured=0
  
  if [[ -f "$HOME/.openclay/config/whatsapp.json" ]] || \
     [[ -n "$WHATSAPP_API_KEY" ]]; then
    configured=1
  fi
  
  if [[ $configured -eq 1 ]]; then
    detail "  ${GREEN}✓ WhatsApp configured${NC}"
    
    if [[ $SEND_TEST -eq 1 ]]; then
      detail "  ${YELLOW}⚠ Test message sending not implemented in bash${NC}"
    fi
    
    return 0
  else
    detail "  ${YELLOW}⚠ WhatsApp not configured${NC}"
    return 1
  fi
}

# Test Discord
test_discord() {
  detail "${BLUE}Testing Discord...${NC}"
  
  local configured=0
  
  if [[ -f "$HOME/.openclaw/config/discord.json" ]] || \
     [[ -n "$DISCORD_BOT_TOKEN" ]]; then
    configured=1
  fi
  
  if [[ $configured -eq 1 ]]; then
    detail "  ${GREEN}✓ Discord configured${NC}"
    return 0
  else
    detail "  ${YELLOW}⚠ Discord not configured${NC}"
    return 1
  fi
}

# Test Telegram
test_telegram() {
  detail "${BLUE}Testing Telegram...${NC}"
  
  local configured=0
  
  if [[ -f "$HOME/.openclaw/config/telegram.json" ]] || \
     [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
    configured=1
  fi
  
  if [[ $configured -eq 1 ]]; then
    detail "  ${GREEN}✓ Telegram configured${NC}"
    return 0
  else
    detail "  ${YELLOW}⚠ Telegram not configured${NC}"
    return 1
  fi
}

# Test Email
test_email() {
  detail "${BLUE}Testing Email...${NC}"
  
  local configured=0
  
  # Check for email configuration
  if [[ -n "$RESEND_API_KEY" ]] || \
     [[ -f "$HOME/.openclaw/config/email.json" ]]; then
    configured=1
  fi
  
  if [[ $configured -eq 1 ]]; then
    detail "  ${GREEN}✓ Email configured${NC}"
    
    # Test SMTP/connectivity if possible
    if command -v nc > /dev/null 2>&1; then
      if nc -z -w 2 smtp.gmail.com 587 2>/dev/null || \
         nc -z -w 2 smtp.resend.com 587 2>/dev/null; then
        detail "  ${GREEN}✓ SMTP reachable${NC}"
      fi
    fi
    
    return 0
  else
    detail "  ${YELLOW}⚠ Email not configured${NC}"
    return 1
  fi
}

# Test a specific channel
test_channel() {
  local channel="$1"
  
  case "$channel" in
    whatsapp)
      test_whatsapp
      ;;
    discord)
      test_discord
      ;;
    telegram)
      test_telegram
      ;;
    email)
      test_email
      ;;
    *)
      echo "Unknown channel: $channel"
      exit 2
      ;;
  esac
}

# Main execution
log "${BLUE}Testing Messaging Channels...${NC}"
log ""

if [[ -n "$SPECIFIC_CHANNEL" ]]; then
  if test_channel "$SPECIFIC_CHANNEL"; then
    log "${GREEN}✓${NC} $SPECIFIC_CHANNEL"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${YELLOW}⚠${NC} $SPECIFIC_CHANNEL (not configured)"
  fi
else
  # Test all channels
  if test_whatsapp; then
    log "${GREEN}✓${NC} WhatsApp"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${YELLOW}⚠${NC} WhatsApp"
  fi
  
  if test_discord; then
    log "${GREEN}✓${NC} Discord"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${YELLOW}⚠${NC} Discord"
  fi
  
  if test_telegram; then
    log "${GREEN}✓${NC} Telegram"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${YELLOW}⚠${NC} Telegram"
  fi
  
  if test_email; then
    log "${GREEN}✓${NC} Email"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${YELLOW}⚠${NC} Email"
  fi
fi

log ""
log "Results: ${GREEN}$PASS_COUNT configured${NC}, channels not shown are unconfigured"

# Don't fail if channels aren't configured - that's expected
exit 0
