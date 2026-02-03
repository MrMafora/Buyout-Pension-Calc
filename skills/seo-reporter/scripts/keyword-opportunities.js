#!/usr/bin/env node
/**
 * Find keyword opportunities for FedBuyOut
 * Usage: node keyword-opportunities.js
 */

const fs = require('fs');
const path = require('path');

const TARGET_KEYWORDS_FILE = path.join(__dirname, '..', 'references', 'target-keywords.json');
const DATA_DIR = path.join(__dirname, '..', 'data', 'opportunities');

// Long-tail keyword generators
const PREFIXES = [
  'best', 'free', 'online', 'accurate', 'simple', '2025', '2026',
  'how to use', 'what is', 'guide to', 'calculate', 'estimate'
];

const SUFFIXES = [
  'for federal employees', 'for FERS', 'for CSRS',
  'with taxes', 'after taxes', 'vs pension',
  'eligibility', 'requirements', 'rules'
];

const QUESTIONS = [
  'how does VSIP work',
  'should I take a federal buyout',
  'how much is a federal buyout',
  'is VSIP taxable',
  'can you take VSIP and retire',
  'what is a voluntary separation incentive',
  'how to calculate federal buyout',
  'when is the best time to take a buyout'
];

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
 * Generate long-tail keyword variations
 */
function generateLongTailVariations(baseKeywords) {
  const variations = [];
  
  for (const keyword of baseKeywords) {
    // Add prefixes
    for (const prefix of PREFIXES) {
      variations.push(`${prefix} ${keyword}`);
    }
    
    // Add suffixes
    for (const suffix of SUFFIXES) {
      variations.push(`${keyword} ${suffix}`);
    }
    
    // Add prefix + suffix combinations
    for (const prefix of PREFIXES.slice(0, 3)) {
      for (const suffix of SUFFIXES.slice(0, 2)) {
        variations.push(`${prefix} ${keyword} ${suffix}`);
      }
    }
  }
  
  return [...new Set(variations)];
}

/**
 * Simulate keyword difficulty analysis
 */
function analyzeKeywordDifficulty(keyword) {
  // Simulated metrics (in production, use keyword research API)
  const baseDifficulty = Math.floor(Math.random() * 100);
  const searchVolume = Math.floor(Math.random() * 5000) + 100;
  const cpc = (Math.random() * 5 + 0.5).toFixed(2);
  
  // Calculate opportunity score (lower difficulty + decent volume = better opportunity)
  const opportunityScore = Math.round((100 - baseDifficulty) * (searchVolume / 5000) * 100);
  
  return {
    keyword,
    difficulty: baseDifficulty,
    searchVolume,
    cpc: parseFloat(cpc),
    opportunityScore: Math.min(opportunityScore, 100),
    recommendation: opportunityScore > 60 ? 'HIGH' : opportunityScore > 40 ? 'MEDIUM' : 'LOW'
  };
}

/**
 * Find content gaps based on current rankings
 */
function findContentGaps() {
  const gaps = [
    { topic: 'VSIP tax implications', priority: 'HIGH', reason: 'High search volume, low competition' },
    { topic: 'Buyout vs early retirement comparison', priority: 'HIGH', reason: 'Common decision point' },
    { topic: 'State-by-state buyout tax calculator', priority: 'MEDIUM', reason: 'Location-specific need' },
    { topic: 'Buyout eligibility checker', priority: 'HIGH', reason: 'First step for users' },
    { topic: 'Federal buyout success stories', priority: 'MEDIUM', reason: 'Social proof content' },
    { topic: 'VSIP negotiation tips', priority: 'LOW', reason: 'Advanced user content' },
    { topic: 'Buyout impact on benefits', priority: 'HIGH', reason: 'Critical decision factor' },
    { topic: 'Federal buyout timeline', priority: 'MEDIUM', reason: 'Process clarity' }
  ];
  
  return gaps;
}

/**
 * Main keyword opportunities function
 */
async function findKeywordOpportunities() {
  console.log(`\n💡 FedBuyOut Keyword Opportunity Finder`);
  console.log(`========================================\n`);
  
  const keywordsData = loadJson(TARGET_KEYWORDS_FILE, { keywords: [] });
  const baseKeywords = keywordsData.keywords.map(k => k.term);
  
  // Generate long-tail variations
  console.log('🔄 Generating long-tail variations...');
  const longTailKeywords = generateLongTailVariations(baseKeywords);
  console.log(`   Generated ${longTailKeywords.length} variations\n`);
  
  // Analyze sample of keywords
  console.log('📊 Analyzing keyword difficulty...');
  const sampleSize = Math.min(50, longTailKeywords.length);
  const sampleKeywords = longTailKeywords.sort(() => 0.5 - Math.random()).slice(0, sampleSize);
  
  const analyzed = sampleKeywords.map(analyzeKeywordDifficulty);
  
  // Sort by opportunity score
  const opportunities = analyzed.sort((a, b) => b.opportunityScore - a.opportunityScore);
  
  // Display top opportunities
  console.log('🎯 Top Keyword Opportunities:');
  console.log('-----------------------------');
  
  opportunities.slice(0, 10).forEach((opp, i) => {
    const diffColor = opp.difficulty < 40 ? '🟢' : opp.difficulty < 70 ? '🟡' : '🔴';
    console.log(`${i + 1}. "${opp.keyword}"`);
    console.log(`   Difficulty: ${diffColor} ${opp.difficulty}/100 | Volume: ${opp.searchVolume}/mo | CPC: $${opp.cpc}`);
    console.log(`   Opportunity: ${opp.recommendation} (${opp.opportunityScore}/100)\n`);
  });
  
  // Question-based keywords (voice search friendly)
  console.log('🎤 Question-Based Keywords (Voice Search):');
  console.log('-------------------------------------------');
  QUESTIONS.forEach((q, i) => {
    console.log(`${i + 1}. "${q}?"`);
  });
  
  // Content gaps
  console.log('\n📝 Content Gaps to Fill:');
  console.log('------------------------');
  const gaps = findContentGaps();
  gaps.forEach(gap => {
    const priorityEmoji = gap.priority === 'HIGH' ? '🔴' : gap.priority === 'MEDIUM' ? '🟡' : '🟢';
    console.log(`${priorityEmoji} ${gap.topic} (${gap.priority})`);
    console.log(`   Reason: ${gap.reason}`);
  });
  
  // Save results
  const results = {
    generatedAt: new Date().toISOString(),
    opportunities: opportunities.slice(0, 20),
    questionKeywords: QUESTIONS,
    contentGaps: gaps,
    totalVariations: longTailKeywords.length
  };
  
  const dateStr = new Date().toISOString().split('T')[0];
  const outputFile = path.join(DATA_DIR, `${dateStr}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
  
  console.log(`\n💾 Opportunity data saved to: ${outputFile}\n`);
  
  return results;
}

// Run if called directly
if (require.main === module) {
  findKeywordOpportunities().catch(console.error);
}

module.exports = { findKeywordOpportunities, generateLongTailVariations };
