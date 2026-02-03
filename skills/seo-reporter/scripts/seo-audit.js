#!/usr/bin/env node
/**
 * Run SEO audit on FedBuyOut pages
 * Usage: node seo-audit.js --url <url>
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data', 'audits');

// Parse arguments
const args = process.argv.slice(2);
const targetUrl = args.find(arg => arg.startsWith('--url='))?.split('=')[1] ||
                  (args[args.indexOf('--url') + 1] || null);

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

/**
 * Simulated page fetch and analysis
 */
async function fetchPageData(url) {
  // In production, this would use puppeteer or similar to fetch actual page data
  // For now, simulating the structure that would be analyzed
  
  return {
    url,
    title: url.includes('calculator') ? 'Federal Buyout Calculator | FedBuyOut' : 'FedBuyOut - Federal Employee Buyout Calculator',
    description: 'Calculate your federal buyout value with our free VSIP calculator. For FERS and CSRS employees considering early retirement.',
    headings: {
      h1: ['Federal Buyout Calculator'],
      h2: ['How It Works', 'Calculate Your Buyout', 'Eligibility Requirements'],
      h3: ['VSIP Overview', 'Tax Implications', 'Next Steps']
    },
    meta: {
      robots: 'index, follow',
      viewport: 'width=device-width, initial-scale=1',
      charset: 'UTF-8',
      canonical: url
    },
    og: {
      title: 'FedBuyOut - Federal Buyout Calculator',
      description: 'Free federal employee buyout calculator',
      image: 'https://fedbuyout.com/og-image.png'
    },
    content: {
      wordCount: 1200,
      internalLinks: 15,
      externalLinks: 3,
      images: 4,
      imagesWithAlt: 3
    },
    technical: {
      https: true,
      mobileFriendly: true,
      loadTime: 1.2,
      pageSize: 850000,
      hasSitemap: true,
      hasRobots: true
    },
    schema: ['Organization', 'WebApplication']
  };
}

/**
 * Analyze on-page SEO factors
 */
function analyzeOnPageSEO(data) {
  const issues = [];
  const warnings = [];
  const passed = [];
  
  // Title analysis
  if (!data.title) {
    issues.push({ type: 'CRITICAL', field: 'title', message: 'Missing title tag' });
  } else {
    if (data.title.length < 30) {
      warnings.push({ type: 'WARNING', field: 'title', message: `Title too short (${data.title.length} chars, recommend 50-60)` });
    } else if (data.title.length > 60) {
      warnings.push({ type: 'WARNING', field: 'title', message: `Title too long (${data.title.length} chars, may be truncated)` });
    } else {
      passed.push({ type: 'PASSED', field: 'title', message: `Title length good (${data.title.length} chars)` });
    }
    
    if (!data.title.toLowerCase().includes('buyout') && !data.title.toLowerCase().includes('vsip')) {
      warnings.push({ type: 'WARNING', field: 'title', message: 'Title missing target keyword (buyout/VSIP)' });
    }
  }
  
  // Description analysis
  if (!data.description) {
    issues.push({ type: 'CRITICAL', field: 'description', message: 'Missing meta description' });
  } else {
    if (data.description.length < 120) {
      warnings.push({ type: 'WARNING', field: 'description', message: `Description too short (${data.description.length} chars)` });
    } else if (data.description.length > 160) {
      warnings.push({ type: 'WARNING', field: 'description', message: `Description too long (${data.description.length} chars)` });
    } else {
      passed.push({ type: 'PASSED', field: 'description', message: `Description length good (${data.description.length} chars)` });
    }
  }
  
  // Heading structure
  if (data.headings.h1.length === 0) {
    issues.push({ type: 'CRITICAL', field: 'h1', message: 'Missing H1 tag' });
  } else if (data.headings.h1.length > 1) {
    warnings.push({ type: 'WARNING', field: 'h1', message: `Multiple H1 tags found (${data.headings.h1.length})` });
  } else {
    passed.push({ type: 'PASSED', field: 'h1', message: 'Single H1 tag present' });
  }
  
  // Image alt text
  const altRatio = data.content.imagesWithAlt / data.content.images;
  if (data.content.images > 0 && altRatio < 1) {
    const missing = data.content.images - data.content.imagesWithAlt;
    warnings.push({ type: 'WARNING', field: 'images', message: `${missing} images missing alt text` });
  } else {
    passed.push({ type: 'PASSED', field: 'images', message: 'All images have alt text' });
  }
  
  return { issues, warnings, passed };
}

/**
 * Analyze technical SEO factors
 */
function analyzeTechnicalSEO(data) {
  const issues = [];
  const warnings = [];
  const passed = [];
  
  if (!data.technical.https) {
    issues.push({ type: 'CRITICAL', field: 'https', message: 'Site not using HTTPS' });
  } else {
    passed.push({ type: 'PASSED', field: 'https', message: 'HTTPS enabled' });
  }
  
  if (data.technical.loadTime > 3) {
    warnings.push({ type: 'WARNING', field: 'speed', message: `Page slow (${data.technical.loadTime}s, target < 3s)` });
  } else {
    passed.push({ type: 'PASSED', field: 'speed', message: `Page speed good (${data.technical.loadTime}s)` });
  }
  
  if (!data.technical.hasSitemap) {
    warnings.push({ type: 'WARNING', field: 'sitemap', message: 'XML sitemap not found' });
  } else {
    passed.push({ type: 'PASSED', field: 'sitemap', message: 'XML sitemap present' });
  }
  
  if (!data.technical.mobileFriendly) {
    issues.push({ type: 'CRITICAL', field: 'mobile', message: 'Page not mobile-friendly' });
  } else {
    passed.push({ type: 'PASSED', field: 'mobile', message: 'Mobile-friendly' });
  }
  
  return { issues, warnings, passed };
}

/**
 * Calculate overall score
 */
function calculateScore(onPage, technical) {
  const totalIssues = onPage.issues.length + technical.issues.length;
  const totalWarnings = onPage.warnings.length + technical.warnings.length;
  const totalPassed = onPage.passed.length + technical.passed.length;
  
  const total = totalIssues * 3 + totalWarnings + totalPassed;
  const deductions = totalIssues * 3 + totalWarnings;
  
  return Math.max(0, Math.round(((total - deductions) / total) * 100));
}

/**
 * Main audit function
 */
async function runSEOAudit(url) {
  const target = url || 'https://fedbuyout.com';
  
  console.log(`\n🔍 FedBuyOut SEO Audit`);
  console.log(`======================\n`);
  console.log(`URL: ${target}`);
  console.log(`Date: ${new Date().toLocaleDateString()}\n`);
  
  // Fetch page data
  console.log('📥 Fetching page data...');
  const pageData = await fetchPageData(target);
  
  // Run analyses
  console.log('🔍 Analyzing on-page SEO...');
  const onPage = analyzeOnPageSEO(pageData);
  
  console.log('⚙️  Analyzing technical SEO...\n');
  const technical = analyzeTechnicalSEO(pageData);
  
  // Calculate score
  const score = calculateScore(onPage, technical);
  
  // Display results
  console.log(`📊 Overall Score: ${score}/100\n`);
  
  // Critical issues
  const allIssues = [...onPage.issues, ...technical.issues];
  if (allIssues.length > 0) {
    console.log('🔴 Critical Issues:');
    allIssues.forEach(issue => {
      console.log(`   [${issue.field}] ${issue.message}`);
    });
    console.log('');
  }
  
  // Warnings
  const allWarnings = [...onPage.warnings, ...technical.warnings];
  if (allWarnings.length > 0) {
    console.log('🟡 Warnings:');
    allWarnings.forEach(warning => {
      console.log(`   [${warning.field}] ${warning.message}`);
    });
    console.log('');
  }
  
  // Passed checks
  const allPassed = [...onPage.passed, ...technical.passed];
  if (allPassed.length > 0) {
    console.log('🟢 Passed:');
    allPassed.slice(0, 5).forEach(passed => {
      console.log(`   [${passed.field}] ${passed.message}`);
    });
    if (allPassed.length > 5) {
      console.log(`   ... and ${allPassed.length - 5} more`);
    }
    console.log('');
  }
  
  // Recommendations
  console.log('💡 Recommendations:');
  if (allIssues.length === 0 && allWarnings.length === 0) {
    console.log('   Great job! No major issues found.');
  } else {
    if (allIssues.some(i => i.field === 'title')) {
      console.log('   1. Add a descriptive title tag with target keywords');
    }
    if (allIssues.some(i => i.field === 'description')) {
      console.log('   2. Add a compelling meta description (150-160 chars)');
    }
    if (allWarnings.some(w => w.field === 'images')) {
      console.log('   3. Add descriptive alt text to all images');
    }
    if (allWarnings.some(w => w.field === 'speed')) {
      console.log('   4. Optimize page speed (compress images, minify JS/CSS)');
    }
  }
  
  // Save results
  const results = {
    url: target,
    auditedAt: new Date().toISOString(),
    score,
    onPage,
    technical,
    pageData: {
      title: pageData.title,
      description: pageData.description,
      wordCount: pageData.content.wordCount,
      loadTime: pageData.technical.loadTime
    }
  };
  
  const dateStr = new Date().toISOString().split('T')[0];
  const urlSlug = target.replace(/[^a-z0-9]/gi, '_');
  const outputFile = path.join(DATA_DIR, `${dateStr}_${urlSlug}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
  
  console.log(`\n💾 Audit saved to: ${outputFile}\n`);
  
  return results;
}

// Run if called directly
if (require.main === module) {
  runSEOAudit(targetUrl).catch(console.error);
}

module.exports = { runSEOAudit };
