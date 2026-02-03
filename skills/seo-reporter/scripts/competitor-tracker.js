#!/usr/bin/env node
/**
 * Monitor competitor rankings for FedBuyOut keywords
 * Usage: node competitor-tracker.js [--domain "competitor.com"]
 */

const fs = require('fs');
const path = require('path');

// Load competitors from reference
const COMPETITORS_FILE = path.join(__dirname, '..', 'references', 'competitors.json');
const TARGET_KEYWORDS_FILE = path.join(__dirname, '..', 'references', 'target-keywords.json');

const DATA_DIR = path.join(__dirname, '..', 'data', 'competitors');

// Parse arguments
const args = process.argv.slice(2);
const specificDomain = args.find(arg => arg.startsWith('--domain='))?.split('=')[1] ||
                       (args[args.indexOf('--domain') + 1] || null);

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

/**
 * Load JSON file with fallback
 */
function loadJson(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return fallback;
  }
}

/**
 * Simulate fetching competitor rankings
 */
async function fetchCompetitorRankings(domain, keywords) {
  console.log(`\n🔍 Analyzing competitor: ${domain}`);
  
  const results = [];
  
  for (const keyword of keywords) {
    // Simulated: In production, use SerpAPI
    const position = Math.random() > 0.4 ? Math.floor(Math.random() * 30) + 1 : null;
    
    results.push({
      keyword,
      position,
      domain,
      url: position ? `https://${domain}/${keyword.replace(/\s+/g, '-')}` : null
    });
    
    await new Promise(r => setTimeout(r, 300));
  }
  
  return results;
}

/**
 * Compare FedBuyOut vs competitor
 */
function compareRankings(ourRankings, competitorRankings) {
  const comparisons = [];
  
  for (const our of ourRankings) {
    const theirs = competitorRankings.find(c => c.keyword === our.keyword);
    if (!theirs) continue;
    
    let status, advantage;
    if (!our.position && theirs.position) {
      status = 'BEHIND';
      advantage = theirs.position;
    } else if (our.position && !theirs.position) {
      status = 'AHEAD';
      advantage = our.position;
    } else if (our.position && theirs.position) {
      const diff = theirs.position - our.position;
      if (diff > 0) {
        status = 'AHEAD';
        advantage = diff;
      } else if (diff < 0) {
        status = 'BEHIND';
        advantage = Math.abs(diff);
      } else {
        status = 'TIED';
        advantage = 0;
      }
    } else {
      status = 'NEITHER';
      advantage = null;
    }
    
    comparisons.push({
      keyword: our.keyword,
      ourPosition: our.position,
      theirPosition: theirs.position,
      status,
      advantage
    });
  }
  
  return comparisons;
}

/**
 * Main competitor tracking function
 */
async function trackCompetitors() {
  const competitors = loadJson(COMPETITORS_FILE, { competitors: [] }).competitors;
  const keywordsData = loadJson(TARGET_KEYWORDS_FILE, { keywords: [] });
  const keywords = keywordsData.keywords.map(k => k.term);
  
  if (specificDomain) {
    competitors.length = 0;
    competitors.push({ domain: specificDomain, name: specificDomain });
  }
  
  console.log(`\n🏆 FedBuyOut Competitor Tracker`);
  console.log(`================================\n`);
  console.log(`Keywords: ${keywords.length}`);
  console.log(`Competitors: ${competitors.length}\n`);
  
  // Load our latest rankings
  const ourRankingsDir = path.join(__dirname, '..', 'data', 'rankings');
  const ourLatestFiles = fs.readdirSync(ourRankingsDir).filter(f => f.endsWith('.json')).sort().reverse();
  let ourRankings = [];
  
  if (ourLatestFiles.length > 0) {
    ourRankings = JSON.parse(fs.readFileSync(path.join(ourRankingsDir, ourLatestFiles[0]), 'utf8'));
  }
  
  const allResults = [];
  
  for (const competitor of competitors) {
    const rankings = await fetchCompetitorRankings(competitor.domain, keywords);
    
    const foundCount = rankings.filter(r => r.position).length;
    const avgPosition = rankings
      .filter(r => r.position)
      .reduce((sum, r) => sum + r.position, 0) / foundCount || 0;
    
    console.log(`  Rankings found: ${foundCount}/${keywords.length}`);
    console.log(`  Average position: ${avgPosition.toFixed(1)}`);
    
    // Compare with us
    if (ourRankings.length > 0) {
      const comparison = compareRankings(ourRankings, rankings);
      const ahead = comparison.filter(c => c.status === 'AHEAD').length;
      const behind = comparison.filter(c => c.status === 'BEHIND').length;
      const tied = comparison.filter(c => c.status === 'TIED').length;
      
      console.log(`  Comparison: Ahead ${ahead} | Behind ${behind} | Tied ${tied}`);
      
      // Show where we're behind
      const behindKeywords = comparison.filter(c => c.status === 'BEHIND');
      if (behindKeywords.length > 0) {
        console.log(`  ⚠️  Opportunities (we're behind):`);
        behindKeywords.slice(0, 5).forEach(k => {
          console.log(`     - "${k.keyword}": They're #${k.theirPosition}, we're ${k.ourPosition ? '#' + k.ourPosition : 'not ranked'}`);
        });
      }
    }
    
    allResults.push({
      competitor: competitor.name,
      domain: competitor.domain,
      rankings,
      checkedAt: new Date().toISOString()
    });
    
    console.log('');
  }
  
  // Save results
  const dateStr = new Date().toISOString().split('T')[0];
  const outputFile = path.join(DATA_DIR, `${dateStr}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(allResults, null, 2));
  
  console.log(`💾 Competitor data saved to: ${outputFile}\n`);
  
  return allResults;
}

// Run if called directly
if (require.main === module) {
  trackCompetitors().catch(console.error);
}

module.exports = { trackCompetitors };
