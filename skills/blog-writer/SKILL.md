---
name: blog-writer
description: Generate SEO-optimized blog posts for FedBuyOut about VSIP, federal employee benefits, and buyouts. Use when creating content for federal employees considering early retirement, voluntary separation incentives, or career transitions. Supports how-to guides, comparisons, news analysis, and case studies with proper SEO structure and conversion-focused CTAs.
---

# Blog Writer for FedBuyOut

Create compelling, SEO-optimized blog content for federal employees exploring VSIP, buyouts, and early retirement options.

## Quick Start

1. **Choose blog type** → See [references/blog-types.md](references/blog-types.md)
2. **Select template** → Copy from [assets/templates/](assets/templates/)
3. **Generate content** → Use scripts or manual workflow below
4. **Add CTAs** → See [references/cta-templates.md](references/cta-templates.md)

## Blog Types

| Type | Best For | See |
|------|----------|-----|
| How-To Guide | Step-by-step instructions | `references/blog-types.md#how-to` |
| Comparison | VSIP vs other options | `references/blog-types.md#comparison` |
| News/Analysis | Policy updates, deadlines | `references/blog-types.md#news` |
| Case Study | Success stories | `references/blog-types.md#case-study` |

## Content Generation Workflow

### Option 1: Use Generator Script (Recommended)

```bash
# Generate a complete blog post
python3 /root/.openclaw/workspace/skills/blog-writer/scripts/generate-blog.py --type how-to --topic "VSIP eligibility requirements"

# Generate with custom parameters
python3 /root/.openclaw/workspace/skills/blog-writer/scripts/generate-blog.py \
  --type comparison \
  --topic "VSIP vs VERA" \
  --tone educational \
  --word-count 1500
```

### Option 2: Manual Workflow

**Step 1: Research Keywords**
- Load [references/seo-keywords.md](references/seo-keywords.md)
- Identify primary and secondary keywords for topic
- Note search intent (informational, transactional, navigational)

**Step 2: Create Outline**
- Load [references/topic-ideas.md](references/topic-ideas.md) for inspiration
- Use [references/outline-templates.md](references/outline-templates.md)
- Include: Hook → Problem → Solution → Proof → CTA

**Step 3: Write with Template**
- Copy template from [assets/templates/](assets/templates/)
- Follow structure: Title → Meta → Intro → H2s → H3s → Conclusion → CTA
- Apply headline formulas from [references/headline-formulas.md](references/headline-formula.md)

**Step 4: Optimize for SEO**
- Primary keyword in title, first paragraph, at least one H2
- Secondary keywords naturally throughout
- Meta description 150-160 characters
- Internal links to related posts

**Step 5: Add CTAs**
- Load [references/cta-templates.md](references/cta-templates.md)
- Place primary CTA after intro and conclusion
- Add secondary CTAs mid-content where relevant

## SEO Best Practices

1. **Title Tag**: 50-60 characters, keyword first, compelling
2. **Meta Description**: 150-160 characters, include keyword, clear value proposition
3. **URL Slug**: Short, keyword-rich, hyphen-separated
4. **Headers**: One H1, logical H2/H3 hierarchy with keywords
5. **Internal Linking**: 2-4 links to related content
6. **Image Alt Text**: Descriptive, include keyword if natural
7. **Readability**: Short paragraphs (2-3 sentences), bullet points, subheadings every 300 words

## Tone Guidelines

- **Empathetic**: Federal employees face major decisions—acknowledge their concerns
- **Authoritative**: Cite OPM guidance, regulations, real examples
- **Clear**: Avoid jargon, explain acronyms on first use
- **Actionable**: Every post should leave reader with next steps
- **Urgent but Not Pushy**: Deadlines matter, but decisions are personal

## Content Calendar

See [references/content-calendar.md](references/content-calendar.md) for:
- Seasonal topics (fiscal year-end, open season)
- Recurring content themes
- Publishing frequency recommendations

## Post-Publishing Checklist

- [ ] Proofread for typos and clarity
- [ ] Verify all links work
- [ ] Check mobile formatting
- [ ] Add to content calendar log
- [ ] Schedule social media promotion
- [ ] Set reminder to update in 6 months

## Resources Quick Reference

| Resource | Use When |
|----------|----------|
| [references/topic-ideas.md](references/topic-ideas.md) | Need blog topic inspiration |
| [references/seo-keywords.md](references/seo-keywords.md) | Researching keywords for post |
| [references/outline-templates.md](references/outline-templates.md) | Creating post structure |
| [references/headline-formulas.md](references/headline-formulas.md) | Writing compelling titles |
| [references/cta-templates.md](references/cta-templates.md) | Adding conversion elements |
| [references/content-calendar.md](references/content-calendar.md) | Planning editorial calendar |
| [references/blog-types.md](references/blog-types.md) | Choosing content format |
| [assets/templates/](assets/templates/) | Starting new post from template |
| [scripts/generate-blog.py](scripts/generate-blog.py) | Automated content generation |
