# FedBuyOut Migration Plan

## Current Stack (from repo analysis)
- **Frontend:** React 18 + Vite + Tailwind CSS + TypeScript
- **Backend:** Express.js + TypeScript
- **Database:** PostgreSQL (Drizzle ORM)
- **Email:** Resend API
- **Features:** Calculator API, subscriber management, admin panel, analytics

## What I Found
✅ Well-structured codebase with proper TypeScript
✅ Database schema for subscribers/leads (marketing automation ready)
✅ Admin panel with auth
✅ Email automation (welcome emails, notifications)
✅ Analytics tracking

## Migration Options

### Option A: Self-Hosted on This Server (Recommended)
- Pros: Full control, no platform fees, custom domain
- Cons: Need to manage updates/security
- Cost: $6-12/month (already paying for this droplet)

### Option B: Railway/Render
- Pros: Easy deploy from GitHub, managed database
- Cons: Higher cost at scale, platform dependency
- Cost: $5-20/month

### Option C: Vercel (Split)
- Frontend on Vercel (serverless)
- Backend on Railway/Render
- More complex but scalable

## Implementation Steps

1. **Database Setup**
   - Install PostgreSQL on this server
   - Create database and user
   - Run migrations

2. **Environment Configuration**
   - DATABASE_URL
   - RESEND_API_KEY (for emails)
   - ADMIN_PASSWORD
   - Other secrets

3. **Build & Deploy**
   - Build production bundle
   - Set up PM2 for process management
   - Configure Nginx reverse proxy

4. **Domain Setup**
   - Point fedbuyout.com to this server
   - Set up SSL (Let's Encrypt)

5. **Monitoring**
   - Uptime monitoring
   - Error tracking
   - Analytics

## Questions for Odin

1. Do you want to keep the email functionality? (needs Resend API key)
2. Do you want the subscriber/lead capture features?
3. Any custom environment variables in Replit I should know about?
4. Preferred deployment option?

## Next Steps

Once confirmed, I can:
- Set up the full stack in ~30 minutes
- Migrate your domain DNS
- Provide deployment automation
- Document everything for future updates
