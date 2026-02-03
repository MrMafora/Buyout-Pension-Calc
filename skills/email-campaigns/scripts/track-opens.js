#!/usr/bin/env node
/**
 * track-opens.js
 * Tracks email opens and generates reports
 */

const fs = require('fs');
const path = require('path');

function showHelp() {
  console.log(`
Usage: node track-opens.js [options]

Options:
  --campaign <name>   Campaign name (required for --report)
  --report            Generate open/click report
  --pixel             Generate tracking pixel HTML (for embedding)
  --email <email>     Email address (for pixel generation)
  --campaign-id <id>  Campaign ID (for pixel generation)
  --path <path>       Campaigns path (default: ./campaigns)
  --leads <path>      Leads database path (default: ./leads.json)
  --help              Show this help

Examples:
  node track-opens.js --campaign "welcome" --report
  node track-opens.js --pixel --email "test@example.com" --campaign-id "welcome"
`);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    path: './campaigns',
    leads: './leads.json'
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--campaign':
        options.campaign = args[++i];
        break;
      case '--report':
        options.report = true;
        break;
      case '--pixel':
        options.pixel = true;
        break;
      case '--email':
        options.email = args[++i];
        break;
      case '--campaign-id':
        options.campaignId = args[++i];
        break;
      case '--path':
        options.path = args[++i];
        break;
      case '--leads':
        options.leads = args[++i];
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

function loadCampaign(campaignPath, name) {
  const filePath = path.join(campaignPath, `${name}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Campaign "${name}" not found at ${filePath}`);
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function generateTrackingPixel(email, campaignId) {
  // In production, this would be a URL to your tracking endpoint
  // For now, we generate a placeholder that can be replaced
  const encodedEmail = Buffer.from(email).toString('base64');
  const trackingUrl = `https://fedbuyout.com/track?c=${campaignId}&e=${encodedEmail}&t=open`;
  
  return `<img src="${trackingUrl}" width="1" height="1" alt="" style="display:block;width:1px;height:1px;">`;
}

function generateReport(options) {
  const campaignPath = path.resolve(options.path);
  const leadsPath = path.resolve(options.leads);
  
  const campaign = loadCampaign(campaignPath, options.campaign);
  const leads = loadLeads(leadsPath);
  
  console.log(`\nCampaign Report: ${options.campaign}`);
  console.log('='.repeat(60));
  
  // Overall stats
  const totalLeads = Object.keys(leads).filter(email => 
    leads[email].campaigns && leads[email].campaigns[options.campaign]
  ).length;
  
  console.log(`\nOverall Statistics:`);
  console.log(`  Total Leads: ${totalLeads}`);
  console.log(`  Emails Sent: ${campaign.stats.emailsSent}`);
  console.log(`  Emails Opened: ${campaign.stats.emailsOpened}`);
  console.log(`  Links Clicked: ${campaign.stats.linksClicked}`);
  console.log(`  Unsubscribes: ${campaign.stats.unsubscribes}`);
  console.log(`  Bounces: ${campaign.stats.bounces}`);
  
  // Calculate rates
  const openRate = campaign.stats.emailsSent > 0
    ? ((campaign.stats.emailsOpened / campaign.stats.emailsSent) * 100).toFixed(2)
    : 0;
  const clickRate = campaign.stats.emailsSent > 0
    ? ((campaign.stats.linksClicked / campaign.stats.emailsSent) * 100).toFixed(2)
  : 0;
  const ctr = campaign.stats.emailsOpened > 0
    ? ((campaign.stats.linksClicked / campaign.stats.emailsOpened) * 100).toFixed(2)
    : 0;
  
  console.log(`\nEngagement Rates:`);
  console.log(`  Open Rate: ${openRate}%`);
  console.log(`  Click Rate: ${clickRate}%`);
  console.log(`  Click-to-Open Rate: ${ctr}%`);
  
  // Per-email stats
  console.log(`\nPer-Email Performance:`);
  console.log('-'.repeat(60));
  
  for (const email of campaign.emails) {
    const emailStats = { sent: 0, opened: 0, clicked: 0 };
    
    for (const leadEmail of Object.keys(leads)) {
      const lead = leads[leadEmail];
      const campaignState = lead.campaigns?.[options.campaign];
      
      if (campaignState && campaignState.emailsSent.includes(email.id)) {
        emailStats.sent++;
        if (campaignState.emailsOpened.includes(email.id)) {
          emailStats.opened++;
        }
        if (campaignState.linksClicked.includes(email.id)) {
          emailStats.clicked++;
        }
      }
    }
    
    const eOpenRate = emailStats.sent > 0
      ? ((emailStats.opened / emailStats.sent) * 100).toFixed(2)
      : 0;
    const eClickRate = emailStats.sent > 0
      ? ((emailStats.clicked / emailStats.sent) * 100).toFixed(2)
      : 0;
    
    console.log(`\n  Email #${email.id}: ${email.subject}`);
    console.log(`    Sent: ${emailStats.sent} | Opened: ${emailStats.opened} (${eOpenRate}%) | Clicked: ${emailStats.clicked} (${eClickRate}%)`);
  }
  
  // Engagement segments
  console.log(`\n\nLead Segments:`);
  const segments = {
    engaged: 0,
    opened: 0,
    noOpen: 0,
    unsubscribed: 0
  };
  
  for (const leadEmail of Object.keys(leads)) {
    const lead = leads[leadEmail];
    const campaignState = lead.campaigns?.[options.campaign];
    
    if (!campaignState) continue;
    
    if (campaignState.unsubscribed) {
      segments.unsubscribed++;
    } else if (campaignState.linksClicked.length > 0) {
      segments.engaged++;
    } else if (campaignState.emailsOpened.length > 0) {
      segments.opened++;
    } else if (campaignState.emailsSent.length > 0) {
      segments.noOpen++;
    }
  }
  
  console.log(`  Highly Engaged (clicked): ${segments.engaged}`);
  console.log(`  Opened (no clicks): ${segments.opened}`);
  console.log(`  No Opens: ${segments.noOpen}`);
  console.log(`  Unsubscribed: ${segments.unsubscribed}`);
}

function main() {
  const options = parseArgs();
  
  if (options.report) {
    if (!options.campaign) {
      console.error('Error: --campaign is required for report');
      process.exit(1);
    }
    generateReport(options);
  } else if (options.pixel) {
    if (!options.email || !options.campaignId) {
      console.error('Error: --email and --campaign-id required for pixel');
      process.exit(1);
    }
    const pixel = generateTrackingPixel(options.email, options.campaignId);
    console.log('Tracking Pixel HTML:');
    console.log(pixel);
  } else {
    console.error('Error: Must specify --report or --pixel');
    showHelp();
    process.exit(1);
  }
}

main();
