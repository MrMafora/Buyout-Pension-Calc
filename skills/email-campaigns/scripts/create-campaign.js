#!/usr/bin/env node
/**
 * create-campaign.js
 * Creates a new email campaign configuration
 */

const fs = require('fs');
const path = require('path');

function showHelp() {
  console.log(`
Usage: node create-campaign.js [options]

Options:
  --name <name>      Campaign name (required)
  --type <type>      Campaign type: welcome|drip|reengagement (required)
  --path <path>      Output path (default: ./campaigns)
  --help             Show this help

Examples:
  node create-campaign.js --name "welcome-new" --type welcome
  node create-campaign.js --name "educational-series" --type drip
`);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    path: './campaigns'
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--name':
        options.name = args[++i];
        break;
      case '--type':
        options.type = args[++i];
        break;
      case '--path':
        options.path = args[++i];
        break;
      case '--help':
        showHelp();
        process.exit(0);
        break;
    }
  }

  return options;
}

function getDefaultEmails(type) {
  const configs = {
    welcome: [
      { id: 1, subject: "Welcome to FedBuyOut - Here's What to Expect", template: "welcome", delayDays: 0, sendTime: "09:00" },
      { id: 2, subject: "How FedBuyOut Helps Federal Employees", template: "educational", delayDays: 2, sendTime: "09:00" },
      { id: 3, subject: "Success Stories from Federal Pension Buyouts", template: "welcome", delayDays: 5, sendTime: "09:00" }
    ],
    drip: [
      { id: 1, subject: "Understanding Your Pension Options", template: "educational", delayDays: 0, sendTime: "09:00" },
      { id: 2, subject: "The True Cost of Waiting", template: "educational", delayDays: 3, sendTime: "09:00" },
      { id: 3, subject: "Buyout vs. Monthly Payments: What's Right for You?", template: "educational", delayDays: 6, sendTime: "09:00" },
      { id: 4, subject: "Tax Implications of Pension Buyouts Explained", template: "educational", delayDays: 9, sendTime: "09:00" },
      { id: 5, subject: "Ready to Discuss Your Options?", template: "welcome", delayDays: 12, sendTime: "09:00" }
    ],
    reengagement: [
      { id: 1, subject: "We Miss You at FedBuyOut", template: "reengagement", delayDays: 0, sendTime: "09:00" },
      { id: 2, subject: "What's Changed in Pension Buyouts", template: "reengagement", delayDays: 3, sendTime: "09:00" },
      { id: 3, subject: "Final Notice: Your Pension Consultation", template: "reengagement", delayDays: 7, sendTime: "09:00" }
    ]
  };

  return configs[type] || configs.welcome;
}

function createCampaign(options) {
  if (!options.name || !options.type) {
    console.error('Error: --name and --type are required');
    showHelp();
    process.exit(1);
  }

  const validTypes = ['welcome', 'drip', 'reengagement'];
  if (!validTypes.includes(options.type)) {
    console.error(`Error: type must be one of: ${validTypes.join(', ')}`);
    process.exit(1);
  }

  const campaignDir = path.resolve(options.path);
  if (!fs.existsSync(campaignDir)) {
    fs.mkdirSync(campaignDir, { recursive: true });
  }

  const campaignFile = path.join(campaignDir, `${options.name}.json`);
  
  if (fs.existsSync(campaignFile)) {
    console.error(`Error: Campaign "${options.name}" already exists at ${campaignFile}`);
    process.exit(1);
  }

  const campaign = {
    name: options.name,
    type: options.type,
    status: 'draft',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    emails: getDefaultEmails(options.type),
    settings: {
      fromName: 'FedBuyOut Team',
      fromEmail: 'support@fedbuyout.com',
      replyTo: 'support@fedbuyout.com',
      trackOpens: true,
      trackClicks: true,
      abTest: {
        enabled: false,
        variants: []
      }
    },
    stats: {
      leadsAdded: 0,
      emailsSent: 0,
      emailsOpened: 0,
      linksClicked: 0,
      unsubscribes: 0,
      bounces: 0
    }
  };

  fs.writeFileSync(campaignFile, JSON.stringify(campaign, null, 2));
  
  console.log(`✓ Campaign "${options.name}" created successfully`);
  console.log(`  Location: ${campaignFile}`);
  console.log(`  Type: ${options.type}`);
  console.log(`  Emails: ${campaign.emails.length}`);
  console.log(`\nNext steps:`);
  console.log(`  1. Review and customize the campaign in ${campaignFile}`);
  console.log(`  2. Add leads: node scripts/add-to-sequence.js --campaign "${options.name}" --email "test@example.com"`);
  console.log(`  3. Test send: node scripts/send-emails.js --campaign "${options.name}" --dry-run`);
}

const options = parseArgs();
createCampaign(options);
