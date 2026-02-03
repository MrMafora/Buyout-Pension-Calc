#!/usr/bin/env python3
"""
Skill Validator - Validate skill structure and integrity
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")

class Colors:
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class SkillValidator:
    def __init__(self, skill_dir: Path, strict: bool = False):
        self.skill_dir = skill_dir
        self.skill_name = skill_dir.name
        self.strict = strict
        self.errors = []
        self.warnings = []
    
    def validate(self) -> bool:
        """Run all validation checks."""
        self._check_skill_md_exists()
        self._check_frontmatter()
        self._check_scripts()
        self._check_references()
        self._check_manifest()
        self._check_permissions()
        
        return len(self.errors) == 0 and (not self.strict or len(self.warnings) == 0)
    
    def _check_skill_md_exists(self):
        """Check that SKILL.md exists."""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md is missing")
        elif not skill_md.is_file():
            self.errors.append("SKILL.md is not a file")
    
    def _check_frontmatter(self):
        """Parse and validate SKILL.md frontmatter."""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text()
        
        # Check for frontmatter
        if not content.startswith("---"):
            self.errors.append("SKILL.md missing frontmatter (must start with ---)")
            return
        
        # Parse frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            self.errors.append("SKILL.md has incomplete frontmatter")
            return
        
        frontmatter = parts[1].strip()
        
        # Required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            pattern = rf"^{field}\s*:"
            if not re.search(pattern, frontmatter, re.MULTILINE):
                self.errors.append(f"SKILL.md frontmatter missing required field: {field}")
        
        # Check name matches directory
        name_match = re.search(r"^name\s*:\s*(.+)$", frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if name != self.skill_name:
                self.warnings.append(f"Frontmatter name '{name}' doesn't match directory '{self.skill_name}'")
        
        # Check description length
        desc_match = re.search(r"^description\s*:\s*(.+)$", frontmatter, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 10:
                self.warnings.append("Description is too short (minimum 10 characters)")
            if len(desc) > 200:
                self.warnings.append("Description is too long (maximum 200 characters)")
    
    def _check_scripts(self):
        """Check scripts directory if it exists."""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return
        
        if not scripts_dir.is_dir():
            self.errors.append("scripts exists but is not a directory")
            return
        
        # Check script files are executable
        for script_file in scripts_dir.iterdir():
            if script_file.is_file():
                # Check for shebang
                try:
                    with open(script_file, 'r') as f:
                        first_line = f.readline()
                        if not first_line.startswith('#!'):
                            self.warnings.append(f"Script {script_file.name} missing shebang (#!/...)")
                except:
                    pass
                
                # Check executable permission
                if not os.access(script_file, os.X_OK):
                    if script_file.suffix in ['.py', '.sh', '.js']:
                        self.warnings.append(f"Script {script_file.name} is not executable")
    
    def _check_references(self):
        """Check that referenced files exist."""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text()
        
        # Find markdown links [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for text, path in links:
            # Skip URLs
            if path.startswith(('http://', 'https://', 'mailto:')):
                continue
            
            # Skip anchors
            if path.startswith('#'):
                continue
            
            # Resolve relative path
            if path.startswith('/'):
                referenced_file = Path(path)
            else:
                referenced_file = self.skill_dir / path
            
            if not referenced_file.exists():
                self.warnings.append(f"Broken reference: {path}")
    
    def _check_manifest(self):
        """Check manifest.json if it exists."""
        manifest_file = self.skill_dir / "manifest.json"
        if not manifest_file.exists():
            return
        
        try:
            manifest = json.loads(manifest_file.read_text())
            
            # Check required fields
            if "name" not in manifest:
                self.warnings.append("manifest.json missing 'name' field")
            elif manifest["name"] != self.skill_name:
                self.warnings.append(f"manifest.json name '{manifest['name']}' doesn't match directory")
            
            if "version" not in manifest:
                self.warnings.append("manifest.json missing 'version' field")
            
        except json.JSONDecodeError as e:
            self.errors.append(f"manifest.json is invalid JSON: {e}")
    
    def _check_permissions(self):
        """Check file permissions and ownership."""
        # Check for world-writable files
        for root, dirs, files in os.walk(self.skill_dir):
            for file in files:
                filepath = Path(root) / file
                try:
                    stat = filepath.stat()
                    if stat.st_mode & 0o002:  # World writable
                        self.warnings.append(f"File is world-writable: {filepath.relative_to(self.skill_dir)}")
                except:
                    pass
    
    def print_report(self):
        """Print validation report."""
        print(f"\nValidating skill: {self.skill_name}")
        print("=" * 50)
        
        if self.errors:
            print(f"\n{Colors.FAIL}Errors:{Colors.ENDC}")
            for error in self.errors:
                print(f"  ✗ {error}")
        
        if self.warnings:
            print(f"\n{Colors.WARNING}Warnings:{Colors.ENDC}")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        if not self.errors and not self.warnings:
            print(f"\n{Colors.GREEN}✓ All checks passed!{Colors.ENDC}")
        elif not self.errors:
            print(f"\n{Colors.GREEN}✓ No errors (with warnings){Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}✗ Validation failed with {len(self.errors)} error(s){Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="Validate OpenClaw skill structure")
    parser.add_argument("--skill", required=True, help="Skill name to validate")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    skill_dir = SKILLS_DIR / args.skill
    if not skill_dir.exists():
        print(f"Error: Skill '{args.skill}' not found at {skill_dir}", file=sys.stderr)
        sys.exit(1)
    
    validator = SkillValidator(skill_dir, strict=args.strict)
    is_valid = validator.validate()
    validator.print_report()
    
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
