#!/usr/bin/env node
/**
 * send-emails.js
 * Sends pending emails for a campaign
 */

const fs = require('fs');
const path = require('path');

function showHelp() {
  console.log(`
Usage: node send-emails.js [options]

Options:
  --campaign <name>   Campaign name (required)
  --dry-run           Show what would be sent without sending
  --step <number>     Send only specific step
  --path <path>       Campaigns path (default: ./campaigns)
  --leads <path>      Leads database path (default: ./leads.json)
  --resend-key <key>  Resend API key (or set RESEND_API_KEY env var)
  --help              Show this help

Examples:
  node send-emails.js --campaign "welcome" --dry-run
  node send-emails.js --campaign "welcome"
`);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    path: './campaigns',
    leads: './leads.json',
    dryRun: false
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--campaign':
        options.campaign = args[++i];
        break;
      case '--dry-run':
        options.dryRun = true;
        break;
      case '--step':
        options.step = parseInt(args[++i]);
        break;
      case '--path':
        options.path = args[++i];
        break;
      case '--leads':
        options.leads = args[++i];
        break;
      case '--resend-key':
        options.resendKey = args[++i];
        break;
      case '--help':
        showHelp();
        process.exit(0);
        break;
    }
  }

  return options;
}

function loadLeads(leadsPath) {
  if (!fs.existsSync(leadsPath)) {
    return {};
  }
  return JSON.parse(fs.readFileSync(leadsPath, 'utf8'));
}

function saveLeads(leadsPath, leads) {
  fs.writeFileSync(leadsPath, JSON.stringify(leads, null, 2));
}

function loadCampaign(campaignPath, name) {
  const filePath = path.join(campaignPath, `${name}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Campaign "${name}" not found at ${filePath}`);
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function saveCampaign(campaignPath, campaign) {
  const filePath = path.join(campaignPath, `${campaign.name}.json`);
  campaign.updatedAt = new Date().toISOString();
  fs.writeFileSync(filePath, JSON.stringify(campaign, null, 2));
}

function loadTemplate(templatePath, templateName, format = 'html') {
  const filePath = path.join(templatePath, `${templateName}.${format}`);
  if (!fs.existsSync(filePath)) {
    // Try default template
    const defaultPath = path.join(templatePath, `default.${format}`);
    if (fs.existsSync(defaultPath)) {
      return fs.readFileSync(defaultPath, 'utf8');
    }
    return null;
  }
  return fs.readFileSync(filePath, 'utf8');
}

function renderTemplate(template, variables) {
  let result = template;
  for (const [key, value] of Object.entries(variables)) {
    const regex = new RegExp(`{{${key}}}`, 'g');
    result = result.replace(regex, value || '');
  }
  return result;
}

function getPendingEmails(leads, campaignName, campaign) {
  const pending = [];
  const now = new Date();

  for (const [email, lead] of Object.entries(leads)) {
    const campaignState = lead.campaigns[campaignName];
    if (!campaignState || campaignState.status !== 'active' || campaignState.unsubscribed) {
      continue;
    }

    const currentStep = campaignState.currentStep;
    const nextEmail = campaign.emails[currentStep];

    if (!nextEmail) {
      continue; // Sequence complete
    }

    // Check if it's time to send
    if (campaignState.lastEmailSent) {
      const lastSent = new Date(campaignState.lastEmailSent);
      const nextSend = new Date(lastSent);
      nextSend.setDate(nextSend.getDate() + nextEmail.delayDays);
      
      if (now < nextSend) {
        continue; // Not time yet
      }
    }

    pending.push({
      email,
      lead,
      step: currentStep,
      emailConfig: nextEmail
    });
  }

  return pending;
}

async function sendEmail(options, to, subject, html, text, campaign) {
  if (options.dryRun) {
    return { success: true, id: 'dry-run-' + Date.now() };
  }

  const apiKey = options.resendKey || process.env.RESEND_API_KEY;
  if (!apiKey) {
    throw new Error('Resend API key required. Set RESEND_API_KEY or use --resend-key');
  }

  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: `${campaign.settings.fromName} <${campaign.settings.fromEmail}>`,
        to: [to],
        reply_to: campaign.settings.replyTo,
        subject: subject,
        html: html,
        text: text
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Resend API error: ${error}`);
    }

    const result = await response.json();
    return { success: true, id: result.id };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function main() {
  const options = parseArgs();

  if (!options.campaign) {
    console.error('Error: --campaign is required');
    showHelp();
    process.exit(1);
  }

  const campaignPath = path.resolve(options.path);
  const leadsPath = path.resolve(options.leads);
  const templatePath = path.join(__dirname, '..', 'assets', 'templates');

  // Load data
  const campaign = loadCampaign(campaignPath, options.campaign);
  const leads = loadLeads(leadsPath);

  // Get pending emails
  let pending = getPendingEmails(leads, options.campaign, campaign);

  // Filter by step if specified
  if (options.step !== undefined) {
    pending = pending.filter(p => p.step + 1 === options.step);
  }

  console.log(`Found ${pending.length} pending emails for campaign "${options.campaign}"`);

  if (pending.length === 0) {
    console.log('No emails to send.');
    return;
  }

  if (options.dryRun) {
    console.log('\n--- DRY RUN ---\n');
  }

  let sent = 0;
  let failed = 0;

  for (const item of pending) {
    const { email, lead, step, emailConfig } = item;
    
    // Load templates
    const htmlTemplate = loadTemplate(templatePath, emailConfig.template, 'html');
    const textTemplate = loadTemplate(templatePath, emailConfig.template, 'txt');

    if (!htmlTemplate) {
      console.error(`Template not found: ${emailConfig.template}`);
      failed++;
      continue;
    }

    // Prepare variables
    const variables = {
      firstName: lead.firstName || 'There',
      email: lead.email,
      companyName: 'FedBuyOut',
      unsubscribeUrl: `https://fedbuyout.com/unsubscribe?email=${encodeURIComponent(email)}`,
      consultationUrl: 'https://fedbuyout.com/consultation',
      phoneNumber: '1-800-FED-BUYOUT'
    };

    const html = renderTemplate(htmlTemplate, variables);
    const text = textTemplate ? renderTemplate(textTemplate, variables) : '';

    console.log(`Sending to ${email}: "${emailConfig.subject}"`);

    const result = await sendEmail(options, email, emailConfig.subject, html, text, campaign);

    if (result.success) {
      sent++;
      
      if (!options.dryRun) {
        // Update lead state
        leads[email].campaigns[options.campaign].currentStep = step + 1;
        leads[email].campaigns[options.campaign].lastEmailSent = new Date().toISOString();
        leads[email].campaigns[options.campaign].emailsSent.push(emailConfig.id);
        
        // Update campaign stats
        campaign.stats.emailsSent++;
      }
    } else {
      failed++;
      console.error(`  Failed: ${result.error}`);
    }
  }

  if (!options.dryRun) {
    saveLeads(leadsPath, leads);
    saveCampaign(campaignPath, campaign);
  }

  console.log(`\n✓ Sent: ${sent}, Failed: ${failed}`);
  if (options.dryRun) {
    console.log('This was a dry run. Use without --dry-run to actually send.');
  }
}

main().catch(console.error);
