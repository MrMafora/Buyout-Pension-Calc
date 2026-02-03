#!/usr/bin/env python3
"""
Blog Post Generator for FedBuyOut
Generates SEO-optimized blog posts about VSIP, federal benefits, and buyouts.
"""

import argparse
import sys
import json
from datetime import datetime
from pathlib import Path

# Templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "assets" / "templates"

def load_template(template_type):
    """Load a blog template by type."""
    template_file = TEMPLATES_DIR / f"{template_type}-template.md"
    if template_file.exists():
        return template_file.read_text()
    return None

def generate_slug(topic):
    """Generate URL-friendly slug from topic."""
    return topic.lower().replace(" ", "-").replace("/", "-").replace("'", "")[:60]

def generate_meta_description(topic, blog_type):
    """Generate meta description based on topic and type."""
    descriptions = {
        "how-to": f"Learn how to {topic.lower()} with this step-by-step guide for federal employees. Expert advice on navigating your VSIP options.",
        "comparison": f"Compare {topic.lower()} to make the best decision for your federal career. Detailed analysis of benefits and drawbacks.",
        "news": f"Stay informed about {topic.lower()}. What federal employees need to know about the latest policy changes and deadlines.",
        "case-study": f"Real story: How one federal employee navigated {topic.lower()}. Insights and lessons learned for your own decision."
    }
    return descriptions.get(blog_type, f"Expert guidance on {topic.lower()} for federal employees considering their options.")

def generate_headline(topic, blog_type, tone="educational"):
    """Generate headline using formulas."""
    formulas = {
        "how-to": [
            f"How to {topic}: A Complete Guide for Federal Employees",
            f"The Federal Employee's Guide to {topic}",
            f"{topic}: Step-by-Step Instructions for Federal Workers",
        ],
        "comparison": [
            f"{topic}: Which Is Right for Your Federal Career?",
            f"{topic} Compared: Making the Smart Choice",
            f"Choosing Between {topic}: A Federal Employee's Analysis",
        ],
        "news": [
            f"What Federal Employees Need to Know About {topic}",
            f"{topic}: Important Updates for Federal Workers",
            f"Breaking Down {topic} for Federal Employees",
        ],
        "case-study": [
            f"How One Federal Employee Successfully Navigated {topic}",
            f"Real Talk: A Federal Worker's Journey Through {topic}",
            f"From Decision to Action: A {topic} Case Study",
        ]
    }
    
    headlines = formulas.get(blog_type, [f"Understanding {topic}"])
    return headlines[0]  # Return first option as default

def generate_outline(blog_type, topic, word_count):
    """Generate blog outline based on type and word count."""
    
    base_outline = {
        "how-to": [
            "Introduction (Hook + Problem)",
            "What You'll Learn (Preview)",
            "Prerequisites/Eligibility",
            "Step 1: [First Action]",
            "Step 2: [Second Action]",
            "Step 3: [Third Action]",
            "Common Mistakes to Avoid",
            "Timeline and Deadlines",
            "What Happens Next",
            "Conclusion with CTA"
        ],
        "comparison": [
            "Introduction (The Decision Dilemma)",
            "Option A: Overview",
            "Option A: Pros and Cons",
            "Option B: Overview",
            "Option B: Pros and Cons",
            "Side-by-Side Comparison Table",
            "Key Factors to Consider",
            "Real-World Scenarios",
            "Expert Recommendation",
            "Conclusion with CTA"
        ],
        "news": [
            "Breaking News Summary",
            "Why This Matters to Federal Employees",
            "Key Details and Changes",
            "Timeline and Deadlines",
            "How This Affects Different Employee Types",
            "What Actions You Should Take",
            "Expert Analysis and Context",
            "Looking Ahead",
            "Conclusion with CTA"
        ],
        "case-study": [
            "Introduction (Meet the Employee)",
            "The Situation and Challenge",
            "The Decision Process",
            "Taking Action (Step by Step)",
            "Obstacles Encountered",
            "The Outcome",
            "Lessons Learned",
            "Key Takeaways for Readers",
            "Conclusion with CTA"
        ]
    }
    
    outline = base_outline.get(blog_type, base_outline["how-to"])
    
    # Adjust based on word count
    if word_count < 1000:
        # Remove some sections for shorter posts
        outline = [outline[0], outline[1], outline[2], "[Key Content]", outline[-2], outline[-1]]
    elif word_count > 2000:
        # Add more detail sections for longer posts
        outline.insert(-2, "Additional Resources")
        outline.insert(-2, "FAQ Section")
    
    return outline

def generate_blog_post(args):
    """Generate a complete blog post."""
    
    # Load template
    template = load_template(args.type)
    if not template:
        print(f"Error: Template for type '{args.type}' not found.")
        sys.exit(1)
    
    # Generate components
    headline = generate_headline(args.topic, args.type, args.tone)
    slug = generate_slug(args.topic)
    meta_desc = generate_meta_description(args.topic, args.type)
    outline = generate_outline(args.type, args.topic, args.word_count)
    
    # Calculate reading time (avg 250 wpm)
    reading_time = max(1, round(args.word_count / 250))
    
    # Current date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Replace template variables
    post = template
    post = post.replace("{{TITLE}}", headline)
    post = post.replace("{{SLUG}}", slug)
    post = post.replace("{{META_DESCRIPTION}}", meta_desc)
    post = post.replace("{{TOPIC}}", args.topic)
    post = post.replace("{{DATE}}", today)
    post = post.replace("{{READING_TIME}}", str(reading_time))
    post = post.replace("{{WORD_COUNT}}", str(args.word_count))
    
    # Generate outline section
    outline_text = "\n".join([f"- {item}" for item in outline])
    post = post.replace("{{OUTLINE}}", outline_text)
    
    # Generate placeholder sections based on word count
    section_count = len(outline) - 2  # Excluding intro and conclusion
    words_per_section = args.word_count // section_count
    
    content_sections = []
    for item in outline[1:-1]:  # Skip intro and conclusion for body
        if "[" in item:
            section_title = item.strip("[]")
            content_sections.append(f"\n## {section_title}\n\n[Write {words_per_section} words about {section_title.lower()} here. Include relevant details, examples, and actionable advice.]\n")
    
    post = post.replace("{{CONTENT_SECTIONS}}", "\n".join(content_sections))
    
    return post

def main():
    parser = argparse.ArgumentParser(
        description="Generate SEO-optimized blog posts for FedBuyOut"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["how-to", "comparison", "news", "case-study"],
        required=True,
        help="Type of blog post to generate"
    )
    parser.add_argument(
        "--topic", "-p",
        required=True,
        help="Main topic of the blog post"
    )
    parser.add_argument(
        "--tone", "-n",
        choices=["educational", "urgent", "empathetic", "authoritative"],
        default="educational",
        help="Tone of the blog post"
    )
    parser.add_argument(
        "--word-count", "-w",
        type=int,
        default=1200,
        help="Target word count (default: 1200)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: prints to stdout)"
    )
    
    args = parser.parse_args()
    
    # Generate the blog post
    blog_post = generate_blog_post(args)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(blog_post)
        print(f"Blog post generated: {args.output}")
    else:
        print(blog_post)

if __name__ == "__main__":
    main()
