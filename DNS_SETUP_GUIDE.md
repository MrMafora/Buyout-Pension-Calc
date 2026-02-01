# FedBuyOut DNS Setup Guide

## Current Status
- **Server IP:** 143.110.225.185
- **Current Domain:** fedbuyout.com
- **Current DNS:** Points to 34.111.179.208 (old Replit server)
- **Target DNS:** Should point to 143.110.225.185 (our server)

## DNS Records to Add

### Required A Records

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ (or fedbuyout.com) | 143.110.225.185 | 300 |
| A | www | 143.110.225.185 | 300 |

### Optional but Recommended

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| CNAME | app | fedbuyout.com | Alternative subdomain |
| TXT | @ | v=spf1 include:_spf.google.com ~all | Email SPF (when ready) |

## Step-by-Step Instructions

### 1. Find Your Domain Registrar
Common registrars:
- GoDaddy
- Namecheap
- Google Domains
- Cloudflare
- Domain.com
- Hostinger

### 2. Access DNS Management
1. Log into your registrar account
2. Find "DNS Management" or "Nameservers" or "DNS Zone"
3. Look for "Manage DNS" or "Advanced DNS"

### 3. Update A Records
1. Find existing A records for @ (root) and www
2. Edit them to point to: **143.110.225.185**
3. Set TTL to 300 (5 minutes) for quick propagation
4. Save changes

### 4. Remove Old Records (Important!)
Delete any A records pointing to:
- 34.111.179.208 (old Replit)
- Any other IPs not matching 143.110.225.185

### 5. Verify Changes
After updating, verify with:
```bash
# Check current DNS
dig fedbuyout.com
nslookup fedbuyout.com

# Should show: 143.110.225.185
```

Or use online tools:
- https://dnschecker.org/
- https://whatsmydns.net/

## Expected Timeline

| Stage | Time |
|-------|------|
| DNS Update | Immediate |
| Propagation | 5 minutes - 48 hours (usually 15-30 min) |
| SSL Certificate | Auto-generates within 1 hour of DNS working |
| Full HTTPS | Within 1-2 hours of DNS update |

## After DNS is Updated

I will automatically:
1. Generate SSL certificate (Let's Encrypt)
2. Configure HTTPS redirect
3. Test the site
4. Enable HTTP/2
5. Confirm PWA works over HTTPS

## Troubleshooting

### If site doesn't load after 1 hour:
1. Clear browser cache
2. Try incognito/private mode
3. Check DNS with: `dig fedbuyout.com +trace`
4. Verify no conflicting records exist

### If SSL fails:
1. Ensure DNS fully propagated
2. Check no firewall blocking port 443
3. Retry certbot manually

### Emergency Rollback:
If issues occur, you can revert DNS back to 34.111.179.208 while we troubleshoot.

## Next Steps After DNS

1. ✅ Test site loads at https://fedbuyout.com
2. ✅ Verify PWA install works
3. ✅ Set up business email
4. ✅ Begin marketing campaigns
5. ✅ Start lead generation

---

**Ready when you are, Odin. Just update those A records and I'll handle the rest!**
