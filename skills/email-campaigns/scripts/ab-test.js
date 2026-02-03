#!/usr/bin/env node
/**
 * ab-test.js
 * Manages A/B test campaigns
 */

const fs = require('fs');
const path = require('path');

function showHelp() {
  console.log(`
Usage: node ab-test.js [options]

Options:
  --campaign <name>    Campaign name (required)
  --create             Create new A/B test
  --variants <n>       Number of variants (2-4)
  --winner <variant>   Declare winner and end test
  --stats              Show test statistics
  --path <path>        Campaigns path (default: ./campaigns)
  --help               Show this help

Examples:
  node ab-test.js --campaign "welcome" --create --variants 2
  node ab-test.js --campaign "welcome" --stats
  node ab-test.js --campaign "welcome" --winner A
`);
}

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    path: './campaigns',
    variants: 2
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--campaign':
        options.campaign = args[++i];
        break;
      case '--create':
        options.create = true;
        break;
      case '--variants':
        options.variants = parseInt(args[++i]);
        break;
      case '--winner':
        options.winner = args[++i];
        break;
      case '--stats':
        options.stats = true;
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

function generateVariants(count) {
  const variants = [];
  const letters = ['A', 'B', 'C', 'D'];
  
  for (let i = 0; i < count && i < 4; i++) {
    variants.push({
      id: letters[i],
      name: `Variant ${letters[i]}`,
      subjectLine: '',
      template: '',
      trafficPercent: Math.floor(100 / count),
      stats: {
        sent: 0,
        opened: 0,
        clicked: 0,
        converted: 0
      }
    });
  }
  
  return variants;
}

function calculateStats(variant) {
  const openRate = variant.stats.sent > 0 
    ? ((variant.stats.opened / variant.stats.sent) * 100).toFixed(2)
    : 0;
  const clickRate = variant.stats.sent > 0
    ? ((variant.stats.clicked / variant.stats.sent) * 100).toFixed(2)
    : 0;
  const ctr = variant.stats.opened > 0
    ? ((variant.stats.clicked / variant.stats.opened) * 100).toFixed(2)
    : 0;
  
  return { openRate, clickRate, ctr };
}

function createABTest(options) {
  const campaignPath = path.resolve(options.path);
  const campaign = loadCampaign(campaignPath, options.campaign);
  
  if (campaign.settings.abTest.enabled) {
    console.error(`Campaign "${options.campaign}" already has an active A/B test`);
    process.exit(1);
  }
  
  campaign.settings.abTest = {
    enabled: true,
    startedAt: new Date().toISOString(),
    variants: generateVariants(options.variants),
    winner: null,
    endedAt: null
  };
  
  saveCampaign(campaignPath, campaign);
  
  console.log(`✓ A/B test created for campaign "${options.campaign}"`);
  console.log(`  Variants: ${options.variants}`);
  console.log(`  Traffic split: ${Math.floor(100 / options.variants)}% each`);
  console.log(`\nNext steps:`);
  console.log(`  1. Edit subject lines in campaign config`);
  console.log(`  2. Run campaign normally - traffic will split automatically`);
  console.log(`  3. Monitor with: node ab-test.js --campaign "${options.campaign}" --stats`);
  console.log(`  4. End test with: node ab-test.js --campaign "${options.campaign}" --winner A`);
}

function showStats(options) {
  const campaignPath = path.resolve(options.path);
  const campaign = loadCampaign(campaignPath, options.campaign);
  
  if (!campaign.settings.abTest.enabled) {
    console.log(`Campaign "${options.campaign}" has no active A/B test`);
    return;
  }
  
  const abTest = campaign.settings.abTest;
  
  console.log(`\nA/B Test: ${options.campaign}`);
  console.log(`Started: ${new Date(abTest.startedAt).toLocaleString()}`);
  console.log(`Status: ${abTest.winner ? 'ENDED' : 'ACTIVE'}`);
  if (abTest.winner) {
    console.log(`Winner: Variant ${abTest.winner}`);
  }
  console.log('');
  
  console.log('Variant Performance:');
  console.log('-'.repeat(80));
  console.log(`${'Variant'.padEnd(10)} ${'Sent'.padEnd(8)} ${'Opens'.padEnd(8)} ${'Clicks'.padEnd(8)} ${'Open %'.padEnd(10)} ${'Click %'.padEnd(10)} ${'CTR %'.padEnd(10)}`);
  console.log('-'.repeat(80));
  
  for (const variant of abTest.variants) {
    const stats = calculateStats(variant);
    const marker = abTest.winner === variant.id ? ' ★' : '';
    console.log(
      `${(variant.id + marker).padEnd(10)} ` +
      `${String(variant.stats.sent).padEnd(8)} ` +
      `${String(variant.stats.opened).padEnd(8)} ` +
      `${String(variant.stats.clicked).padEnd(8)} ` +
      `${stats.openRate.padEnd(10)} ` +
      `${stats.clickRate.padEnd(10)} ` +
      `${stats.ctr.padEnd(10)}`
    );
  }
  console.log('-'.repeat(80));
  
  // Find winner recommendation
  if (!abTest.winner) {
    let bestVariant = abTest.variants[0];
    let bestRate = 0;
    
    for (const variant of abTest.variants) {
      const rate = variant.stats.opened / (variant.stats.sent || 1);
      if (rate > bestRate) {
        bestRate = rate;
        bestVariant = variant;
      }
    }
    
    console.log(`\nRecommendation: Variant ${bestVariant.id} is performing best`);
    console.log(`Significance: ${bestVariant.stats.sent >= 100 ? 'Sufficient data' : 'Need more data (min 100 per variant)'}`);
  }
}

function declareWinner(options) {
  const campaignPath = path.resolve(options.path);
  const campaign = loadCampaign(campaignPath, options.campaign);
  
  if (!campaign.settings.abTest.enabled) {
    console.error(`Campaign "${options.campaign}" has no active A/B test`);
    process.exit(1);
  }
  
  const variantIds = campaign.settings.abTest.variants.map(v => v.id);
  if (!variantIds.includes(options.winner)) {
    console.error(`Invalid variant: ${options.winner}. Options: ${variantIds.join(', ')}`);
    process.exit(1);
  }
  
  campaign.settings.abTest.winner = options.winner;
  campaign.settings.abTest.endedAt = new Date().toISOString();
  
  saveCampaign(campaignPath, campaign);
  
  console.log(`✓ Winner declared: Variant ${options.winner}`);
  console.log(`  Campaign will now use the winning variant for all future sends`);
  
  // Show final stats
  showStats(options);
}

function main() {
  const options = parseArgs();
  
  if (!options.campaign) {
    console.error('Error: --campaign is required');
    showHelp();
    process.exit(1);
  }
  
  if (options.create) {
    createABTest(options);
  } else if (options.stats) {
    showStats(options);
  } else if (options.winner) {
    declareWinner(options);
  } else {
    console.error('Error: Must specify --create, --stats, or --winner');
    showHelp();
    process.exit(1);
  }
}

main();
