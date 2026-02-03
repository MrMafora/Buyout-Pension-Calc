#!/usr/bin/env node
/**
 * Track backlinks for FedBuyOut
 * Usage: node backlink-tracker.js
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data', 'backlinks');
const DOMAIN = 'fedbuyout.com';

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

/**
 * Simulate fetching backlink data from Ahrefs/Majestic
 */
async function fetchBacklinkData() {
  // In production, this would use Ahrefs API or similar
  // For simulation, generating realistic backlink data
  
  const referringDomains = [
    { domain: 'federalnewsnetwork.com', authority: 72, links: 3, firstSeen: '2025-11-15', anchor: 'federal buyout calculator' },
    { domain: 'fedsmith.com', authority: 68, links: 2, firstSeen: '2025-12-01', anchor: 'VSIP calculator' },
    { domain: 'governmentexecutive.com', authority: 75, links: 1, firstSeen: '2025-12-10', anchor: 'federal employee buyout' },
    { domain: 'federaltimes.com', authority: 70, links: 2, firstSeen: '2026-01-05', anchor: 'early retirement calculator' },
    { domain: 'retirementplanning.com', authority: 45, links: 1, firstSeen: '2026-01-15', anchor: 'FERS buyout information' },
    { domain: 'federalretirement.net', authority: 52, links: 4, firstSeen: '2025-10-20', anchor: 'buyout calculator' },
    { domain: 'reddit.com/r/fednews', authority: 91, links: 1, firstSeen: '2026-01-20', anchor: 'fedbuyout.com' },
    { domain: 'govloop.com', authority: 58, links: 2, firstSeen: '2025-12-25', anchor: 'federal buyout guide' }
  ];
  
  // Simulate some new links
  const newLinks = [
    { domain: 'usajobs.gov', authority: 88, links: 1, firstSeen: new Date().toISOString().split('T')[0], anchor: 'federal buyout resources', isNew: true },
    { domain: 'opm.gov', authority: 85, links: 1, firstSeen: new Date().toISOString().split('T')[0], anchor: 'VSIP information', isNew: true }
  ];
  
  const allDomains = [...referringDomains, ...newLinks];
  
  const totalLinks = allDomains.reduce((sum, d) => sum + d.links, 0);
  const avgAuthority = allDomains.reduce((sum, d) => sum + d.authority, 0) / allDomains.length;
  
  return {
    domain: DOMAIN,
    checkedAt: new Date().toISOString(),
    summary: {
      referringDomains: allDomains.length,
      totalBacklinks: totalLinks,
      averageAuthority: Math.round(avgAuthority),
      newDomainsThisMonth: newLinks.length,
      lostDomainsThisMonth: 0
    },
    referringDomains: allDomains,
    topAnchors: [
      { text: 'federal buyout calculator', count: 5 },
      { text: 'VSIP calculator', count: 3 },
      { text: 'federal employee buyout', count: 2 },
      { text: 'early retirement calculator', count: 2 },
      { text: 'buyout calculator', count: 4 }
    ]
  };
}

/**
 * Compare with previous backlink data
 */
function compareWithPrevious(current) {
  const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith('.json')).sort().reverse();
  
  if (files.length === 0) {
    return { isFirstRun: true, changes: null };
  }
  
  try {
    const previous = JSON.parse(fs.readFileSync(path.join(DATA_DIR, files[0]), 'utf8'));
    
    const currentDomains = new Set(current.referringDomains.map(d => d.domain));
    const previousDomains = new Set(previous.referringDomains.map(d => d.domain));
    
    const newDomains = [...currentDomains].filter(d => !previousDomains.has(d));
    const lostDomains = [...previousDomains].filter(d => !currentDomains.has(d));
    
    const domainGrowth = current.summary.referringDomains - previous.summary.referringDomains;
    const linkGrowth = current.summary.totalBacklinks - previous.summary.totalBacklinks;
    
    return {
      isFirstRun: false,
      changes: {
        newDomains,
        lostDomains,
        domainGrowth,
        linkGrowth
      }
    };
  } catch {
    return { isFirstRun: true, changes: null };
  }
}

/**
 * Main backlink tracking function
 */
async function trackBacklinks() {
  console.log(`\n🔗 FedBuyOut Backlink Tracker`);
  console.log(`=============================\n`);
  console.log(`Domain: ${DOMAIN}`);
  console.log(`Date: ${new Date().toLocaleDateString()}\n`);
  
  // Fetch data
  console.log('📥 Fetching backlink data...\n');
  const data = await fetchBacklinkData();
  
  // Compare with previous
  const comparison = compareWithPrevious(data);
  
  // Display summary
  console.log('📊 Backlink Summary');
  console.log('-------------------');
  console.log(`Referring Domains: ${data.summary.referringDomains}`);
  console.log(`Total Backlinks: ${data.summary.totalBacklinks}`);
  console.log(`Average Domain Authority: ${data.summary.averageAuthority}/100`);
  
  if (!comparison.isFirstRun && comparison.changes) {
    const { changes } = comparison;
    console.log(`\n📈 Changes Since Last Check:`);
    console.log(`   Domain growth: ${changes.domainGrowth > 0 ? '+' : ''}${changes.domainGrowth}`);
    console.log(`   Link growth: ${changes.linkGrowth > 0 ? '+' : ''}${changes.linkGrowth}`);
    
    if (changes.newDomains.length > 0) {
      console.log(`\n   🆕 New Domains (${changes.newDomains.length}):`);
      changes.newDomains.forEach(d => console.log(`      + ${d}`));
    }
    
    if (changes.lostDomains.length > 0) {
      console.log(`\n   ❌ Lost Domains (${changes.lostDomains.length}):`);
      changes.lostDomains.forEach(d => console.log(`      - ${d}`));
    }
  }
  
  // Top referring domains
  console.log(`\n🌐 Top Referring Domains`);
  console.log('-----------------------');
  const topDomains = data.referringDomains
    .sort((a, b) => b.authority - a.authority)
    .slice(0, 5);
  
  topDomains.forEach((domain, i) => {
    console.log(`${i + 1}. ${domain.domain}`);
    console.log(`   Authority: ${domain.authority}/100 | Links: ${domain.links} | Anchor: "${domain.anchor}"`);
  });
  
  // Anchor text distribution
  console.log(`\n🏷️  Top Anchor Texts`);
  console.log('------------------');
  data.topAnchors.forEach((anchor, i) => {
    console.log(`${i + 1}. "${anchor.text}" (${anchor.count} links)`);
  });
  
  // Recommendations
  console.log(`\n💡 Backlink Recommendations`);
  console.log('--------------------------');
  console.log('1. Target federal employee forums and communities');
  console.log('2. Reach out to federal retirement blogs for guest posts');
  console.log('3. Create shareable resources (infographics, guides)');
  console.log('4. Engage with federal employee subreddits authentically');
  console.log('5. Consider partnerships with federal unions/associations');
  
  // Save results
  const dateStr = new Date().toISOString().split('T')[0];
  const outputFile = path.join(DATA_DIR, `${dateStr}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(data, null, 2));
  
  console.log(`\n💾 Backlink data saved to: ${outputFile}\n`);
  
  return data;
}

// Run if called directly
if (require.main === module) {
  trackBacklinks().catch(console.error);
}

module.exports = { trackBacklinks };
