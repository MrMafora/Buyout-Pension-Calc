# Thor (Clark) Migration Guide: Linux VPS → MacBook Pro

**Date:** 2026-02-03  
**From:** DigitalOcean VPS (Ubuntu 24.04)  
**To:** MacBook Pro (macOS Sonoma/Sequoia)  
**Estimated Time:** 30-45 minutes

---

## Why Migrate to MacBook Pro?

| Feature | VPS (Current) | MacBook Pro |
|---------|--------------|-------------|
| **Display** | Headless/VNC issues | Native Retina display |
| **Browser Automation** | Cookie extraction blocked | Full Chrome/Safari control |
| **GUI Reliability** | Gray screens, crashes | Stable macOS desktop |
| **Automation** | Limited headless tools | AppleScript, Shortcuts, GUI scripting |
| **Notifications** | None | Native macOS notifications |
| **Accessibility** | Complex setup | Built-in macOS permissions |
| **Offline Capability** | Requires internet | Can work locally |

**Bottom Line:** On MacBook, I can truly operate autonomously without manual intervention.

---

## Phase 1: Prerequisites (5 min)

### System Requirements
- **macOS:** Sonoma (14.x) or Sequoia (15.x)
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 10GB free space
- **Internet:** For initial setup and API calls

### Install Homebrew
```bash
# Open Terminal on MacBook
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Install Node.js 22.x
```bash
brew install node@22
brew link node@22 --force
```

---

## Phase 2: Install OpenClaw (5 min)

```bash
# Install OpenClaw globally
npm install -g openclaw

# Verify installation
openclaw --version

# Start OpenClaw gateway
openclaw gateway start
```

### Configure OpenClaw
```bash
# Edit config (creates if not exists)
openclaw config edit
```

Add this basic config:
```json
{
  "channel": {
    "whatsapp": {
      "enabled": true
    }
  },
  "browser": {
    "enabled": true,
    "profile": "chrome"
  }
}
```

---

## Phase 3: Restore Thor's State (10 min)

### 1. Clone Agent State Repository
```bash
cd ~/Documents
mkdir -p OpenClaw
 cd OpenClaw

# Clone my complete state
git clone https://github.com/MrMafora/thor-openclaw-state.git
cd thor-openclaw-state
```

### 2. Restore Workspace
```bash
# Create OpenClaw workspace
mkdir -p ~/.openclaw/workspace

# Copy identity files
cp AGENTS.md SOUL.md IDENTITY.md USER.md TOOLS.md HEARTBEAT.md MEMORY.md ~/.openclaw/workspace/

# Copy memory logs
mkdir -p ~/.openclaw/workspace/memory
cp memory-backup/*.md ~/.openclaw/workspace/memory/ 2>/dev/null || true

# Copy custom skills
mkdir -p ~/.openclaw/skills
cp -r custom-skills/* ~/.openclaw/skills/ 2>/dev/null || true

# Copy config
cp openclaw.json ~/.openclaw/ 2>/dev/null || true
```

### 3. Restore FedBuyOut Project
```bash
cd ~/Documents/OpenClaw

# Clone FedBuyOut
git clone https://github.com/MrMafora/Buyout-Pension-Calc.git fedbuyout
cd fedbuyout

# Install dependencies
npm install

# Copy environment template (you'll fill in secrets)
cp .env.template .env
```

---

## Phase 4: Install Mac-Specific Skills (10 min)

### Core CLI Tools
```bash
# Install essential tools
brew install git gh ffmpeg imagemagick

# Install browser automation
brew install --cask google-chrome

# Install Twitter CLI
npm install -g @steipete/bird

# Install email client
brew install himalaya

# Install other useful tools
brew install tmux jq tree
```

### macOS-Specific Skills
```bash
# Install OpenClaw skills available on macOS
openclaw skill:install bird
openclaw skill:install github
openclaw skill:install blogwatcher
openclaw skill:install canvas
openclaw skill:install slack
openclaw skill:install discord
openclaw skill:install notion
openclaw skill:install obsidian
openclaw skill:install apple-notes
openclaw skill:install apple-reminders
```

### Optional AI Tools
```bash
# OpenAI tools (requires API key)
npm install -g openai

# Image generation
openclaw skill:install openai-image-gen
```

---

## Phase 5: Configure macOS Permissions (5 min)

### Enable Required Permissions

1. **Open System Settings** → **Privacy & Security**

2. **Screen Recording:**
   - Add Terminal (or iTerm)
   - Add Chrome

3. **Accessibility:**
   - Add Terminal (for GUI automation)
   - Add Chrome

4. **Automation:**
   - Allow Terminal to control System Events
   - Allow Terminal to control Chrome

5. **Full Disk Access** (optional):
   - Add Terminal if needed for file operations

### Grant Permissions via Command Line
```bash
# Note: Some permissions require GUI approval
tccutil reset ScreenCapture
```

---

## Phase 6: Setup Browser Automation (5 min)

### Chrome Setup for Twitter
```bash
# Launch Chrome (creates profile)
open -a "Google Chrome"

# Login to Twitter manually first (one time)
# I can then use the profile for automation
```

### Configure Bird (Twitter CLI)
```bash
# Bird will automatically use Chrome cookies on Mac
bird check

# Should show: ✅ Chrome cookies found
```

### Test Browser Automation
```bash
# I can now automate Chrome on macOS
openclaw browser start --profile chrome
```

---

## Phase 7: Restore Services (5 min)

### PostgreSQL (if needed locally)
```bash
brew install postgresql@16
brew services start postgresql@16

# Create database
createdb fedbuyout
```

### PM2 (Process Manager)
```bash
npm install -g pm2

# Start FedBuyOut
cd ~/Documents/OpenClaw/fedbuyout
pm2 start ecosystem.config.cjs
```

### Cron Jobs
```bash
# Import cron jobs from backup
cat ~/Documents/OpenClaw/thor-openclaw-state/cron-jobs.json

# Recreate using openclaw cron or macOS launchd
```

---

## Phase 8: Test & Verify (5 min)

### Test 1: Basic Functionality
```bash
# Check OpenClaw status
openclaw status

# Test browser
openclaw browser open https://fedbuyout.com
```

### Test 2: Twitter Automation
```bash
# This should work now with Mac Chrome cookies
bird tweet "Testing Thor on MacBook Pro! 🍎⚡"
```

### Test 3: GUI Automation
```bash
# Test macOS native automation
openclaw canvas screenshot
```

### Test 4: WhatsApp Connection
```bash
# Should auto-reconnect
openclaw channel whatsapp status
```

---

## Phase 9: Copy Secrets (Manual)

**Copy these from old server or secure backup:**

### Environment Variables (~/.zshrc or ~/.bash_profile)
```bash
# FedBuyOut secrets
export DATABASE_URL="postgresql://fedbuyout:PASSWORD@localhost:5432/fedbuyout"
export RESEND_API_KEY="re_..."
export ADMIN_PASSWORD="..."

# Twitter (if using API)
export TWITTER_API_KEY="..."
export TWITTER_API_SECRET="..."
export TWITTER_ACCESS_TOKEN="..."
export TWITTER_ACCESS_SECRET="..."

# OpenAI (optional)
export OPENAI_API_KEY="sk-..."

# GitHub token
export GH_TOKEN="ghp_..."
```

### VNC Password (no longer needed on Mac!)
- Delete: `@G0its30` (not needed with native display)

---

## Phase 10: Final Verification

### Checklist
- [ ] OpenClaw running
- [ ] Gateway started
- [ ] WhatsApp connected
- [ ] Chrome automation working
- [ ] Twitter can post
- [ ] FedBuyOut website accessible
- [ ] Cron jobs scheduled
- [ ] All skills installed

### First Automated Tasks (I'll do these)
1. ✅ Post to Twitter
2. ✅ Post to Reddit
3. ✅ Check Gmail
4. ✅ Monitor FedBuyOut analytics
5. ✅ Run news scan

---

## What's Different on MacBook

### Better Capabilities
- **Native GUI:** No VNC needed, direct screen access
- **Browser Control:** Full Chrome/Safari automation
- **Notifications:** Native macOS alerts
- **Shortcuts:** Apple Shortcuts integration
- **File Management:** Native Finder automation
- **Reliability:** No more gray screens or crashes

### New Possibilities
- Control any Mac app (Numbers, Pages, Mail)
- Use AppleScript for advanced automation
- iCloud integration
- AirDrop for file sharing
- FaceTime/screen sharing with you
- Local ML models (Core ML)

---

## Rollback Plan

If something goes wrong:
1. Keep VPS running until Mac is verified
2. Can run both in parallel
3. DNS points to VPS until Mac is ready
4. Switch DNS when confirmed working

---

## Support

**Issues?**
- Check: `openclaw logs`
- Verify: `openclaw doctor`
- Reset: Delete `~/.openclaw/` and restore from backup

**Contact:**
- WhatsApp: +27812857015
- GitHub: https://github.com/MrMafora/thor-openclaw-state

---

## Summary

| Task | Time |
|------|------|
| Install prerequisites | 5 min |
| Install OpenClaw | 5 min |
| Restore state | 10 min |
| Install skills | 10 min |
| Configure permissions | 5 min |
| Setup browser | 5 min |
| Test & verify | 5 min |
| **Total** | **~45 min** |

**After migration:** I run fully autonomously on your MacBook! 🍎⚡

---

*Prepared by Thor (Clark) for Odin*  
*Migration Date: 2026-02-03*
