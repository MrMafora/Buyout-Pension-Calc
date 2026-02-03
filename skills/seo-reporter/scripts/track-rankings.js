#!/usr/bin/env node
/**
 * Track keyword rankings for FedBuyOut
 * Usage: node track-rankings.js [--keyword "keyword"]
 */

const fs = require('fs');
const path = require('path');

// Target keywords
const TARGET_KEYWORDS = [
  'federal buyout calculator',
  'VSIP calculator',
  'FERS buyout',
  'federal employee buyout',
  'early retirement calculator',
  'federal retirement buyout',
  'government buyout calculator',
  'VSIP federal',
  'voluntary separation incentive',
  'federal early out calculator'
];

// FedBuyOut domain
const DOMAIN = 'fedbuyout.com';

// Data storage paths
const DATA_DIR = path.join(__dirname, '..', 'data', 'rankings');

// Parse arguments
const args = process.argv.slice(2);
const specificKeyword = args.find(arg => arg.startsWith('--keyword='))?.split('=')[1] ||
                       (args[args.indexOf('--keyword') + 1] || null);

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

/**
 * Simulate fetching ranking (in production, use SerpAPI or similar)
 */
async function fetchRanking(keyword) {
  console.log(`🔍 Checking ranking for: "${keyword}"`);
  
  // In production, this would call SerpAPI or similar service
  // const response = await fetch(`https://serpapi.com/search?q=${encodeURIComponent(keyword)}&api_key=${process.env.SERPAPI_KEY}`);
  
  // Simulated ranking (random position between 1-50 or null if not found)
  // In production, this would parse actual search results
  const position = Math.random() > 0.3 ? Math.floor(Math.random() * 20) + 1 : null;
  
  return {
    keyword,
    position,
    domain: DOMAIN,
    checkedAt: new Date().toISOString(),
    url: position ? `https://${DOMAIN}` : null
  };
}

/**
 * Load previous ranking for comparison
 */
function getPreviousRanking(keyword) {
  const files = fs.readdirSync(DATA_DIR).filter(f => f.endsWith('.json')).sort().reverse();
  
  for (const file of files.slice(0, 7)) { // Check last 7 days
    const data = JSON.parse(fs.readFileSync(path.join(DATA_DIR, file), 'utf8'));
    const previous = data.find(r => r.keyword === keyword);
    if (previous) return previous;
  }
  return null;
}

/**
 * Calculate position change
 */
function calculateChange(current, previous) {
  if (!previous || previous.position === null) return current.position ? 'NEW' : 'N/A';
  if (current.position === null) return 'LOST';
  
  const change = previous.position - current.position;
  if (change > 0) return `+${change} ↑`;
  if (change < 0) return `${change} ↓`;
  return '→';
}

/**
 * Main tracking function
 */
async function trackRankings() {
  const keywordsToCheck = specificKeyword ? [specificKeyword] : TARGET_KEYWORDS;
  const results = [];
  
  console.log(`\n📊 FedBuyOut SEO Rank Tracker`);
  console.log(`==============================\n`);
  console.log(`Domain: ${DOMAIN}`);
  console.log(`Keywords: ${keywordsToCheck.length}`);
  console.log(`Date: ${new Date().toLocaleDateString()}\n`);
  
  for (const keyword of keywordsToCheck) {
    try {
      const result = await fetchRanking(keyword);
      const previous = getPreviousRanking(keyword);
      result.change = calculateChange(result, previous);
      results.push(result);
      
      const positionDisplay = result.position ? `#${result.position}` : 'Not found';
      const changeDisplay = result.change !== '→' ? ` (${result.change})` : '';
      console.log(`  ${keyword}: ${positionDisplay}${changeDisplay}`);
      
      // Rate limiting
      await new Promise(r => setTimeout(r, 500));
    } catch (error) {
      console.error(`  ❌ Error checking "${keyword}":`, error.message);
      results.push({
        keyword,
        error: error.message,
        checkedAt: new Date().toISOString()
      });
    }
  }
  
  // Save results
  const dateStr = new Date().toISOString().split('T')[0];
  const outputFile = path.join(DATA_DIR, `${dateStr}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
  
  // Summary
  const foundCount = results.filter(r => r.position).length;
  const avgPosition = results
    .filter(r => r.position)
    .reduce((sum, r) => sum + r.position, 0) / foundCount || 0;
  
  console.log(`\n📈 Summary`);
  console.log(`---------`);
  console.log(`Keywords tracked: ${results.length}`);
  console.log(`Rankings found: ${foundCount}`);
  console.log(`Average position: ${avgPosition.toFixed(1)}`);
  console.log(`\n💾 Results saved to: ${outputFile}\n`);
  
  return results;
}

// Run if called directly
if (require.main === module) {
  trackRankings().catch(console.error);
}

module.exports = { trackRankings, TARGET_KEYWORDS };
