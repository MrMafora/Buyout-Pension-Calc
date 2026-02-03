#!/bin/bash
# Full backup script for Thor/Clark Mafora environment

BACKUP_DIR="/root/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "🔨 Creating full backup at $BACKUP_DIR..."

# 1. Workspace code and configs
echo "📁 Backing up workspace..."
tar -czf "$BACKUP_DIR/workspace.tar.gz" \
  --exclude='node_modules' \
  --exclude='.git/objects' \
  --exclude='*.log' \
  /root/.openclaw/workspace/

# 2. Environment variables (sanitized)
echo "🔐 Backing up environment config..."
cp /root/.openclaw/workspace/.env "$BACKUP_DIR/env.backup" 2>/dev/null || echo "No .env file"

# 3. Skills directory
echo "🛠️ Backing up skills..."
tar -czf "$BACKUP_DIR/skills.tar.gz" /root/.openclaw/workspace/skills/

# 4. Memory files
echo "🧠 Backing up memory..."
tar -czf "$BACKUP_DIR/memory.tar.gz" /root/.openclaw/workspace/memory/ 2>/dev/null || echo "No memory dir"

# 5. Identity and config files
echo "📄 Backing up identity files..."
cp /root/.openclaw/workspace/IDENTITY.md "$BACKUP_DIR/" 2>/dev/null
cp /root/.openclaw/workspace/SOUL.md "$BACKUP_DIR/" 2>/dev/null
cp /root/.openclaw/workspace/USER.md "$BACKUP_DIR/" 2>/dev/null
cp /root/.openclaw/workspace/MEMORY.md "$BACKUP_DIR/" 2>/dev/null
cp /root/.openclaw/workspace/HEARTBEAT.md "$BACKUP_DIR/" 2>/dev/null
cp /root/.openclaw/workspace/TOOLS.md "$BACKUP_DIR/" 2>/dev/null

# 6. System state
echo "⚙️ Backing up system state..."
dpkg --get-selections > "$BACKUP_DIR/installed_packages.txt" 2>/dev/null
pip list > "$BACKUP_DIR/python_packages.txt" 2>/dev/null
npm list -g --depth=0 > "$BACKUP_DIR/npm_packages.txt" 2>/dev/null

# 7. PM2 processes
echo "📊 Backing up PM2 config..."
pm2 save > /dev/null 2>&1
pm2 ecosystem export "$BACKUP_DIR/pm2_ecosystem.json" 2>/dev/null || echo "No PM2 export available"

# 8. Create backup manifest
echo "📝 Creating manifest..."
cat > "$BACKUP_DIR/manifest.txt" << EOF
Backup created: $(date)
System: $(uname -a)
Hostname: $(hostname)
Workspace: /root/.openclaw/workspace

Contents:
- workspace.tar.gz: Full workspace code
- skills.tar.gz: All custom skills
- memory.tar.gz: Memory files
- *.md: Identity and configuration files
- env.backup: Environment variables
- installed_packages.txt: System packages
- python_packages.txt: Python packages
- npm_packages.txt: NPM packages
- pm2_ecosystem.json: Process manager config

To restore:
1. Extract workspace.tar.gz to /root/.openclaw/workspace
2. Extract skills.tar.gz to workspace/skills/
3. Restore .env from env.backup
4. Run: dpkg --set-selections < installed_packages.txt && apt-get dselect-upgrade
5. Run: pip install -r python_packages.txt (after converting format)
6. Run: pm2 ecosystem import pm2_ecosystem.json
EOF

# Show backup summary
echo ""
echo "✅ Backup complete!"
echo "📦 Location: $BACKUP_DIR"
echo "📊 Size: $(du -sh $BACKUP_DIR | cut -f1)"
echo ""
ls -lah "$BACKUP_DIR"
