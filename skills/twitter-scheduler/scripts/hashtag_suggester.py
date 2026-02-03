#!/usr/bin/env python3
"""
Generate hashtag suggestions and analyze hashtag performance.
"""

import argparse
import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path.home() / ".openclaw" / "twitter-scheduler"

# FedBuyOut core hashtags by category
HASHTAG_CATEGORIES = {
    "core": [
        "#GovCon",
        "#GovernmentContracting",
        "#FederalContracts",
        "#SmallBusiness",
        "#ContractingMadeSimple"
    ],
    "set_asides": [
        "#8a",
        "#WOSB",
        "#HUBZone",
        "#SDVOSB",
        "#VOSB",
        "#MinorityOwned",
        "#WomenOwned"
    ],
    "process": [
        "#SAMRegistration",
        "#SAMgov",
        "#NAICS",
        "#NAICSCode",
        "#NAICSCodeHelp",
        "#RFP",
        "#ContractOpportunity"
    ],
    "business": [
        "#B2G",
        "#B2GGrowth",
        "#GovSales",
        "#GovernmentSales",
        "#ContractorLife",
        "#SmallBiz"
    ],
    "tips": [
        "#ContractingTips",
        "#GovConTips",
        "#SmallBusinessTips",
        "#WinGovernmentContracts",
        "#Contracting101"
    ],
    "community": [
        "#GovConCommunity",
        "#SmallBusinessCommunity",
        "#Entrepreneur",
        "#BusinessGrowth"
    ]
}

# Topic-based hashtag recommendations
TOPIC_HASHTAGS = {
    "sam registration": ["#SAMRegistration", "#SAMgov", "#GovCon", "#SmallBusiness", "#Contracting101"],
    "naics codes": ["#NAICS", "#NAICSCode", "#NAICSCodeHelp", "#GovCon", "#FederalContracts"],
    "government contracts": ["#GovCon", "#GovernmentContracting", "#FederalContracts", "#B2G", "#SmallBusiness"],
    "8a program": ["#8a", "#MinorityOwned", "#GovCon", "#SmallBusiness", "#FederalContracts"],
    "wosb": ["#WOSB", "#WomenOwned", "#GovCon", "#SmallBusiness", "#FederalContracts"],
    "hubzone": ["#HUBZone", "#GovCon", "#SmallBusiness", "#FederalContracts", "#RuralBusiness"],
    "winning contracts": ["#WinGovernmentContracts", "#GovCon", "#B2GGrowth", "#ContractingTips"],
    "proposal writing": ["#ProposalWriting", "#RFP", "#GovCon", "#FederalContracts", "#ContractingTips"],
    "marketing": ["#GovMarketing", "#B2G", "#GovernmentSales", "#SmallBusiness", "#MarketingTips"],
    "set asides": ["#SetAsides", "#8a", "#WOSB", "#HUBZone", "#SmallBusiness"],
    "contract opportunities": ["#ContractOpportunity", "#FedBizOpps", "#GovCon", "#RFP", "#FederalContracts"]
}


def get_hashtag_suggestions(topic, count=5):
    """Get hashtag suggestions for a topic."""
    topic_lower = topic.lower()
    suggestions = []
    
    # Check for exact topic match
    if topic_lower in TOPIC_HASHTAGS:
        suggestions = TOPIC_HASHTAGS[topic_lower][:count]
    else:
        # Try partial matches
        for key, tags in TOPIC_HASHTAGS.items():
            if any(word in topic_lower for word in key.split()):
                suggestions.extend(tags)
        
        # Remove duplicates and limit
        seen = set()
        unique = []
        for tag in suggestions:
            if tag not in seen:
                seen.add(tag)
                unique.append(tag)
        suggestions = unique[:count]
    
    # If still no suggestions, use core tags
    if not suggestions:
        suggestions = HASHTAG_CATEGORIES["core"][:count]
    
    return suggestions


def suggest_hashtags(topic, count=5):
    """Display hashtag suggestions for a topic."""
    print(f"🔍 Hashtag suggestions for: '{topic}'\n")
    
    suggestions = get_hashtag_suggestions(topic, count)
    
    print("📌 Recommended Hashtags:")
    for i, tag in enumerate(suggestions, 1):
        print(f"   {i}. {tag}")
    
    print(f"\n💡 Usage:")
    print(f"   Add these to your tweet for better reach")
    print(f"   Example: Your content here {' '.join(suggestions[:3])}")


def list_all_categories():
    """List all hashtag categories."""
    print("📚 FedBuyOut Hashtag Library\n")
    
    for category, tags in HASHTAG_CATEGORIES.items():
        print(f"🏷️  {category.replace('_', ' ').title()}")
        for tag in tags:
            print(f"      {tag}")
        print()


def analyze_hashtags(hashtag_string):
    """Analyze a string of hashtags."""
    hashtags = [tag.strip() for tag in hashtag_string.split(',')]
    
    print("📊 Hashtag Analysis\n")
    
    total_chars = sum(len(tag) for tag in hashtags)
    tweet_chars_remaining = 280 - total_chars - len(hashtags)  # Account for spaces
    
    print(f"Hashtags provided: {len(hashtags)}")
    print(f"Total characters: {total_chars}")
    print(f"Remaining for tweet content: ~{tweet_chars_remaining} chars")
    
    print("\n📋 Hashtag Breakdown:")
    for tag in hashtags:
        tag_lower = tag.lower().replace('#', '')
        category = "other"
        for cat, cat_tags in HASHTAG_CATEGORIES.items():
            if any(tag_lower in t.lower() for t in cat_tags):
                category = cat.replace('_', ' ').title()
                break
        print(f"   {tag:<25} ({category})")
    
    print("\n💡 Recommendations:")
    if len(hashtags) > 5:
        print("   ⚠️  Consider using 3-5 hashtags for best engagement")
    if tweet_chars_remaining < 100:
        print("   ⚠️  Hashtags taking up significant space - keep content concise")
    
    # Suggest related hashtags
    print("\n🔄 Related hashtags to consider:")
    all_related = []
    for tag in hashtags:
        tag_lower = tag.lower().replace('#', '')
        for topic, topic_tags in TOPIC_HASHTAGS.items():
            if tag_lower.replace('program', '').replace('codes', 'code') in topic:
                all_related.extend(topic_tags)
    
    if all_related:
        seen = set(h.lower() for h in hashtags)
        for tag in all_related[:5]:
            if tag.lower() not in seen:
                print(f"      {tag}")


def generate_content_ideas(topic):
    """Generate tweet content ideas for a topic."""
    print(f"💡 Content Ideas for '{topic}'\n")
    
    templates = {
        "sam registration": [
            "📝 SAM Registration tip: Update your profile quarterly to stay compliant",
            "❓ Did you know? SAM registration is FREE. Don't pay someone to do it for you",
            "🚀 Just got SAM registered? Here's what to do next... 🧵"
        ],
        "naics codes": [
            "🔢 Choosing the right NAICS code can make or break your GovCon success",
            "📊 Your NAICS code determines which contracts you can bid on",
            "💡 Pro tip: You can have multiple NAICS codes in your SAM profile"
        ],
        "government contracts": [
            "🏆 Small businesses won $154B in federal contracts last year",
            "🤔 Think GovCon is just for big companies? Think again",
            "📈 The government buys everything from coffee to cloud services"
        ],
        "8a program": [
            "⭐ The 8(a) program can be a game-changer for eligible small businesses",
            "🎓 8(a) firms get sole-source contracts up to $4.5M",
            "⏰ 8(a) certification takes time - start the process early"
        ]
    }
    
    topic_lower = topic.lower()
    if topic_lower in templates:
        for idea in templates[topic_lower]:
            print(f"   • {idea}")
    else:
        print(f"   • 🧵 Thread idea: 5 things every small business should know about {topic}")
        print(f"   • 💡 Quick tip: Best practices for {topic}")
        print(f"   • ❓ Question: What's your biggest challenge with {topic}?")
        print(f"   • 📊 Stat: Share an interesting number or fact about {topic}")


def main():
    parser = argparse.ArgumentParser(
        description="Hashtag suggestions and analysis for FedBuyOut Twitter"
    )
    parser.add_argument("--topic", "-t", help="Topic to get hashtag suggestions for")
    parser.add_argument("--count", "-c", type=int, default=5, help="Number of suggestions (default: 5)")
    parser.add_argument("--analyze", "-a", help="Analyze comma-separated hashtags")
    parser.add_argument("--list-categories", "-l", action="store_true", help="List all hashtag categories")
    parser.add_argument("--ideas", "-i", help="Generate content ideas for a topic")
    
    args = parser.parse_args()
    
    if args.topic:
        suggest_hashtags(args.topic, args.count)
    elif args.analyze:
        analyze_hashtags(args.analyze)
    elif args.list_categories:
        list_all_categories()
    elif args.ideas:
        generate_content_ideas(args.ideas)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
