---
name: tool-tester
description: Test and verify OpenClaw tools, scripts, and integrations. Use when: (1) Verifying tool availability and functionality, (2) Testing script execution, (3) Checking API connectivity, (4) Validating environment setup, (5) Running integration tests, (6) Testing browser automation, (7) Verifying messaging channels, (8) Generating test reports.
---

# Tool Tester

Comprehensive testing framework for OpenClaw tools, scripts, and integrations.

## Overview

This skill provides automated testing capabilities to verify that all OpenClaw tools, scripts, and integrations are functioning correctly. It runs diagnostic checks, performs integration tests, and generates detailed test reports.

## Quick Start

```bash
# Run all tests
./scripts/run-all-tests.sh

# Test specific category
./scripts/test-tools.sh
./scripts/test-scripts.sh
./scripts/test-apis.sh
./scripts/test-browser.sh
./scripts/test-messaging.sh

# Generate test report
./scripts/generate-report.sh
```

## Test Categories

### 1. Tool Availability Tests

Verify all OpenClaw tools are accessible and responding:

```bash
# Test all tools
./scripts/test-tools.sh

# Test specific tool
./scripts/test-tools.sh --tool browser

# Verbose output
./scripts/test-tools.sh --verbose
```

**Tools Tested:**
- `read` - File reading operations
- `write` - File writing operations
- `edit` - File editing operations
- `exec` - Shell command execution
- `process` - Process management
- `web_search` - Web search functionality
- `web_fetch` - URL content fetching
- `browser` - Browser automation
- `canvas` - Canvas operations
- `nodes` - Node management
- `message` - Messaging channels
- `image` - Image analysis
- `tts` - Text-to-speech

### 2. Script Execution Tests

Verify scripts run correctly and produce expected output:

```bash
# Test all scripts in workspace
./scripts/test-scripts.sh

# Test specific script
./scripts/test-scripts.sh --script /path/to/script.sh

# Test with timeout
./scripts/test-scripts.sh --timeout 30
```

### 3. API Connectivity Tests

Check external API connectivity and authentication:

```bash
# Test all configured APIs
./scripts/test-apis.sh

# Test specific API
./scripts/test-apis.sh --api brave

# Test with retry
./scripts/test-apis.sh --retry 3
```

**APIs Tested:**
- Brave Search API
- Resend Email API
- Browser control server
- Node gateway
- Messaging channels (WhatsApp, Discord, etc.)

### 4. Environment Validation

Verify environment setup and dependencies:

```bash
# Validate environment
./scripts/validate-env.sh

# Check dependencies
./scripts/validate-env.sh --check-deps

# Fix common issues
./scripts/validate-env.sh --fix
```

**Checks:**
- Node.js version
- Required binaries (chromium, ffmpeg, etc.)
- Environment variables
- Directory permissions
- Configuration files

### 5. Integration Tests

Run end-to-end integration tests:

```bash
# Run all integration tests
./scripts/test-integration.sh

# Run specific test suite
./scripts/test-integration.sh --suite browser-automation

# Run with coverage
./scripts/test-integration.sh --coverage
```

**Test Suites:**
- Browser automation workflow
- Messaging channel workflow
- File operation workflow
- Web search and fetch workflow
- Multi-tool integration

### 6. Browser Automation Tests

Test browser control and automation:

```bash
# Test browser functionality
./scripts/test-browser.sh

# Test specific profile
./scripts/test-browser.sh --profile chrome

# Run visual tests
./scripts/test-browser.sh --visual
```

**Tests:**
- Browser status and connectivity
- Page navigation
- Element interaction
- Screenshot capture
- PDF generation

### 7. Messaging Channel Tests

Verify messaging channels are working:

```bash
# Test all messaging channels
./scripts/test-messaging.sh

# Test specific channel
./scripts/test-messaging.sh --channel whatsapp

# Send test message
./scripts/test-messaging.sh --send-test
```

**Channels:**
- WhatsApp
- Discord
- Telegram
- Email

### 8. Test Report Generation

Generate comprehensive test reports:

```bash
# Generate HTML report
./scripts/generate-report.sh --format html

# Generate JSON report
./scripts/generate-report.sh --format json

# Generate markdown report
./scripts/generate-report.sh --format markdown

# Include all test history
./scripts/generate-report.sh --history
```

## Configuration

Edit `references/test-config.json` to customize test behavior:

```json
{
  "tools": {
    "timeout": 30,
    "retry": 2,
    "exclude": []
  },
  "apis": {
    "timeout": 10,
    "endpoints": {
      "brave": "https://api.search.brave.com",
      "resend": "https://api.resend.com"
    }
  },
  "browser": {
    "profiles": ["chrome", "openclaw"],
    "test_url": "https://example.com"
  },
  "messaging": {
    "test_recipient": "test@example.com",
    "channels": ["whatsapp", "discord"]
  },
  "scripts": {
    "directories": ["./scripts", "./skills/*/scripts"],
    "extensions": [".sh", ".py", ".js"]
  }
}
```

## Test Results

Test results are stored in `data/test-results/`:

- `latest.json` - Most recent test run results
- `history/` - Archived test results by date
- `screenshots/` - Visual test captures
- `logs/` - Detailed test logs

## Continuous Testing

Set up automated testing with cron:

```bash
# Add to crontab for daily tests
0 9 * * * cd /root/.openclaw/workspace/skills/tool-tester && ./scripts/run-all-tests.sh --quiet

# Weekly comprehensive tests
0 10 * * 1 cd /root/.openclaw/workspace/skills/tool-tester && ./scripts/run-all-tests.sh --comprehensive --report
```

## Troubleshooting

### Common Issues

**Tool Timeout:**
```bash
# Increase timeout
./scripts/test-tools.sh --timeout 60
```

**Browser Connection Failed:**
```bash
# Check browser status
openclaw gateway status

# Restart browser control
openclaw gateway restart
```

**API Authentication Error:**
```bash
# Check API keys
./scripts/validate-env.sh --check-keys

# Test specific API with verbose output
./scripts/test-apis.sh --api brave --verbose
```

### Debug Mode

Run tests with debug output:

```bash
DEBUG=1 ./scripts/test-tools.sh
VERBOSE=1 ./scripts/test-integration.sh
```

## Reference Files

- **[test-config.json](references/test-config.json)** - Test configuration
- **[test-matrix.md](references/test-matrix.md)** - Test coverage matrix
- **[api-endpoints.md](references/api-endpoints.md)** - API endpoint documentation
- **[troubleshooting.md](references/troubleshooting.md)** - Common issues and solutions

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed
- `2` - Configuration error
- `3` - Environment error
- `4` - Test script error
