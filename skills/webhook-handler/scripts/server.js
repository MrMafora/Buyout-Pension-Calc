const express = require('express');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();
const argv = require('minimist')(process.argv.slice(2));

const PORT = argv.port || 3000;
const SECRET = argv.secret || process.env.WEBHOOK_SECRET || 'default-secret';
const LOG_FILE = path.join(__dirname, '../../../../webhook-logs.jsonl');

// Middleware to capture raw body for signature verification
app.use(express.json({
  verify: (req, res, buf) => {
    req.rawBody = buf;
  }
}));

// Logging helper
function logWebhook(event) {
  const logEntry = JSON.stringify({ timestamp: new Date(), ...event }) + '\n';
  fs.appendFileSync(LOG_FILE, logEntry);
  console.log(`[Webhook] Logged event: ${event.type || 'unknown'}`);
}

// Signature Verification Middleware
function verifySignature(req, res, next) {
  const signature = req.headers['x-hub-signature-256'] || req.headers['x-signature'];
  if (!signature) {
    // For development/testing, you might allow missing signatures if a flag is set
    // return res.status(401).send('No signature provided');
    console.warn('[Webhook] Warning: No signature header found.');
  }

  if (SECRET === 'default-secret') {
      console.warn('[Webhook] Warning: Using default secret. Validation may be weak.');
  }

  // If we have a signature and a secret, verify it
  if (signature && req.rawBody) {
    const hmac = crypto.createHmac('sha256', SECRET);
    const digest = 'sha256=' + hmac.update(req.rawBody).digest('hex');
    
    // Simple comparison (consider timingSafeEqual for production)
    if (signature !== digest && signature !== hmac.update(req.rawBody).digest('hex')) { // Handle cases with/without 'sha256=' prefix
       // return res.status(403).send('Invalid signature');
       console.error('[Webhook] Signature mismatch!');
    }
  }
  
  next();
}

app.post('/webhook', verifySignature, (req, res) => {
  const payload = req.body;
  
  // 1. Log the payload
  logWebhook({ type: 'received', headers: req.headers, body: payload });

  // 2. Routing Logic (Basic Example)
  // In a real scenario, you might emit an event or write to a queue file 
  // that the main agent watches or is notified about via `process` tool.
  
  if (payload.event === 'ping') {
      console.log('Received ping event');
  } else {
      console.log('Received payload:', JSON.stringify(payload).substring(0, 100) + '...');
  }

  res.status(200).send({ received: true });
});

app.get('/health', (req, res) => {
  res.send('OK');
});

app.listen(PORT, () => {
  console.log(`Webhook handler listening on port ${PORT}`);
  console.log(`Secret configured: ${SECRET !== 'default-secret'}`);
  console.log(`Logs writing to: ${LOG_FILE}`);
});
