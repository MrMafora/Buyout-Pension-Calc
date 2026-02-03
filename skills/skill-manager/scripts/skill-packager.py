#!/usr/bin/env python3
"""
Skill Packager - Package and install OpenClaw skills
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
REGISTRY_PATH = SKILLS_DIR / "skill-manager" / "registry.json"

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class SkillPackager:
    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.skill_name = skill_dir.name
    
    def package(self, output_path: Path = None, include_registry: bool = False) -> Path:
        """Package skill into .skill file (tar.gz)."""
        if output_path is None:
            output_path = Path(f"./{self.skill_name}.skill")
        
        output_path = output_path.resolve()
        
        # Create manifest
        manifest = self._create_manifest()
        
        # Create temporary directory for packaging
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            pkg_dir = tmpdir / self.skill_name
            pkg_dir.mkdir()
            
            # Copy skill files
            self._copy_skill_files(pkg_dir)
            
            # Write manifest
            manifest_path = pkg_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))
            
            # Create tar.gz
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(pkg_dir, arcname=self.skill_name)
        
        print(f"{Colors.GREEN}✓{Colors.ENDC} Packaged '{self.skill_name}' to {output_path}")
        print(f"  Size: {self._format_size(output_path.stat().st_size)}")
        
        # Add to registry if requested
        if include_registry:
            self._add_to_registry(manifest, output_path)
        
        return output_path
    
    def _create_manifest(self) -> dict:
        """Create package manifest from SKILL.md."""
        skill_md = self.skill_dir / "SKILL.md"
        manifest = {
            "name": self.skill_name,
            "version": "1.0.0",
            "description": "",
            "author": "unknown",
            "license": "MIT",
            "created": datetime.now().isoformat(),
            "dependencies": [],
            "tags": [],
            "files": []
        }
        
        if skill_md.exists():
            content = skill_md.read_text()
            
            # Parse frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    
                    # Extract fields
                    for key in ["name", "version", "description", "author"]:
                        match = re.search(rf"^{key}\s*:\s*(.+)$", frontmatter, re.MULTILINE)
                        if match:
                            manifest[key] = match.group(1).strip()
                    
                    # Extract lists
                    for key in ["dependencies", "tags"]:
                        match = re.search(rf"^{key}\s*:\s*(.+)$", frontmatter, re.MULTILINE)
                        if match:
                            value = match.group(1).strip()
                            manifest[key] = [v.strip().strip('[]"') for v in value.strip("[]").split(",") if v.strip()]
        
        # List all files
        for root, dirs, files in os.walk(self.skill_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.startswith('.'):
                    filepath = Path(root) / file
                    rel_path = filepath.relative_to(self.skill_dir)
                    manifest["files"].append(str(rel_path))
        
        return manifest
    
    def _copy_skill_files(self, dest_dir: Path):
        """Copy skill files to destination."""
        for item in self.skill_dir.iterdir():
            if item.name.startswith('.'):
                continue
            
            dest = dest_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns('.*'))
            else:
                shutil.copy2(item, dest)
    
    def _add_to_registry(self, manifest: dict, package_path: Path):
        """Add skill to local registry."""
        registry = {"skills": []}
        if REGISTRY_PATH.exists():
            registry = json.loads(REGISTRY_PATH.read_text())
        
        # Update or add entry
        entry = {
            "name": manifest["name"],
            "version": manifest["version"],
            "description": manifest["description"],
            "author": manifest["author"],
            "tags": manifest.get("tags", []),
            "path": str(package_path.resolve()),
            "installed": False
        }
        
        # Replace existing or add new
        existing = [s for s in registry["skills"] if s["name"] == entry["name"]]
        if existing:
            registry["skills"].remove(existing[0])
        
        registry["skills"].append(entry)
        
        # Save registry
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_text(json.dumps(registry, indent=2))
        
        print(f"{Colors.BLUE}ℹ{Colors.ENDC} Added to registry")
    
    def _format_size(self, size: int) -> str:
        """Format file size."""
        for unit in ['B', 'KB', 'MB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"

class SkillInstaller:
    def __init__(self, force: bool = False, install_deps: bool = False):
        self.force = force
        self.install_deps = install_deps
    
    def install_from_file(self, file_path: Path) -> bool:
        """Install skill from .skill file."""
        if not file_path.exists():
            print(f"{Colors.FAIL}✗{Colors.ENDC} File not found: {file_path}")
            return False
        
        # Check if valid tar.gz
        try:
            with tarfile.open(file_path, "r:gz") as tar:
                # Extract manifest
                manifest_member = None
                for member in tar.getmembers():
                    if member.name.endswith("manifest.json"):
                        manifest_member = member
                        break
                
                if not manifest_member:
                    print(f"{Colors.FAIL}✗{Colors.ENDC} Invalid .skill file: no manifest.json found")
                    return False
                
                manifest_file = tar.extractfile(manifest_member)
                manifest = json.loads(manifest_file.read())
                skill_name = manifest["name"]
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Failed to read .skill file: {e}")
            return False
        
        # Check if already installed
        target_dir = SKILLS_DIR / skill_name
        if target_dir.exists():
            if not self.force:
                print(f"{Colors.WARNING}⚠{Colors.ENDC} Skill '{skill_name}' already installed. Use --force to overwrite.")
                return False
            print(f"{Colors.BLUE}ℹ{Colors.ENDC} Removing existing installation...")
            shutil.rmtree(target_dir)
        
        # Extract skill
        try:
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(SKILLS_DIR)
            
            print(f"{Colors.GREEN}✓{Colors.ENDC} Installed '{skill_name}'")
            
            # Install dependencies if requested
            if self.install_deps and manifest.get("dependencies"):
                self._install_dependencies(manifest["dependencies"])
            
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Installation failed: {e}")
            return False
    
    def install_from_url(self, url: str) -> bool:
        """Download and install skill from URL."""
        import urllib.request
        
        print(f"{Colors.BLUE}ℹ{Colors.ENDC} Downloading from {url}...")
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".skill", delete=False) as tmp:
                urllib.request.urlretrieve(url, tmp.name)
                return self.install_from_file(Path(tmp.name))
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Download failed: {e}")
            return False
    
    def install_from_git(self, git_url: str) -> bool:
        """Clone and install skill from git repository."""
        print(f"{Colors.BLUE}ℹ{Colors.ENDC} Cloning from {git_url}...")
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Clone repository
                result = subprocess.run(
                    ["git", "clone", git_url, tmpdir],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"{Colors.FAIL}✗{Colors.ENDC} Git clone failed: {result.stderr}")
                    return False
                
                # Find skill directory (look for SKILL.md)
                skill_dir = None
                for item in Path(tmpdir).iterdir():
                    if (item / "SKILL.md").exists():
                        skill_dir = item
                        break
                
                if not skill_dir:
                    print(f"{Colors.FAIL}✗{Colors.ENDC} No SKILL.md found in repository")
                    return False
                
                # Package and install
                packager = SkillPackager(skill_dir)
                with tempfile.NamedTemporaryFile(suffix=".skill", delete=False) as tmp:
                    package_path = packager.package(Path(tmp.name))
                    return self.install_from_file(package_path)
                    
        except Exception as e:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Installation failed: {e}")
            return False
    
    def _install_dependencies(self, dependencies: list):
        """Install skill dependencies."""
        print(f"{Colors.BLUE}ℹ{Colors.ENDC} Installing dependencies...")
        for dep in dependencies:
            print(f"  - {dep}")
            # TODO: Implement dependency resolution

def main():
    parser = argparse.ArgumentParser(description="Package and install OpenClaw skills")
    subparsers = parser.add_subparsers(dest="command")
    
    # Package command
    package_parser = subparsers.add_parser("package", help="Package a skill")
    package_parser.add_argument("--skill", required=True, help="Skill to package")
    package_parser.add_argument("--output", help="Output file path")
    package_parser.add_argument("--include-registry", action="store_true", help="Include in registry")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install a skill")
    install_parser.add_argument("--file", help="Path to .skill file")
    install_parser.add_argument("--url", help="URL to download .skill file")
    install_parser.add_argument("--git", help="Git repository URL")
    install_parser.add_argument("--force", action="store_true", help="Force overwrite")
    install_parser.add_argument("--deps", action="store_true", help="Install dependencies")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "package":
        skill_dir = SKILLS_DIR / args.skill
        if not skill_dir.exists():
            print(f"Error: Skill '{args.skill}' not found", file=sys.stderr)
            sys.exit(1)
        
        output = Path(args.output) if args.output else None
        packager = SkillPackager(skill_dir)
        packager.package(output, args.include_registry)
    
    elif args.command == "install":
        installer = SkillInstaller(force=args.force, install_deps=args.deps)
        
        success = False
        if args.file:
            success = installer.install_from_file(Path(args.file))
        elif args.url:
            success = installer.install_from_url(args.url)
        elif args.git:
            success = installer.install_from_git(args.git)
        else:
            print("Error: Please specify --file, --url, or --git", file=sys.stderr)
            sys.exit(1)
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
