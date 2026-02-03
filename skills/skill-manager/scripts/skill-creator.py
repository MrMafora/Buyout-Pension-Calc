#!/usr/bin/env python3
"""
Skill Creator - Create new skills from templates
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
TEMPLATES_DIR = SKILLS_DIR / "skill-manager" / "templates"

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class SkillCreator:
    def __init__(self, name: str, description: str, template: str):
        self.name = self._sanitize_name(name)
        self.description = description
        self.template = template
        self.skill_dir = SKILLS_DIR / self.name
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize skill name."""
        # Remove skill- prefix if present
        name = re.sub(r'^skill[-_]', '', name, flags=re.IGNORECASE)
        # Replace spaces and invalid chars with hyphens
        name = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
        # Lowercase
        name = name.lower()
        # Remove consecutive hyphens
        name = re.sub(r'-+', '-', name)
        # Strip leading/trailing hyphens
        name = name.strip('-')
        return name
    
    def create(self) -> bool:
        """Create new skill from template."""
        # Check if skill already exists
        if self.skill_dir.exists():
            print(f"{Colors.FAIL}✗{Colors.ENDC} Skill '{self.name}' already exists")
            return False
        
        # Create directory
        self.skill_dir.mkdir(parents=True)
        
        # Create based on template
        if self.template == "basic":
            self._create_basic_template()
        elif self.template == "python":
            self._create_python_template()
        elif self.template == "node":
            self._create_node_template()
        else:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Unknown template: {self.template}")
            return False
        
        print(f"{Colors.GREEN}✓{Colors.ENDC} Created skill '{self.name}' at {self.skill_dir}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.ENDC}")
        print(f"  1. Edit {self.skill_dir}/SKILL.md")
        print(f"  2. Add your scripts to {self.skill_dir}/scripts/")
        print(f"  3. Validate: python3 scripts/skill-manager.py validate --skill {self.name}")
        print(f"  4. Package: python3 scripts/skill-manager.py package --skill {self.name}")
        
        return True
    
    def _create_basic_template(self):
        """Create basic skill template."""
        # Create SKILL.md
        skill_md_content = f"""---
name: {self.name}
description: {self.description}
version: 1.0.0
author: Your Name
tags: []
dependencies: []
---

# {self.name.replace('-', ' ').title()}

{self.description}

## Quick Start

Describe how to use this skill quickly.

## Features

- Feature 1
- Feature 2
- Feature 3

## Usage

### Example Command

```bash
# Add example usage here
```

## Configuration

Describe any configuration options.

## Resources

List any resources or references.

## Changelog

### v1.0.0 ({datetime.now().strftime('%Y-%m-%d')})
- Initial release
"""
        
        (self.skill_dir / "SKILL.md").write_text(skill_md_content)
        
        # Create scripts directory
        scripts_dir = self.skill_dir / "scripts"
        scripts_dir.mkdir()
        
        # Create basic script
        script_content = f"""#!/usr/bin/env python3
\"\"\"
{self.name} - {self.description}
\"\"\"

import argparse

def main():
    parser = argparse.ArgumentParser(description="{self.description}")
    parser.add_argument("--example", help="Example argument")
    
    args = parser.parse_args()
    
    print("Hello from {self.name}!")
    
    if args.example:
        print(f"Example: {{args.example}}")

if __name__ == "__main__":
    main()
"""
        
        script_file = scripts_dir / "main.py"
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        
        # Create manifest.json
        manifest_content = f"""{{
  "name": "{self.name}",
  "version": "1.0.0",
  "description": "{self.description}",
  "author": "Your Name",
  "license": "MIT",
  "entryPoint": "scripts/main.py",
  "dependencies": [],
  "tags": []
}}
"""
        
        (self.skill_dir / "manifest.json").write_text(manifest_content)
    
    def _create_python_template(self):
        """Create Python-focused skill template."""
        self._create_basic_template()
        
        # Add additional Python-specific files
        scripts_dir = self.skill_dir / "scripts"
        
        # Create requirements.txt
        requirements = """# Python dependencies for this skill
# Add your dependencies here
# Example:
# requests>=2.28.0
"""
        (self.skill_dir / "requirements.txt").write_text(requirements)
        
        # Create utils.py
        utils_content = """#!/usr/bin/env python3
\"\"\"
Utility functions for this skill
\"\"\"

def load_config():
    \"\"\"Load skill configuration.\"\"\"
    return {}

def save_data(data, filename):
    \"\"\"Save data to file.\"\"\"
    import json
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_data(filename):
    \"\"\"Load data from file.\"\"\"
    import json
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
"""
        
        utils_file = scripts_dir / "utils.py"
        utils_file.write_text(utils_content)
        utils_file.chmod(0o644)
    
    def _create_node_template(self):
        """Create Node.js skill template."""
        # Create SKILL.md
        skill_md_content = f"""---
name: {self.name}
description: {self.description}
version: 1.0.0
author: Your Name
tags: [nodejs]
dependencies: []
---

# {self.name.replace('-', ' ').title()}

{self.description}

## Quick Start

```bash
cd scripts
npm install
node main.js
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Usage

### Example Command

```bash
node scripts/main.js --example value
```

## Configuration

Describe any configuration options.
"""
        
        (self.skill_dir / "SKILL.md").write_text(skill_md_content)
        
        # Create scripts directory
        scripts_dir = self.skill_dir / "scripts"
        scripts_dir.mkdir()
        
        # Create package.json
        package_json = f"""{{
  "name": "{self.name}",
  "version": "1.0.0",
  "description": "{self.description}",
  "main": "main.js",
  "scripts": {{
    "start": "node main.js",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  }},
  "keywords": [],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {{}}
}}
"""
        
        (scripts_dir / "package.json").write_text(package_json)
        
        # Create main.js
        main_js = f"""#!/usr/bin/env node
/**
 * {self.name} - {self.description}
 */

const args = process.argv.slice(2);

function main() {{
  console.log('Hello from {self.name}!');
  
  // Parse arguments
  const exampleIndex = args.indexOf('--example');
  if (exampleIndex !== -1 && args[exampleIndex + 1]) {{
    console.log(`Example: ${{args[exampleIndex + 1]}}`);
  }}
}}

main();
"""
        
        main_file = scripts_dir / "main.js"
        main_file.write_text(main_js)
        main_file.chmod(0o755)
        
        # Create manifest.json
        manifest_content = f"""{{
  "name": "{self.name}",
  "version": "1.0.0",
  "description": "{self.description}",
  "author": "Your Name",
  "license": "MIT",
  "entryPoint": "scripts/main.js",
  "dependencies": [],
  "tags": ["nodejs"]
}}
"""
        
        (self.skill_dir / "manifest.json").write_text(manifest_content)

def main():
    parser = argparse.ArgumentParser(description="Create a new OpenClaw skill")
    parser.add_argument("--name", required=True, help="Skill name")
    parser.add_argument("--description", default="A new OpenClaw skill", help="Skill description")
    parser.add_argument("--template", choices=["basic", "python", "node"], default="basic", help="Template to use")
    
    args = parser.parse_args()
    
    creator = SkillCreator(args.name, args.description, args.template)
    success = creator.create()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
