#!/usr/bin/env node
/**
 * Generate SEO reports for FedBuyOut
 * Usage: node generate-report.js --type <weekly|monthly>
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const REPORTS_DIR = path.join(DATA_DIR, 'reports');

// Parse arguments
const args = process.argv.slice(2);
const reportType = args.find(arg => arg.startsWith('--type='))?.split('=')[1] ||
                   (args[args.indexOf('--type') + 1] || 'weekly');

// Ensure reports directory exists
if (!fs.existsSync(REPORTS_DIR)) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

/**
 * Load latest data from a subdirectory
 */
function loadLatestData(subdir) {
  const dir = path.join(DATA_DIR, subdir);
  if (!fs.existsSync(dir)) return null;
  
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.json')).sort().reverse();
  if (files.length === 0) return null;
  
  try {
    return JSON.parse(fs.readFileSync(path.join(dir, files[0]), 'utf8'));
  } catch {
    return null;
  }
}

/**
 * Load historical data for trend analysis
 */
function loadHistoricalData(subdir, days) {
  const dir = path.join(DATA_DIR, subdir);
  if (!fs.existsSync(dir)) return [];
  
  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.json'))
    .sort()
    .reverse()
    .slice(0, days);
  
  return files.map(f => {
    try {
      return JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
    } catch {
      return null;
    }
  }).filter(Boolean);
}

/**
 * Generate weekly report
 */
function generateWeeklyReport() {
  const rankings = loadLatestData('rankings');
  const competitors = loadLatestData('competitors');
  const backlinks = loadLatestData('backlinks');
  const opportunities = loadLatestData('opportunities');
  
  const reportDate = new Date().toISOString().split('T')[0];
  
  // Calculate metrics
  const rankingMetrics = rankings ? {
    totalKeywords: rankings.length,
    rankedKeywords: rankings.filter(r => r.position).length,
    averagePosition: rankings.filter(r => r.position).reduce((sum, r) => sum + r.position, 0) / 
                     rankings.filter(r => r.position).length || 0,
    top3Count: rankings.filter(r => r.position && r.position <= 3).length,
    top10Count: rankings.filter(r => r.position && r.position <= 10).length
  } : null;
  
  const backlinkMetrics = backlinks ? {
    referringDomains: backlinks.summary.referringDomains,
    totalBacklinks: backlinks.summary.totalBacklinks,
    avgAuthority: backlinks.summary.averageAuthority
  } : null;
  
  // Build markdown report
  let md = `# FedBuyOut SEO Weekly Report\n\n`;
  md += `**Report Period:** Week of ${reportDate}\n`;
  md += `**Generated:** ${new Date().toLocaleString()}\n\n`;
  
  md += `## 📊 Executive Summary\n\n`;
  
  if (rankingMetrics) {
    md += `### Rankings Overview\n`;
    md += `- **Keywords Tracked:** ${rankingMetrics.totalKeywords}\n`;
    md += `- **Keywords Ranked:** ${rankingMetrics.rankedKeywords}/${rankingMetrics.totalKeywords}\n`;
    md += `- **Average Position:** ${rankingMetrics.averagePosition.toFixed(1)}\n`;
    md += `- **Top 3 Rankings:** ${rankingMetrics.top3Count}\n`;
    md += `- **Top 10 Rankings:** ${rankingMetrics.top10Count}\n\n`;
  }
  
  if (backlinkMetrics) {
    md += `### Backlink Overview\n`;
    md += `- **Referring Domains:** ${backlinkMetrics.referringDomains}\n`;
    md += `- **Total Backlinks:** ${backlinkMetrics.totalBacklinks}\n`;
    md += `- **Average Authority:** ${backlinkMetrics.avgAuthority}/100\n\n`;
  }
  
  // Keyword performance
  if (rankings) {
    md += `## 🎯 Keyword Performance\n\n`;
    md += `| Keyword | Position | Change | Status |\n`;
    md += `|---------|----------|--------|--------|\n`;
    
    rankings.forEach(r => {
      const pos = r.position ? `#${r.position}` : 'Not ranked';
      const change = r.change || 'N/A';
      const status = r.position && r.position <= 10 ? '🟢' : r.position ? '🟡' : '🔴';
      md += `| ${r.keyword} | ${pos} | ${change} | ${status} |\n`;
    });
    
    md += `\n`;
  }
  
  // Competitor summary
  if (competitors) {
    md += `## 🏆 Competitor Activity\n\n`;
    competitors.forEach(comp => {
      const ranked = comp.rankings.filter(r => r.position).length;
      md += `- **${comp.competitor}:** ${ranked}/${comp.rankings.length} keywords ranked\n`;
    });
    md += `\n`;
  }
  
  // Opportunities
  if (opportunities) {
    md += `## 💡 This Week\'s Opportunities\n\n`;
    md += `### Top Keyword Opportunities\n`;
    opportunities.opportunities.slice(0, 5).forEach((opp, i) => {
      md += `${i + 1}. **${opp.keyword}** (Score: ${opp.opportunityScore}/100)\n`;
      md += `   - Difficulty: ${opp.difficulty}/100 | Volume: ${opp.searchVolume}/mo\n`;
    });
    md += `\n`;
    
    md += `### Content Gaps to Fill\n`;
    opportunities.contentGaps.slice(0, 3).forEach((gap, i) => {
      md += `${i + 1}. **${gap.topic}** (${gap.priority})\n`;
    });
    md += `\n`;
  }
  
  // Action items
  md += `## ✅ Action Items for Next Week\n\n`;
  md += `1. [ ] Continue monitoring target keyword rankings\n`;
  md += `2. [ ] Review and respond to competitor content updates\n`;
  md += `3. [ ] Implement high-priority content gaps\n`;
  md += `4. [ ] Build 2-3 new quality backlinks\n`;
  md += `5. [ ] Optimize pages ranking 11-20 for target keywords\n\n`;
  
  return { md, data: { rankings, competitors, backlinks, opportunities, rankingMetrics, backlinkMetrics } };
}

/**
 * Generate monthly report
 */
function generateMonthlyReport() {
  // Load last 30 days of data
  const rankingHistory = loadHistoricalData('rankings', 30);
  const backlinkHistory = loadHistoricalData('backlinks', 30);
  
  const reportDate = new Date().toISOString().split('T')[0];
  const monthName = new Date().toLocaleString('default', { month: 'long' });
  
  // Calculate trends
  const rankingTrend = rankingHistory.length >= 2 ? {
    startAvg: rankingHistory[rankingHistory.length - 1]
      .filter(r => r.position)
      .reduce((sum, r) => sum + r.position, 0) / 
      rankingHistory[rankingHistory.length - 1].filter(r => r.position).length || 0,
    endAvg: rankingHistory[0]
      .filter(r => r.position)
      .reduce((sum, r) => sum + r.position, 0) / 
      rankingHistory[0].filter(r => r.position).length || 0
  } : null;
  
  // Build markdown report
  let md = `# FedBuyOut SEO Monthly Report\n\n`;
  md += `**Report Period:** ${monthName} ${new Date().getFullYear()}\n`;
  md += `**Generated:** ${new Date().toLocaleString()}\n\n`;
  
  md += `## 📈 Monthly Performance Summary\n\n`;
  
  if (rankingTrend) {
    const improvement = rankingTrend.startAvg - rankingTrend.endAvg;
    md += `### Ranking Trend\n`;
    md += `- **Starting Avg Position:** ${rankingTrend.startAvg.toFixed(1)}\n`;
    md += `- **Current Avg Position:** ${rankingTrend.endAvg.toFixed(1)}\n`;
    md += `- **Improvement:** ${improvement > 0 ? '+' : ''}${improvement.toFixed(1)} positions\n\n`;
  }
  
  // Backlink growth
  if (backlinkHistory.length >= 2) {
    const startLinks = backlinkHistory[backlinkHistory.length - 1].summary.referringDomains;
    const endLinks = backlinkHistory[0].summary.referringDomains;
    const growth = endLinks - startLinks;
    
    md += `### Backlink Growth\n`;
    md += `- **New Domains This Month:** ${growth}\n`;
    md += `- **Total Referring Domains:** ${endLinks}\n\n`;
  }
  
  // Key wins
  md += `## 🏅 Key Wins This Month\n\n`;
  md += `1. Improved average ranking position\n`;
  md += `2. Gained new high-authority backlinks\n`;
  md += `3. Increased organic visibility for target keywords\n\n`;
  
  // Challenges
  md += `## ⚠️ Challenges & Areas for Improvement\n\n`;
  md += `1. Some keywords still not ranking in top 50\n`;
  md += `2. Competitor activity increasing\n`;
  md += `3. Need more diverse anchor text distribution\n\n`;
  
  // Next month goals
  md += `## 🎯 Goals for Next Month\n\n`;
  md += `1. Achieve top 10 rankings for 5+ target keywords\n`;
  md += `2. Acquire 5+ new quality referring domains\n`;
  md += `3. Publish 2 new pieces of target content\n`;
  md += `4. Improve average page load speed\n`;
  md += `5. Increase organic traffic by 20%\n\n`;
  
  return { md, data: { rankingHistory, backlinkHistory, rankingTrend } };
}

/**
 * Main report generation function
 */
async function generateReport() {
  console.log(`\n📄 FedBuyOut SEO Report Generator`);
  console.log(`=================================\n`);
  console.log(`Type: ${reportType}`);
  console.log(`Date: ${new Date().toLocaleDateString()}\n`);
  
  let result;
  
  if (reportType === 'monthly') {
    console.log('Generating monthly report...\n');
    result = generateMonthlyReport();
  } else {
    console.log('Generating weekly report...\n');
    result = generateWeeklyReport();
  }
  
  // Save markdown report
  const dateStr = new Date().toISOString().split('T')[0];
  const mdFile = path.join(REPORTS_DIR, `${dateStr}-${reportType}.md`);
  fs.writeFileSync(mdFile, result.md);
  
  // Save JSON data
  const jsonFile = path.join(REPORTS_DIR, `${dateStr}-${reportType}.json`);
  fs.writeFileSync(jsonFile, JSON.stringify({
    type: reportType,
    generatedAt: new Date().toISOString(),
    ...result.data
  }, null, 2));
  
  // Save CSV summary
  if (result.data.rankings) {
    const csvFile = path.join(REPORTS_DIR, `${dateStr}-${reportType}.csv`);
    let csv = 'Keyword,Position,Change\n';
    result.data.rankings.forEach(r => {
      csv += `"${r.keyword}",${r.position || 'Not ranked'},${r.change || 'N/A'}\n`;
    });
    fs.writeFileSync(csvFile, csv);
  }
  
  console.log('✅ Report generated successfully!\n');
  console.log(`📄 Markdown: ${mdFile}`);
  console.log(`📊 JSON: ${jsonFile}`);
  if (result.data.rankings) {
    console.log(`📈 CSV: ${path.join(REPORTS_DIR, `${dateStr}-${reportType}.csv`)}`);
  }
  
  // Display summary
  console.log(`\n📝 Report Preview:`);
  console.log('==================');
  console.log(result.md.split('\n').slice(0, 30).join('\n'));
  console.log('\n... (truncated)\n');
  
  return result;
}

// Run if called directly
if (require.main === module) {
  generateReport().catch(console.error);
}

module.exports = { generateReport, generateWeeklyReport, generateMonthlyReport };
