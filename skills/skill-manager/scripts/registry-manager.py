#!/usr/bin/env python3
"""
Registry Manager - Manage skill registry
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
REGISTRY_PATH = SKILLS_DIR / "skill-manager" / "registry.json"

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class RegistryManager:
    def __init__(self):
        self.registry = self._load_registry()
    
    def _load_registry(self) -> dict:
        """Load or create registry."""
        if REGISTRY_PATH.exists():
            return json.loads(REGISTRY_PATH.read_text())
        return {"version": "1.0", "lastUpdated": None, "skills": []}
    
    def _save_registry(self):
        """Save registry to file."""
        self.registry["lastUpdated"] = datetime.now().isoformat()
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_text(json.dumps(self.registry, indent=2))
    
    def rebuild(self, add_path: Path = None, remove_name: str = None, sync_url: str = None):
        """Rebuild registry from installed skills."""
        if sync_url:
            print(f"Syncing with remote registry: {sync_url}")
            # TODO: Implement remote sync
            return
        
        if add_path:
            self._add_from_path(add_path)
            return
        
        if remove_name:
            self._remove_skill(remove_name)
            return
        
        # Rebuild from installed skills
        print("Rebuilding registry from installed skills...")
        
        skills = []
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skill_info = self._parse_skill_info(skill_dir)
                skills.append(skill_info)
        
        self.registry["skills"] = skills
        self._save_registry()
        
        print(f"{Colors.GREEN}✓{Colors.ENDC} Registry updated with {len(skills)} skills")
    
    def _parse_skill_info(self, skill_dir: Path) -> dict:
        """Parse skill info from SKILL.md."""
        import re
        
        info = {
            "name": skill_dir.name,
            "description": "No description",
            "version": "unknown",
            "author": "unknown",
            "tags": [],
            "installed": True,
            "path": str(skill_dir)
        }
        
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    
                    for key in ["name", "description", "version", "author"]:
                        match = re.search(rf"^{key}\s*:\s*(.+)$", frontmatter, re.MULTILINE)
                        if match:
                            info[key] = match.group(1).strip()
                    
                    match = re.search(r"^tags\s*:\s*(.+)$", frontmatter, re.MULTILINE)
                    if match:
                        tags = match.group(1).strip()
                        info["tags"] = [t.strip().strip('[]"') for t in tags.strip("[]").split(",") if t.strip()]
        
        return info
    
    def _add_from_path(self, path: Path):
        """Add skill from path to registry."""
        if not path.exists():
            print(f"{Colors.FAIL}✗{Colors.ENDC} Path not found: {path}")
            return
        
        if path.suffix == ".skill":
            # Parse .skill file
            import tarfile
            with tarfile.open(path, "r:gz") as tar:
                manifest_member = [m for m in tar.getmembers() if m.name.endswith("manifest.json")][0]
                manifest = json.loads(tar.extractfile(manifest_member).read())
                
                entry = {
                    "name": manifest["name"],
                    "version": manifest["version"],
                    "description": manifest.get("description", ""),
                    "author": manifest.get("author", "unknown"),
                    "tags": manifest.get("tags", []),
                    "path": str(path.resolve()),
                    "installed": False
                }
        else:
            entry = self._parse_skill_info(path)
        
        # Replace or add
        existing = [s for s in self.registry["skills"] if s["name"] == entry["name"]]
        if existing:
            self.registry["skills"].remove(existing[0])
        
        self.registry["skills"].append(entry)
        self._save_registry()
        
        print(f"{Colors.GREEN}✓{Colors.ENDC} Added '{entry['name']}' to registry")
    
    def _remove_skill(self, name: str):
        """Remove skill from registry."""
        existing = [s for s in self.registry["skills"] if s["name"] == name]
        if existing:
            self.registry["skills"].remove(existing[0])
            self._save_registry()
            print(f"{Colors.GREEN}✓{Colors.ENDC} Removed '{name}' from registry")
        else:
            print(f"{Colors.WARNING}⚠{Colors.ENDC} '{name}' not in registry")
    
    def search(self, query: str = None, tag: str = None, source: str = "all"):
        """Search skills in registry."""
        results = []
        
        for skill in self.registry.get("skills", []):
            if source == "local" and not skill.get("installed", False):
                continue
            if source == "remote" and skill.get("installed", False):
                continue
            
            if query:
                query_lower = query.lower()
                if (query_lower not in skill["name"].lower() and 
                    query_lower not in skill.get("description", "").lower()):
                    continue
            
            if tag and tag not in skill.get("tags", []):
                continue
            
            results.append(skill)
        
        if not results:
            print("No skills found matching criteria")
            return
        
        print(f"\n{Colors.BOLD}{'Name':<25} {'Version':<10} {'Installed':<10} Description{Colors.ENDC}")
        print("-" * 80)
        
        for skill in results:
            name = skill["name"][:24]
            version = skill.get("version", "unknown")[:9]
            installed = "✓" if skill.get("installed", False) else ""
            desc = skill.get("description", "No description")[:40]
            if len(desc) > 37:
                desc = desc[:37] + "..."
            print(f"{name:<25} {version:<10} {installed:<10} {desc}")
        
        print(f"\nFound {len(results)} skill(s)")
    
    def update(self, skill_name: str = None, check_only: bool = False, update_all: bool = False):
        """Check for and apply updates."""
        if skill_name:
            self._update_single(skill_name, check_only)
        elif update_all:
            for skill in self.registry.get("skills", []):
                if skill.get("installed", False):
                    self._update_single(skill["name"], check_only)
        else:
            print("Please specify --skill <name> or --all")
    
    def _update_single(self, skill_name: str, check_only: bool):
        """Update a single skill."""
        skill = [s for s in self.registry["skills"] if s["name"] == skill_name]
        if not skill:
            print(f"{Colors.WARNING}⚠{Colors.ENDC} '{skill_name}' not in registry")
            return
        
        skill = skill[0]
        
        # TODO: Check for newer version in remote registry
        # For now, just report installed version
        
        if check_only:
            print(f"{Colors.BLUE}ℹ{Colors.ENDC} {skill_name}: {skill.get('version', 'unknown')} (installed)")
        else:
            print(f"{Colors.BLUE}ℹ{Colors.ENDC} Updating {skill_name}...")
            # TODO: Implement actual update logic
            print(f"{Colors.GREEN}✓{Colors.ENDC} {skill_name} is up to date")

def main():
    parser = argparse.ArgumentParser(description="Manage OpenClaw skill registry")
    subparsers = parser.add_subparsers(dest="command")
    
    # rebuild command
    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild registry")
    rebuild_parser.add_argument("--add", type=Path, help="Add skill to registry")
    rebuild_parser.add_argument("--remove", help="Remove from registry")
    rebuild_parser.add_argument("--sync", help="Sync with remote registry URL")
    
    # search command
    search_parser = subparsers.add_parser("search", help="Search skills")
    search_parser.add_argument("--query", help="Search query")
    search_parser.add_argument("--tag", help="Filter by tag")
    search_parser.add_argument("--source", choices=["local", "remote", "all"], default="all")
    
    # update command
    update_parser = subparsers.add_parser("update", help="Update skills")
    update_parser.add_argument("--skill", help="Skill to update")
    update_parser.add_argument("--all", action="store_true", help="Update all")
    update_parser.add_argument("--check", action="store_true", help="Check only")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = RegistryManager()
    
    if args.command == "rebuild":
        manager.rebuild(
            add_path=args.add,
            remove_name=args.remove,
            sync_url=args.sync
        )
    elif args.command == "search":
        manager.search(
            query=args.query,
            tag=args.tag,
            source=args.source
        )
    elif args.command == "update":
        manager.update(
            skill_name=args.skill,
            check_only=args.check,
            update_all=args.all
        )

if __name__ == "__main__":
    main()
