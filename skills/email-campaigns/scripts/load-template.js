#!/usr/bin/env node
/**
 * load-template.js
 * Loads and renders email templates
 */

const fs = require('fs');
const path = require('path');

const TEMPLATE_DIR = path.join(__dirname, '..', 'assets', 'templates');

/**
 * Load a template file
 * @param {string} name - Template name
 * @param {string} format - 'html' or 'txt'
 * @returns {string|null}
 */
function load(name, format = 'html') {
  const filePath = path.join(TEMPLATE_DIR, `${name}.${format}`);
  
  if (!fs.existsSync(filePath)) {
    // Try fallback to default
    const defaultPath = path.join(TEMPLATE_DIR, `default.${format}`);
    if (fs.existsSync(defaultPath)) {
      return fs.readFileSync(defaultPath, 'utf8');
    }
    return null;
  }
  
  return fs.readFileSync(filePath, 'utf8');
}

/**
 * Render a template with variables
 * @param {string} template - Template string
 * @param {object} variables - Variables to replace
 * @returns {string}
 */
function render(template, variables) {
  let result = template;
  
  // Replace {{variable}} syntax
  for (const [key, value] of Object.entries(variables)) {
    const regex = new RegExp(`{{${key}}}`, 'g');
    result = result.replace(regex, escapeHtml(value || ''));
  }
  
  // Replace conditionals {{#if variable}}...{{/if}}
  result = result.replace(/{{#if (\w+)}}([\s\S]*?){{\/if}}/g, (match, varName, content) => {
    return variables[varName] ? content : '';
  });
  
  return result;
}

/**
 * Escape HTML entities
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Load and render a complete email
 * @param {string} name - Template name
 * @param {object} variables - Variables to replace
 * @param {string} format - 'html' or 'txt'
 * @returns {string|null}
 */
function loadAndRender(name, variables, format = 'html') {
  const template = load(name, format);
  if (!template) return null;
  return render(template, variables);
}

/**
 * List available templates
 * @returns {string[]}
 */
function list() {
  if (!fs.existsSync(TEMPLATE_DIR)) {
    return [];
  }
  
  const files = fs.readdirSync(TEMPLATE_DIR);
  const templates = new Set();
  
  for (const file of files) {
    const match = file.match(/^(.+)\.(html|txt)$/);
    if (match) {
      templates.add(match[1]);
    }
  }
  
  return Array.from(templates).sort();
}

/**
 * Get template metadata
 * @param {string} name
 * @returns {object|null}
 */
function getMetadata(name) {
  const html = load(name, 'html');
  const text = load(name, 'txt');
  
  if (!html && !text) return null;
  
  return {
    name,
    hasHtml: !!html,
    hasText: !!text,
    htmlLength: html ? html.length : 0,
    textLength: text ? text.length : 0
  };
}

module.exports = {
  load,
  render,
  loadAndRender,
  list,
  getMetadata,
  escapeHtml
};

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
Usage: node load-template.js <command> [options]

Commands:
  list                    List available templates
  show <name> [format]    Show template content
  render <name> [json]    Render template with variables

Examples:
  node load-template.js list
  node load-template.js show welcome html
  node load-template.js render welcome '{"firstName":"John"}'
`);
    process.exit(0);
  }
  
  const command = args[0];
  
  switch (command) {
    case 'list':
      const templates = list();
      console.log('Available templates:');
      templates.forEach(t => console.log(`  - ${t}`));
      break;
      
    case 'show':
      const name = args[1];
      const format = args[2] || 'html';
      const content = load(name, format);
      if (content) {
        console.log(content);
      } else {
        console.error(`Template not found: ${name}.${format}`);
        process.exit(1);
      }
      break;
      
    case 'render':
      const renderName = args[1];
      const varsJson = args[2] || '{}';
      try {
        const vars = JSON.parse(varsJson);
        const rendered = loadAndRender(renderName, vars, 'html');
        if (rendered) {
          console.log(rendered);
        } else {
          console.error(`Template not found: ${renderName}`);
          process.exit(1);
        }
      } catch (e) {
        console.error('Invalid JSON variables:', e.message);
        process.exit(1);
      }
      break;
      
    default:
      console.error(`Unknown command: ${command}`);
      process.exit(1);
  }
}
