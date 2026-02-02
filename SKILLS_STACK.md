# FedBuyOut Skills Stack

## Installed & Ready Skills

### 1. 🐦 bird (Twitter/X)
- **Status:** ✅ Installed
- **Path:** `/usr/lib/node_modules/openclaw/skills/bird/`
- **Purpose:** Post to Twitter, read timeline, search
- **CLI:** `bird tweet "message"`
- **Needs:** Authentication (auth_token, ct0 cookies)

### 2. 📰 blogwatcher (News Monitoring)
- **Status:** ✅ Installed
- **Path:** `/usr/lib/node_modules/openclaw/skills/blogwatcher/`
- **Purpose:** Monitor federal employee news sources
- **Sources:** FedSmith, Federal News Network, GovExec, NARFE
- **Usage:** `blogwatcher list --unread`

### 3. 📱 reddit-poster (Custom)
- **Status:** ✅ Created in workspace
- **Path:** `/root/.openclaw/workspace/skills/reddit-poster/`
- **Purpose:** Post to r/fednews, r/govfire, r/federalemployees
- **Templates:** Ready in `/references/`

### 4. 🐙 github (GitHub CLI)
- **Status:** ✅ Available
- **Path:** `/usr/lib/node_modules/openclaw/skills/github/`
- **Purpose:** GitHub issues, PRs, repository management
- **CLI:** `gh issue list`, `gh pr create`
- **Needs:** `gh` CLI installed

### 5. 🌐 canvas (Browser)
- **Status:** ✅ Available
- **Path:** `/usr/lib/node_modules/openclaw/skills/canvas/`
- **Purpose:** Browser automation, screenshots
- **Usage:** `canvas present <url>`

### 6. 📧 himalaya (Email)
- **Status:** ✅ Available
- **Path:** `/usr/lib/node_modules/openclaw/skills/himalaya/`
- **Purpose:** IMAP email management
- **CLI:** `himalaya list`, `himalaya write`
- **Needs:** IMAP configuration

### 7. 💬 slack (Notifications)
- **Status:** ✅ Available
- **Path:** `/usr/lib/node_modules/openclaw/skills/slack/`
- **Purpose:** Slack channel notifications
- **Needs:** Slack bot token

### 8. 🎭 discord (Community)
- **Status:** ✅ Available
- **Path:** `/usr/lib/node_modules/openclaw/skills/discord/`
- **Purpose:** Discord server integration
- **Needs:** Discord bot token

## Installation Status

| Skill | Priority | Status | Action |
|-------|----------|--------|--------|
| bird | HIGH | ✅ | Needs auth setup |
| reddit-poster | HIGH | ✅ | Ready to use |
| blogwatcher | HIGH | ✅ | Already running |
| github | MEDIUM | ⏳ | Install gh CLI |
| himalaya | MEDIUM | ⏳ | Install himalaya |
| canvas | LOW | ⏳ | Available |
| slack | LOW | ⏳ | Config needed |

## Next Steps

1. **Setup bird auth** - Extract Twitter cookies for automated posting
2. **Install gh CLI** - For GitHub automation
3. **Install himalaya** - For Gmail management
4. **Test all skills** - Verify each works with FedBuyOut workflows

## Usage Examples

```bash
# Twitter posting
bird tweet "New blog post: Should I take the federal buyout? https://fedbuyout.com"

# Check federal news
blogwatcher list --unread --tag federal

# GitHub management
gh issue create --title "Feature request" --body "Add military buyback calc"

# Email campaign
himalaya write --to subscribers@fedbuyout.com --subject "Weekly Fed News"
```
