# API Endpoints

This document lists the API endpoints tested by the tool-tester skill.

## External APIs

### Brave Search API
- **Endpoint:** `https://api.search.brave.com`
- **Auth Type:** API Key
- **Environment Variable:** `BRAVE_API_KEY`
- **Test Method:** HTTP GET with API key
- **Expected Response:** 200 OK (or 401 if key not configured)

### Resend Email API
- **Endpoint:** `https://api.resend.com`
- **Auth Type:** API Key
- **Environment Variable:** `RESEND_API_KEY`
- **Test Method:** HTTP GET /domains
- **Expected Response:** 200 OK (or 401 if key not configured)

## Internal Services

### OpenClaw Gateway
- **Endpoint:** `http://localhost:3000`
- **Auth Type:** None
- **Test Method:** HTTP GET /status
- **Expected Response:** 200 OK
- **Notes:** Main gateway for tool execution

### Browser Control Server
- **Endpoint:** `http://localhost:9222`
- **Auth Type:** None
- **Test Method:** HTTP GET /json/version
- **Expected Response:** Chrome DevTools Protocol info
- **Notes:** Chrome/Chromium DevTools Protocol endpoint

## Adding New APIs

To add a new API endpoint to the test suite:

1. Edit `references/test-config.json`
2. Add endpoint to `apis.endpoints`:

```json
{
  "new_api": {
    "url": "https://api.example.com",
    "description": "Example API",
    "auth_type": "api_key|oauth|none",
    "env_var": "EXAMPLE_API_KEY"
  }
}
```

3. Update `scripts/test-apis.sh` with test logic if needed

## Health Check Endpoints

### Common Patterns

| Service | Health Endpoint | Expected Status |
|---------|-----------------|-----------------|
| REST API | `/health` or `/status` | 200 OK |
| GraphQL | `/graphql` with `{ __typename }` | 200 OK |
| WebSocket | Connect handshake | Connection OK |

## Troubleshooting

### Connection Refused
- Check if service is running
- Verify port configuration
- Check firewall rules

### Timeout
- Increase timeout in test config
- Check network connectivity
- Verify service responsiveness

### Authentication Errors
- Check API key is set
- Verify key permissions
- Check key expiration
