#!/usr/bin/env python3
"""
Dependency Checker - Check and resolve skill dependencies
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Dependency:
    def __init__(self, name: str, version_spec: str = None):
        self.name = name
        self.version_spec = version_spec  # e.g., ">= 1.0.0"
    
    @classmethod
    def parse(cls, spec: str) -> 'Dependency':
        """Parse dependency spec like 'skill-name >= 1.0.0'."""
        parts = spec.split()
        name = parts[0]
        version = parts[1] if len(parts) > 1 else None
        return cls(name, version)
    
    def __str__(self):
        if self.version_spec:
            return f"{self.name} {self.version_spec}"
        return self.name

class DependencyChecker:
    def __init__(self):
        self.installed_skills = self._get_installed_skills()
    
    def _get_installed_skills(self) -> Dict[str, Dict]:
        """Get all installed skills with their dependencies."""
        skills = {}
        
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                info = self._parse_skill_info(skill_dir)
                skills[info["name"]] = info
        
        return skills
    
    def _parse_skill_info(self, skill_dir: Path) -> Dict:
        """Parse skill info from SKILL.md."""
        info = {
            "name": skill_dir.name,
            "version": "unknown",
            "dependencies": [],
            "path": str(skill_dir)
        }
        
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    
                    match = re.search(r"^version\s*:\s*(.+)$", frontmatter, re.MULTILINE)
                    if match:
                        info["version"] = match.group(1).strip()
                    
                    match = re.search(r"^dependencies\s*:\s*(.+)$", frontmatter, re.MULTILINE)
                    if match:
                        deps_str = match.group(1).strip()
                        # Parse list format
                        deps = [d.strip().strip('[]"') for d in deps_str.strip("[]").split(",") if d.strip()]
                        info["dependencies"] = [Dependency.parse(d) for d in deps]
        
        return info
    
    def check_dependencies(self, skill_name: str, install_missing: bool = False) -> bool:
        """Check dependencies for a skill."""
        if skill_name not in self.installed_skills:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Skill '{skill_name}' is not installed")
            return False
        
        skill = self.installed_skills[skill_name]
        deps = skill.get("dependencies", [])
        
        if not deps:
            print(f"{Colors.GREEN}✓{Colors.ENDC} '{skill_name}' has no dependencies")
            return True
        
        print(f"\nChecking dependencies for '{skill_name}':")
        print("=" * 50)
        
        all_satisfied = True
        missing = []
        version_mismatch = []
        
        for dep in deps:
            if dep.name not in self.installed_skills:
                all_satisfied = False
                missing.append(dep)
                print(f"  {Colors.FAIL}✗{Colors.ENDC} {dep.name} - Not installed")
            else:
                installed = self.installed_skills[dep.name]
                if dep.version_spec and not self._version_satisfies(installed["version"], dep.version_spec):
                    all_satisfied = False
                    version_mismatch.append((dep, installed["version"]))
                    print(f"  {Colors.WARNING}⚠{Colors.ENDC} {dep.name} - Version mismatch (need {dep.version_spec}, have {installed['version']})")
                else:
                    print(f"  {Colors.GREEN}✓{Colors.ENDC} {dep.name} {installed['version']}")
        
        if not all_satisfied:
            print(f"\n{Colors.FAIL}Dependency check failed{Colors.ENDC}")
            
            if missing and install_missing:
                print(f"\n{Colors.BLUE}Installing missing dependencies...{Colors.ENDC}")
                for dep in missing:
                    self._install_dependency(dep)
            
            return False
        
        print(f"\n{Colors.GREEN}✓ All dependencies satisfied{Colors.ENDC}")
        return True
    
    def _version_satisfies(self, version: str, spec: str) -> bool:
        """Check if version satisfies spec."""
        # Simple version comparison (TODO: proper semver)
        if spec.startswith(">="):
            required = spec[2:].strip()
            return version >= required
        elif spec.startswith(">"):
            required = spec[1:].strip()
            return version > required
        elif spec.startswith("="):
            required = spec[1:].strip()
            return version == required
        return True
    
    def _install_dependency(self, dep: Dependency):
        """Install a missing dependency."""
        print(f"  Installing {dep.name}...")
        # TODO: Implement actual installation (from registry, git, etc.)
        print(f"  {Colors.WARNING}⚠{Colors.ENDC} Auto-install not implemented yet")
    
    def show_dependency_tree(self, skill_name: str, level: int = 0, visited: Set[str] = None):
        """Show dependency tree for a skill."""
        if visited is None:
            visited = set()
        
        if skill_name in visited:
            print("  " * level + f"{Colors.WARNING}↻{Colors.ENDC} {skill_name} (circular)")
            return
        
        visited.add(skill_name)
        
        if skill_name not in self.installed_skills:
            print("  " * level + f"{Colors.FAIL}✗{Colors.ENDC} {skill_name} (not installed)")
            return
        
        skill = self.installed_skills[skill_name]
        prefix = "  " * level
        
        if level == 0:
            print(f"{prefix}{Colors.BOLD}{skill_name}{Colors.ENDC} ({skill['version']})")
        else:
            print(f"{prefix}└── {skill_name} ({skill['version']})")
        
        deps = skill.get("dependencies", [])
        for dep in deps:
            self.show_dependency_tree(dep.name, level + 1, visited.copy())
    
    def check_all_dependencies(self) -> bool:
        """Check dependencies for all installed skills."""
        all_good = True
        
        for skill_name in sorted(self.installed_skills.keys()):
            if not self.check_dependencies(skill_name):
                all_good = False
            print()
        
        return all_good
    
    def find_dependents(self, skill_name: str) -> List[str]:
        """Find all skills that depend on the given skill."""
        dependents = []
        
        for name, info in self.installed_skills.items():
            deps = info.get("dependencies", [])
            if any(dep.name == skill_name for dep in deps):
                dependents.append(name)
        
        return dependents

def main():
    parser = argparse.ArgumentParser(description="Check and resolve skill dependencies")
    parser.add_argument("--skill", help="Check dependencies for this skill")
    parser.add_argument("--install", action="store_true", help="Install missing dependencies")
    parser.add_argument("--tree", action="store_true", help="Show dependency tree")
    parser.add_argument("--all", action="store_true", help="Check all skills")
    parser.add_argument("--dependents", help="Find skills that depend on this skill")
    
    args = parser.parse_args()
    
    checker = DependencyChecker()
    
    if args.tree and args.skill:
        print(f"\n{Colors.BOLD}Dependency tree for '{args.skill}':{Colors.ENDC}\n")
        checker.show_dependency_tree(args.skill)
    elif args.dependents:
        deps = checker.find_dependents(args.dependents)
        if deps:
            print(f"\nSkills that depend on '{args.dependents}':")
            for dep in sorted(deps):
                print(f"  - {dep}")
        else:
            print(f"\nNo skills depend on '{args.dependents}'")
    elif args.all:
        success = checker.check_all_dependencies()
        sys.exit(0 if success else 1)
    elif args.skill:
        success = checker.check_dependencies(args.skill, install_missing=args.install)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
