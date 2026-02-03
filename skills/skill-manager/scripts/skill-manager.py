#!/usr/bin/env python3
"""
Skill Manager - Main CLI for managing OpenClaw skills
Usage: python3 skill-manager.py <command> [options]
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Configuration
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
SCRIPT_DIR = Path(__file__).parent

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✓{Colors.ENDC} {msg}")

def print_error(msg: str):
    print(f"{Colors.FAIL}✗{Colors.ENDC} {msg}", file=sys.stderr)

def print_warning(msg: str):
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {msg}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ{Colors.ENDC} {msg}")

def get_installed_skills() -> List[Dict]:
    """Get list of all installed skills with metadata."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skill_info = parse_skill_md(skill_dir)
            skill_info["path"] = str(skill_dir)
            skill_info["size"] = get_dir_size(skill_dir)
            skills.append(skill_info)
    
    return skills

def parse_skill_md(skill_dir: Path) -> Dict:
    """Parse SKILL.md frontmatter and content."""
    skill_md = skill_dir / "SKILL.md"
    info = {
        "name": skill_dir.name,
        "description": "No description available",
        "version": "unknown",
        "author": "unknown",
        "tags": [],
        "dependencies": []
    }
    
    if not skill_md.exists():
        return info
    
    content = skill_md.read_text()
    
    # Parse frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "name":
                        info["name"] = value
                    elif key == "description":
                        info["description"] = value
                    elif key == "version":
                        info["version"] = value
                    elif key == "author":
                        info["author"] = value
                    elif key == "tags":
                        # Parse list format: [tag1, tag2]
                        info["tags"] = [t.strip().strip('[]"') for t in value.strip("[]").split(",") if t.strip()]
                    elif key == "dependencies":
                        info["dependencies"] = [d.strip().strip('[]"') for d in value.strip("[]").split(",") if d.strip()]
    
    return info

def get_dir_size(path: Path) -> int:
    """Get directory size in bytes."""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_dir_size(Path(entry.path))
    return total

def format_size(size: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"

def cmd_list(args):
    """List all installed skills."""
    skills = get_installed_skills()
    
    if args.filter:
        skills = [s for s in skills if args.filter.lower() in s["name"].lower() 
                  or args.filter.lower() in s["description"].lower()]
    
    if not skills:
        print_warning("No skills found.")
        return
    
    if args.format == "json":
        print(json.dumps(skills, indent=2))
    else:
        print(f"\n{Colors.BOLD}{'Name':<25} {'Version':<10} {'Size':<10} Description{Colors.ENDC}")
        print("-" * 80)
        for skill in skills:
            name = skill["name"][:24]
            version = skill["version"][:9]
            size = format_size(skill["size"])
            desc = skill["description"][:40] + "..." if len(skill["description"]) > 40 else skill["description"]
            print(f"{name:<25} {version:<10} {size:<10} {desc}")
        print(f"\nTotal: {len(skills)} skill(s) installed")

def cmd_validate(args):
    """Validate skill structure."""
    validator_script = SCRIPT_DIR / "skill-validator.py"
    
    if args.all:
        skills = get_installed_skills()
        errors = 0
        warnings = 0
        
        print_info(f"Validating {len(skills)} skills...")
        for skill in skills:
            result = subprocess.run(
                [sys.executable, str(validator_script), "--skill", skill["name"]],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print_error(f"{skill['name']}: Failed validation")
                print(result.stderr)
                errors += 1
            elif "Warning" in result.stdout and args.strict:
                print_warning(f"{skill['name']}: Has warnings")
                warnings += 1
            else:
                print_success(f"{skill['name']}: Valid")
        
        print(f"\nValidation complete: {len(skills) - errors - warnings} passed, {warnings} warnings, {errors} errors")
        return errors == 0
    
    elif args.skill:
        result = subprocess.run(
            [sys.executable, str(validator_script), "--skill", args.skill],
            capture_output=False
        )
        return result.returncode == 0
    
    else:
        print_error("Please specify --skill <name> or --all")
        return False

def cmd_package(args):
    """Package a skill into .skill file."""
    packager_script = SCRIPT_DIR / "skill-packager.py"
    
    cmd = [sys.executable, str(packager_script), "--skill", args.skill]
    if args.output:
        cmd.extend(["--output", args.output])
    if args.include_registry:
        cmd.append("--include-registry")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def cmd_install(args):
    """Install a skill from .skill file or URL."""
    packager_script = SCRIPT_DIR / "skill-packager.py"
    
    cmd = [sys.executable, str(packager_script), "install"]
    
    if args.file:
        cmd.extend(["--file", args.file])
    elif args.url:
        cmd.extend(["--url", args.url])
    elif args.git:
        cmd.extend(["--git", args.git])
    else:
        print_error("Please specify --file, --url, or --git")
        return False
    
    if args.force:
        cmd.append("--force")
    if args.deps:
        cmd.append("--deps")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def cmd_uninstall(args):
    """Uninstall a skill."""
    if not args.skill:
        print_error("Please specify --skill <name>")
        return False
    
    skill_dir = SKILLS_DIR / args.skill
    if not skill_dir.exists():
        print_error(f"Skill '{args.skill}' not found")
        return False
    
    print_warning(f"This will remove {args.skill} and all its files.")
    response = input("Are you sure? [y/N]: ")
    if response.lower() != 'y':
        print_info("Cancelled")
        return False
    
    import shutil
    try:
        shutil.rmtree(skill_dir)
        print_success(f"Uninstalled '{args.skill}'")
        return True
    except Exception as e:
        print_error(f"Failed to uninstall: {e}")
        return False

def cmd_update(args):
    """Update installed skills."""
    registry_script = SCRIPT_DIR / "registry-manager.py"
    
    cmd = [sys.executable, str(registry_script), "update"]
    
    if args.skill:
        cmd.extend(["--skill", args.skill])
    elif args.all:
        cmd.append("--all")
    
    if args.check:
        cmd.append("--check")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def cmd_registry_update(args):
    """Update skill registry."""
    registry_script = SCRIPT_DIR / "registry-manager.py"
    
    cmd = [sys.executable, str(registry_script), "rebuild"]
    
    if args.add:
        cmd.extend(["--add", args.add])
    if args.remove:
        cmd.extend(["--remove", args.remove])
    if args.sync:
        cmd.extend(["--sync", args.sync])
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def cmd_deps(args):
    """Check skill dependencies."""
    deps_script = SCRIPT_DIR / "dependency-checker.py"
    
    cmd = [sys.executable, str(deps_script)]
    
    if args.skill:
        cmd.extend(["--skill", args.skill])
    if args.install:
        cmd.append("--install")
    if args.tree:
        cmd.append("--tree")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def cmd_docs(args):
    """Browse skill documentation."""
    docs_script = SCRIPT_DIR / "doc-browser.py"
    
    cmd = [sys.executable, str(docs_script)]
    
    if args.skill:
        cmd.extend(["--skill", args.skill])
    if args.search:
        cmd.extend(["--search", args.search])
    if args.section:
        cmd.extend(["--section", args.section])
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def cmd_search(args):
    """Search for skills."""
    registry_script = SCRIPT_DIR / "registry-manager.py"
    
    cmd = [sys.executable, str(registry_script), "search"]
    
    if args.query:
        cmd.extend(["--query", args.query])
    if args.tag:
        cmd.extend(["--tag", args.tag])
    if args.source:
        cmd.extend(["--source", args.source])
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def cmd_create(args):
    """Create a new skill from template."""
    creator_script = SCRIPT_DIR / "skill-creator.py"
    
    cmd = [sys.executable, str(creator_script)]
    
    if args.name:
        cmd.extend(["--name", args.name])
    if args.description:
        cmd.extend(["--description", args.description])
    if args.template:
        cmd.extend(["--template", args.template])
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(
        description="Skill Manager - Manage OpenClaw skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s validate --skill blog-writer
  %(prog)s package --skill blog-writer --output ./blog-writer.skill
  %(prog)s install --file ./blog-writer.skill
  %(prog)s docs --skill blog-writer
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List installed skills")
    list_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    list_parser.add_argument("--filter", help="Filter by keyword")
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate skill structure")
    validate_parser.add_argument("--skill", help="Skill name to validate")
    validate_parser.add_argument("--all", action="store_true", help="Validate all skills")
    validate_parser.add_argument("--strict", action="store_true", help="Strict validation")
    
    # package command
    package_parser = subparsers.add_parser("package", help="Package a skill")
    package_parser.add_argument("--skill", required=True, help="Skill to package")
    package_parser.add_argument("--output", help="Output file path")
    package_parser.add_argument("--include-registry", action="store_true", help="Include in registry")
    
    # install command
    install_parser = subparsers.add_parser("install", help="Install a skill")
    install_group = install_parser.add_mutually_exclusive_group()
    install_group.add_argument("--file", help="Path to .skill file")
    install_group.add_argument("--url", help="URL to download .skill file")
    install_group.add_argument("--git", help="Git repository URL")
    install_parser.add_argument("--force", action="store_true", help="Force overwrite")
    install_parser.add_argument("--deps", action="store_true", help="Install dependencies")
    
    # uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a skill")
    uninstall_parser.add_argument("--skill", required=True, help="Skill to uninstall")
    uninstall_parser.add_argument("--keep-data", action="store_true", help="Keep data files")
    
    # update command
    update_parser = subparsers.add_parser("update", help="Update installed skills")
    update_parser.add_argument("--skill", help="Skill to update")
    update_parser.add_argument("--all", action="store_true", help="Update all skills")
    update_parser.add_argument("--check", action="store_true", help="Check for updates only")
    
    # registry-update command
    registry_parser = subparsers.add_parser("registry-update", help="Update skill registry")
    registry_parser.add_argument("--add", help="Add skill to registry")
    registry_parser.add_argument("--remove", help="Remove from registry")
    registry_parser.add_argument("--sync", help="Sync with remote registry URL")
    
    # deps command
    deps_parser = subparsers.add_parser("deps", help="Check dependencies")
    deps_parser.add_argument("--skill", help="Check dependencies for skill")
    deps_parser.add_argument("--install", action="store_true", help="Install missing dependencies")
    deps_parser.add_argument("--tree", action="store_true", help="Show dependency tree")
    
    # docs command
    docs_parser = subparsers.add_parser("docs", help="Browse skill documentation")
    docs_parser.add_argument("--skill", required=True, help="Show docs for skill")
    docs_parser.add_argument("--search", help="Search in documentation")
    docs_parser.add_argument("--section", help="Jump to section")
    
    # search command
    search_parser = subparsers.add_parser("search", help="Search for skills")
    search_parser.add_argument("--query", help="Search query")
    search_parser.add_argument("--tag", help="Filter by tag")
    search_parser.add_argument("--source", choices=["local", "remote", "all"], default="all", help="Search scope")
    
    # create command
    create_parser = subparsers.add_parser("create", help="Create a new skill")
    create_parser.add_argument("--name", required=True, help="Skill name")
    create_parser.add_argument("--description", default="A new OpenClaw skill", help="Skill description")
    create_parser.add_argument("--template", default="basic", choices=["basic", "python", "node"], help="Template to use")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "list": cmd_list,
        "validate": cmd_validate,
        "package": cmd_package,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
        "update": cmd_update,
        "registry-update": cmd_registry_update,
        "deps": cmd_deps,
        "docs": cmd_docs,
        "search": cmd_search,
        "create": cmd_create,
    }
    
    success = commands[args.command](args)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
