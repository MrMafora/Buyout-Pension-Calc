#!/usr/bin/env node
/**
 * add-to-sequence.js
 * Adds leads to an email campaign sequence
 */

const fs = require('fs');
const path = require('path');
const csv = require('csv-parse/sync');

function showHelp() {
  console.log(`
Usage: node add-to-sequence.js [options]

Options:
  --campaign <name>   Campaign name (required)
  --email <email>     Single email to add
  --file <path>       CSV file with leads (columns: email, firstName, lastName)
  --firstName <name>  First name (with --email)
  --lastName <name>   Last name (with --email)
  --path <path>       Campaigns path (default: ./campaigns)
  --leads <path>      Leads database path (default: ./leads.json)
  --help              Show this help

Examples:
  node add-to-sequence.js --campaign "welcome" --email "john@example.com" --firstName "John"
  node add-to-sequence.js --campaign "welcome" --file leads.csv
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
      case '--email':
        options.email = args[++i];
        break;
      case '--file':
        options.file = args[++i];
        break;
      case '--firstName':
        options.firstName = args[++i];
        break;
      case '--lastName':
        options.lastName = args[++i];
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

function parseCSV(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const records = csv.parse(content, {
    columns: true,
    skip_empty_lines: true
  });
  return records.map(r => ({
    email: r.email,
    firstName: r.firstName || r.first_name || r['First Name'] || '',
    lastName: r.lastName || r.last_name || r['Last Name'] || ''
  }));
}

function addLead(leads, email, firstName, lastName, campaignName) {
  const normalizedEmail = email.toLowerCase().trim();
  
  if (!leads[normalizedEmail]) {
    leads[normalizedEmail] = {
      email: normalizedEmail,
      firstName: firstName || '',
      lastName: lastName || '',
      joinedAt: new Date().toISOString(),
      source: 'manual',
      status: 'active',
      campaigns: {}
    };
  }

  if (!leads[normalizedEmail].campaigns[campaignName]) {
    leads[normalizedEmail].campaigns[campaignName] = {
      status: 'active',
      currentStep: 0,
      joinedAt: new Date().toISOString(),
      lastEmailSent: null,
      emailsSent: [],
      emailsOpened: [],
      linksClicked: [],
      unsubscribed: false
    };
    return true;
  }
  
  return false;
}

function main() {
  const options = parseArgs();

  if (!options.campaign) {
    console.error('Error: --campaign is required');
    showHelp();
    process.exit(1);
  }

  if (!options.email && !options.file) {
    console.error('Error: Either --email or --file is required');
    showHelp();
    process.exit(1);
  }

  const campaignPath = path.resolve(options.path);
  const leadsPath = path.resolve(options.leads);

  // Load campaign
  const campaign = loadCampaign(campaignPath, options.campaign);
  
  // Load leads database
  const leads = loadLeads(leadsPath);

  let added = 0;
  let skipped = 0;

  if (options.email) {
    // Add single lead
    const isNew = addLead(leads, options.email, options.firstName, options.lastName, options.campaign);
    if (isNew) {
      added++;
    } else {
      skipped++;
    }
  } else if (options.file) {
    // Add from CSV
    const records = parseCSV(options.file);
    for (const record of records) {
      const isNew = addLead(leads, record.email, record.firstName, record.lastName, options.campaign);
      if (isNew) {
        added++;
      } else {
        skipped++;
      }
    }
  }

  // Update campaign stats
  campaign.stats.leadsAdded += added;
  saveCampaign(campaignPath, campaign);
  
  // Save leads
  saveLeads(leadsPath, leads);

  console.log(`✓ Added ${added} leads to campaign "${options.campaign}"`);
  if (skipped > 0) {
    console.log(`  Skipped ${skipped} (already in campaign)`);
  }
  console.log(`  Total leads in campaign: ${campaign.stats.leadsAdded}`);
}

main();
