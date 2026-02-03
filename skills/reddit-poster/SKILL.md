---
name: reddit-poster
description: Post content to Reddit subreddits. Use when you need to share FedBuyOut content on Reddit for marketing, engagement, or community participation. Supports r/fednews, r/govfire, r/federalemployees, and other federal employee communities.
---

# Reddit Poster Skill

Post FedBuyOut marketing content to Reddit subreddits.

## When to Use

- Sharing calculator updates
- Answering buyout questions
- Posting federal employee news
- Engaging with target communities
- Driving traffic to FedBuyOut

## Target Subreddits

### Primary
- r/fednews - Federal employee news
- r/govfire - Government financial independence
- r/federalemployees - Federal worker discussions
- r/personalfinance - When relevant

### Secondary
- r/tsp - Thrift Savings Plan specific
- r/fers - FERS retirement
- r/csrs - CSRS retirement

## Best Practices

1. **Be helpful first** - Answer questions genuinely
2. **Don't spam** - Only post when relevant
3. **Follow subreddit rules** - Check sidebar before posting
4. **Use appropriate flair** - If required by subreddit
5. **Engage with comments** - Respond to questions

## Post Templates

### Educational Post
```
Title: I built a free federal buyout calculator - would love feedback

Content:
Hi everyone! I'm a [federal employee/developer/financial advisor] and I noticed a lot of confusion around buyout offers vs pension benefits.

I built a free calculator that compares:
- FERS/CSRS pension calculations
- Buyout tax implications
- Break-even analysis
- Early retirement penalties

Check it out here: https://fedbuyout.com

Would love any feedback or suggestions for features you'd find helpful!
```

### News Sharing Post
```
Title: [FedSmith Article] TSP Performance January 2026

Content:
Great news for federal employees - all TSP funds showed positive returns in January 2026.

Full article: [link]

If you're considering a buyout, this might be a good time to check how your retirement savings are tracking. I built a calculator that can help you compare buyout offers vs your pension: https://fedbuyout.com
```

### Question Answering
```
Title: RE: Should I take the buyout?

Content:
Great question! A few things to consider:

1. Calculate your pension at current years of service
2. Factor in early retirement penalties if under MRA
3. Consider the tax hit on the buyout (it's taxed as income)
4. Run a break-even analysis

I built a tool that does all this automatically: https://fedbuyout.com

Happy to answer any specific questions about your situation!
```

## Commands

### Check current posts
```bash
# List recent posts in a subreddit
curl -s "https://www.reddit.com/r/fednews/new.json?limit=10" -A "FedBuyOutBot/1.0" | jq -r '.data.children[].data.title'
```

### Post content (manual approach)
```bash
./scripts/reddit-post.sh "subreddit" "title" "content"
```

This outputs formatted content ready for manual posting.

## Automation Note

Full automation requires:
1. Reddit API credentials (app registration)
2. OAuth2 authentication flow
3. Refresh token management
4. Rate limiting compliance

For now, use browser automation or manual posting.

## Metrics to Track

- Post upvotes
- Comment engagement
- Click-through to FedBuyOut
- New subscribers from Reddit
- Lead conversions

## Weekly Schedule

- **Monday**: Educational post in r/fednews
- **Wednesday**: Answer questions in r/govfire
- **Friday**: Share relevant news article
- **Daily**: Monitor mentions and respond

## Compliance

- Follow Reddit's self-promotion guidelines (9:1 ratio)
- Never use multiple accounts
- Don't upvote your own posts
- Respect subreddit-specific rules
