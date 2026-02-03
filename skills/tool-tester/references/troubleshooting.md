# Troubleshooting Guide

Common issues and solutions when using the tool-tester skill.

## Test Failures

### Tool Timeout

**Symptom:** Test reports "timeout" or hangs

**Solutions:**
```bash
# Increase timeout for slow tools
./scripts/test-tools.sh --timeout 60

# Test specific tool with verbose output
./scripts/test-tools.sh --tool browser --verbose
```

### Browser Connection Failed

**Symptom:** Browser tests fail with connection error

**Solutions:**
```bash
# Check browser control server status
curl http://localhost:9222/json/version

# Check if browser is installed
which chromium || which google-chrome

# Check gateway status
openclaw gateway status

# Restart browser control
openclaw gateway restart
```

### API Authentication Error

**Symptom:** API tests fail with 401 or 403

**Solutions:**
```bash
# Check API keys are set
echo $BRAVE_API_KEY
echo $RESEND_API_KEY

# Test with verbose output
./scripts/test-apis.sh --api brave --verbose
```

### Script Syntax Errors

**Symptom:** Script tests report syntax errors

**Solutions:**
```bash
# Check specific script
bash -n /path/to/script.sh

# For Python scripts
python3 -m py_compile /path/to/script.py

# For Node scripts
node --check /path/to/script.js
```

## Environment Issues

### Missing Dependencies

**Symptom:** Environment validation fails

**Solutions:**
```bash
# Install common dependencies
apt-get update
apt-get install -y curl git python3 python3-pip

# Install optional tools
apt-get install -y chromium-browser ffmpeg
```

### Permission Denied

**Symptom:** Cannot write to workspace or temp directories

**Solutions:**
```bash
# Fix workspace permissions
chmod -R u+w /root/.openclaw/workspace

# Fix temp permissions
chmod 1777 /tmp
```

### Node.js Version

**Symptom:** Tests warn about Node.js version

**Solutions:**
```bash
# Check current version
node --version

# Update Node.js (if needed)
npm install -g n
n 18
```

## Integration Test Failures

### File Operations

**Symptom:** File read/write tests fail

**Solutions:**
```bash
# Check /tmp is writable
touch /tmp/test-write && rm /tmp/test-write

# Check workspace is accessible
ls /root/.openclaw/workspace
```

### Web Workflow

**Symptom:** Web fetch tests fail

**Solutions:**
```bash
# Check network connectivity
ping -c 1 google.com

# Check DNS resolution
nslookup example.com

# Test with curl
curl -I https://example.com
```

## Report Generation Issues

### Missing Results

**Symptom:** Report generation fails with "Input file not found"

**Solutions:**
```bash
# Run tests first
./scripts/run-all-tests.sh

# Check results exist
ls -la data/test-results/

# Generate report manually
./scripts/generate-report.sh --input data/test-results/latest.json
```

### Invalid JSON

**Symptom:** Python JSON parsing errors

**Solutions:**
```bash
# Validate JSON
python3 -m json.tool data/test-results/latest.json

# Regenerate results
rm data/test-results/latest.json
./scripts/run-all-tests.sh
```

## Getting Help

### Debug Mode

Run any test with debug output:
```bash
DEBUG=1 ./scripts/test-tools.sh
VERBOSE=1 ./scripts/test-integration.sh
```

### Check Logs

View detailed test logs:
```bash
ls -la data/test-results/logs/
cat data/test-results/logs/test-run-*.log
```

### Manual Tool Testing

Test tools directly:
```bash
# Test read tool
cat /root/.openclaw/workspace/AGENTS.md

# Test exec tool
uname -a

# Test web_search (via curl)
curl -s "https://api.search.brave.com/res/v1/web/search?q=test"
```

## Known Limitations

1. **Browser Tests:** Require browser control server to be running
2. **Messaging Tests:** May send real messages if not in dry-run mode
3. **API Tests:** Some tests require valid API keys
4. **Visual Tests:** Require display or virtual framebuffer (xvfb)

## Reporting Bugs

When reporting issues:
1. Run with `--verbose` flag
2. Include full log output
3. Specify OpenClaw version
4. Include environment details (OS, Node version)
