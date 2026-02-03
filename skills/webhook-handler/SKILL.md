---
name: webhook-handler
description: Receive and process external webhooks, verify signatures, and route events.
version: 1.0.0
author: OpenClaw
---

# Webhook Handler Skill

This skill provides a standalone Express server to listen for, verify, and route external webhooks.

## Capabilities
- Start/stop a webhook listener on a configurable port.
- Verify signatures (HMAC-SHA256, etc.) to ensure security.
- Log incoming payloads for debugging.
- Route events to other skills or trigger agent actions.

## Usage

### Start Listener
To start the webhook server:
```bash
node skills/webhook-handler/scripts/server.js --port 3000 --secret YOUR_SECRET
```

### Stop Listener
Find the process ID and kill it (or use a process manager like PM2 if available).

## Configuration
- **Port**: Default 3000
- **Secret**: Shared secret for HMAC verification (x-hub-signature-256 or similar)
- **Route Map**: Defined in `scripts/routes.json` (optional) or handled dynamically in `server.js`.

## Scripts
- `scripts/server.js`: Main Express server entry point.
- `scripts/verify.js`: Middleware for signature verification.
- `scripts/logger.js`: Simple file-based logger.
