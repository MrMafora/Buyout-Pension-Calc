#!/usr/bin/env python3
"""
Doc Browser - Browse skill documentation
"""

import argparse
import re
import sys
from pathlib import Path

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DocBrowser:
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.skill_dir = SKILLS_DIR / skill_name
        self.skill_md = self.skill_dir / "SKILL.md"
    
    def show_docs(self, section: str = None, search: str = None):
        """Show skill documentation."""
        if not self.skill_dir.exists():
            print(f"{Colors.FAIL}✗{Colors.ENDC} Skill '{self.skill_name}' not found")
            return False
        
        if not self.skill_md.exists():
            print(f"{Colors.FAIL}✗{Colors.ENDC} No SKILL.md found for '{self.skill_name}'")
            return False
        
        content = self.skill_md.read_text()
        
        # Remove frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]
        
        if search:
            self._search_content(content, search)
        elif section:
            self._show_section(content, section)
        else:
            self._show_full_docs(content)
        
        return True
    
    def _show_full_docs(self, content: str):
        """Show full documentation with formatting."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}📚 {self.skill_name}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        formatted = self._format_markdown(content)
        print(formatted)
    
    def _show_section(self, content: str, section_name: str):
        """Show a specific section."""
        # Find section header
        section_pattern = rf"(^|\n)##+\s*{re.escape(section_name)}.*?(?=\n##|\Z)"
        match = re.search(section_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not match:
            print(f"{Colors.WARNING}⚠{Colors.ENDC} Section '{section_name}' not found")
            
            # Show available sections
            print(f"\n{Colors.BLUE}Available sections:{Colors.ENDC}")
            headers = re.findall(r'\n(##+\s+.+)', content)
            for header in headers[:20]:  # Limit to 20 sections
                level = header.count('#')
                title = header.strip('#').strip()
                indent = "  " * (level - 2)
                print(f"{indent}- {title}")
            return
        
        section_content = match.group(0)
        print(f"\n{Colors.BOLD}{Colors.CYAN}📖 {self.skill_name} - {section_name}{Colors.ENDC}\n")
        print(self._format_markdown(section_content))
    
    def _search_content(self, content: str, query: str):
        """Search for text in documentation."""
        query_lower = query.lower()
        lines = content.split('\n')
        
        matches = []
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Get context (2 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = lines[start:end]
                matches.append((i + 1, context))
        
        if not matches:
            print(f"{Colors.WARNING}⚠{Colors.ENDC} No matches found for '{query}'")
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 Search results for '{query}' in {self.skill_name}:{Colors.ENDC}\n")
        
        for line_num, context in matches[:10]:  # Limit to 10 matches
            print(f"{Colors.BLUE}Line {line_num}:{Colors.ENDC}")
            for j, line in enumerate(context):
                prefix = ">>> " if j == 2 else "    "
                # Highlight search term
                highlighted = re.sub(
                    f'({re.escape(query)})', 
                    f'{Colors.GREEN}\\1{Colors.ENDC}', 
                    line, 
                    flags=re.IGNORECASE
                )
                print(f"{prefix}{highlighted}")
            print()
        
        if len(matches) > 10:
            print(f"... and {len(matches) - 10} more matches")
    
    def _format_markdown(self, content: str) -> str:
        """Simple markdown formatting for terminal."""
        lines = content.split('\n')
        formatted = []
        in_code_block = False
        
        for line in lines:
            # Code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                formatted.append(f"{Colors.CYAN}{line}{Colors.ENDC}")
                continue
            
            if in_code_block:
                formatted.append(line)
                continue
            
            # Headers
            if line.startswith('# '):
                formatted.append(f"{Colors.BOLD}{Colors.CYAN}{line[2:]}{Colors.ENDC}")
            elif line.startswith('## '):
                formatted.append(f"\n{Colors.BOLD}{Colors.BLUE}{line[3:]}{Colors.ENDC}")
            elif line.startswith('### '):
                formatted.append(f"{Colors.BOLD}{line[4:]}{Colors.ENDC}")
            # Bold
            elif '**' in line:
                line = re.sub(r'\*\*(.+?)\*\*', f'{Colors.BOLD}\\1{Colors.ENDC}', line)
                formatted.append(line)
            # Italic
            elif '*' in line:
                line = re.sub(r'\*(.+?)\*', f'{Colors.UNDERLINE}\\1{Colors.ENDC}', line)
                formatted.append(line)
            # Code inline
            elif '`' in line:
                line = re.sub(r'`(.+?)`', f'{Colors.CYAN}\\1{Colors.ENDC}', line)
                formatted.append(line)
            # Links
            elif '[' in line and '](' in line:
                line = re.sub(r'\[(.+?)\]\((.+?)\)', f'\\1 ({Colors.BLUE}\\2{Colors.ENDC})', line)
                formatted.append(line)
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)
    
    def list_sections(self):
        """List all sections in the skill documentation."""
        if not self.skill_md.exists():
            print(f"{Colors.FAIL}✗{Colors.ENDC} No SKILL.md found for '{self.skill_name}'")
            return False
        
        content = self.skill_md.read_text()
        
        # Remove frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2]
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}📑 Sections in {self.skill_name}:{Colors.ENDC}\n")
        
        headers = re.findall(r'\n(##+\s+.+)', content)
        for header in headers:
            level = header.count('#')
            title = header.strip('#').strip()
            indent = "  " * (level - 2)
            marker = "━" if level == 2 else "─"
            print(f"{indent}{marker} {title}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Browse skill documentation")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--section", help="Jump to specific section")
    parser.add_argument("--search", help="Search for text")
    parser.add_argument("--list-sections", action="store_true", help="List all sections")
    
    args = parser.parse_args()
    
    browser = DocBrowser(args.skill)
    
    if args.list_sections:
        success = browser.list_sections()
    else:
        success = browser.show_docs(section=args.section, search=args.search)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
