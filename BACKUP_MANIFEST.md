# FedBuyOut System Backup Manifest
Generated: 2026-02-02 04:22 UTC

## GitHub Repository
URL: https://github.com/MrMafora/Buyout-Pension-Calc
Status: ✅ Up to date with origin/main

## Server Infrastructure
- **IP**: 143.110.225.185
- **Domain**: https://fedbuyout.com
- **SSL**: Let's Encrypt (valid until May 2026)
- **OS**: Ubuntu 24.04.3 LTS

## Core Services
| Service | Status | Port |
|---------|--------|------|
| FedBuyOut App | ✅ Online (PM2) | 5000 |
| Nginx | ✅ Running | 80/443 |
| PostgreSQL | ✅ Running | 5432 |
| VNC | ✅ Running | 5901 |
| noVNC Web | ✅ Running | 6080 |

## Installed Skills (OpenClaw)
- ✅ bird (Twitter/X CLI)
- ✅ blogwatcher (News monitoring)
- ✅ reddit-poster (Custom workspace skill)
- ✅ github (GitHub CLI)
- ✅ canvas (Browser automation)
- ✅ weather (Forecasts)

## Content Created
### SEO Blog Posts
1. article-1-fers-vs-csrs.md (6,200 words)
2. article-2-should-i-take-buyout.md (8,000 words)
3. article-3-buyout-tax-implications.md (9,500 words)

### Automation Scripts
- daily-twitter-post.sh (10 rotating tweets)
- weekly-reddit-post.sh (3 subreddits rotation)
- Cron jobs configured for daily/weekly execution

### Marketing Content
- MARKETING_CONTENT_LIBRARY.md (Reddit/Twitter/LinkedIn posts)
- SEO_CONTENT_PLAN.md (7 articles planned)
- ADVISOR_OUTREACH_PLAN.md (Lead buyer strategy)

## System Configuration
### VNC Setup
- Desktop: Openbox (lightweight, reliable)
- Display: :1 (1280x720)
- Access: http://143.110.225.185:6080/vnc.html
- Password: @G0its30

### Chrome Profile
- Location: /tmp/chrome_twitter/
- Status: Logged into Twitter as @FedBuyOut
- Purpose: Cookie extraction for automation

## Credentials (Server-side only)
- Admin Panel: fboadmin / @G0its30n3m
- Gmail: fedbuyout@gmail.com (browser authenticated)
- Database: fedbuyout / fedbuyout_secure_2026
- VNC: @G0its30

## What's Working
✅ Website live and SSL-secured
✅ PWA installable on mobile
✅ Email system (Resend) active
✅ Google Analytics tracking
✅ Blogwatcher monitoring 4 news sources
✅ Daily cron jobs scheduled
✅ Twitter account created
✅ 3 SEO articles published
✅ GitHub repo current

## What's Pending
⏳ Twitter cookie extraction (Chrome encryption issue)
⏳ First automated tweet via bird CLI
⏳ Reddit posting (manual for now)
⏳ Lead buyer outreach (50 advisors to research)
⏳ GitHub token rotation (security)

## Backup Strategy
1. GitHub: All code, content, configs pushed
2. Daily: Marketing content auto-generated
3. Weekly: Cron jobs rotate Reddit posts
4. Database: PostgreSQL dumps (manual)
5. Secrets: Environment variables (not in git)

## Recovery Steps
If server fails:
1. Clone repo: git clone https://github.com/MrMafora/Buyout-Pension-Calc
2. Install deps: npm install
3. Setup DB: postgresql + restore dump
4. Copy .env.production (from secure backup)
5. Build: npm run build
6. Start: pm2 start ecosystem.config.cjs
7. Setup VNC + Chrome for automation

## Next Session Priorities
1. Extract Twitter cookies for bird CLI
2. Test automated daily tweet
3. Research 50 fee-only advisors
4. Post first Reddit thread manually
5. Monitor FedBuyOut traffic in GA4

---
Last updated: Thor (Clark) for Odin
