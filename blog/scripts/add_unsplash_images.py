#!/usr/bin/env python3
"""
Add Unsplash hero images to all blog posts based on their titles.
Uses Unsplash Source API for relevant, free-to-use images.
"""

import os
import re
from pathlib import Path

# Mapping of post slugs to Unsplash image URLs
POST_IMAGES = {
    # January
    "2025-01-01-the-circadian-shuffle": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=1600&h=900&fit=crop",
    "2025-01-08-nutritional-nihilism": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=1600&h=900&fit=crop",
    "2025-01-15-sedentary-mastery": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1600&h=900&fit=crop",
    "2025-01-22-the-desert-strategy": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=1600&h=900&fit=crop",
    "2025-01-29-the-aesthetic-of-neglect": "https://images.unsplash.com/photo-1518156677180-95a2893f3e9f?w=1600&h=900&fit=crop",
    # February
    "2025-02-05-cacophony-of-the-city": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=1600&h=900&fit=crop",
    "2025-02-12-architecture-of-anxiety": "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=1600&h=900&fit=crop",
    "2025-02-19-chronotypes-of-chaos": "https://images.unsplash.com/photo-1501139083538-0139583c060f?w=1600&h=900&fit=crop",
    "2025-02-26-artificial-light-bathing": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1600&h=900&fit=crop",
    # March
    "2025-03-05-the-cold-shower-of-reality": "https://images.unsplash.com/photo-1504309092620-4d0ec726efa4?w=1600&h=900&fit=crop",
    "2025-03-12-recycling-sights": "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=1600&h=900&fit=crop",
    "2025-03-19-the-4am-inventory": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=1600&h=900&fit=crop",
    "2025-03-26-the-grounding-of-ambition": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1600&h=900&fit=crop",
    # April
    "2025-04-01-numerical-obsession": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1600&h=900&fit=crop",
    "2025-04-08-the-antifragility-of-ego": "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=1600&h=900&fit=crop",
    "2025-04-15-the-paradox-of-choice": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1600&h=900&fit=crop",
    "2025-04-22-sunk-cost-of-personality": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1600&h=900&fit=crop",
    "2025-04-29-intellectualization-of-avoidance": "https://images.unsplash.com/photo-1456324504439-367cee3b3c32?w=1600&h=900&fit=crop",
    # May
    "2025-05-06-negative-filtering": "https://images.unsplash.com/photo-1516534775068-ba3e7458af70?w=1600&h=900&fit=crop",
    "2025-05-13-the-vapid-goal": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=1600&h=900&fit=crop",
    "2025-05-20-the-fragility-of-comfort": "https://images.unsplash.com/photo-1489367874814-f5d040621dd8?w=1600&h=900&fit=crop",
    "2025-05-27-peak-end-engineering": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&h=900&fit=crop",
    # June
    "2025-06-03-the-mirage-of-completion": "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?w=1600&h=900&fit=crop",
    "2025-06-10-reverse-affirmations": "https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=1600&h=900&fit=crop",
    "2025-06-17-the-cult-of-the-problem": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1600&h=900&fit=crop",
    "2025-06-24-cognitive-dissonance-as-fuel": "https://images.unsplash.com/photo-1494022299300-899b96e49893?w=1600&h=900&fit=crop",
    # July
    "2025-07-01-linkedin-mirage": "https://images.unsplash.com/photo-1611944212129-29977ae1398c?w=1600&h=900&fit=crop",
    "2025-07-08-corporate-gaslighting": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&h=900&fit=crop",
    "2025-07-15-gig-economy-of-the-soul": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1600&h=900&fit=crop",
    "2025-07-22-the-resume-of-regrets": "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1600&h=900&fit=crop",
    "2025-07-29-digital-nomadic-nihilism": "https://images.unsplash.com/photo-1488998427799-e3362cec87c3?w=1600&h=900&fit=crop",
    # August
    "2025-08-05-aesthetics-of-debt": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&h=900&fit=crop",
    "2025-08-12-market-mastery-in-reverse": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1600&h=900&fit=crop",
    "2025-08-19-the-subscription-trap": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1600&h=900&fit=crop",
    "2025-08-26-ghosting-protocol": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1600&h=900&fit=crop",
    # September
    "2025-09-02-family-system-entropy": "https://images.unsplash.com/photo-1511895426328-dc8714191300?w=1600&h=900&fit=crop",
    "2025-09-09-performative-support": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1600&h=900&fit=crop",
    "2025-09-16-social-ledger-of-resentment": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1600&h=900&fit=crop",
    "2025-09-23-the-broken-window-theory-of-despair": "https://images.unsplash.com/photo-1518005020951-eccb494ad742?w=1600&h=900&fit=crop",
    "2025-09-30-intimacy-of-reinforcement": "https://images.unsplash.com/photo-1473172707857-f9e276582ab6?w=1600&h=900&fit=crop",
    # October
    "2025-10-07-the-small-talk-trench": "https://images.unsplash.com/photo-1515169067868-5387ec356754?w=1600&h=900&fit=crop",
    "2025-10-14-the-art-of-being-boring": "https://images.unsplash.com/photo-1494972308805-463bc619d34e?w=1600&h=900&fit=crop",
    "2025-10-21-dinner-party-of-discomfort": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1600&h=900&fit=crop",
    "2025-10-29-library-of-unread-books": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1600&h=900&fit=crop",
    # November
    "2025-11-05-cult-of-the-productivity-hack": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1600&h=900&fit=crop",
    "2025-11-12-archive-of-incomplete-projects": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=1600&h=900&fit=crop",
    "2025-11-19-the-somatic-shadow": "https://images.unsplash.com/photo-1518241353330-0f7941c2d9b5?w=1600&h=900&fit=crop",
    "2025-11-26-the-reverse-bibliography": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=1600&h=900&fit=crop",
    # December
    "2025-12-03-shadow-mentors": "https://images.unsplash.com/photo-1491438590914-bc09fcaaf77a?w=1600&h=900&fit=crop",
    "2025-12-10-the-glossary-of-gaps": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1600&h=900&fit=crop",
    "2025-12-17-the-year-in-review--a-failure": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&h=900&fit=crop",
    "2025-12-24-the-masterwork-is-ready": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1600&h=900&fit=crop",
    "2025-12-31-book-launch": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=1600&h=900&fit=crop",
}

def add_hero_image_to_post(file_path: Path, image_url: str) -> bool:
    """Add heroImage to the frontmatter of a blog post."""
    content = file_path.read_text()
    
    # Check if heroImage already exists
    if "heroImage:" in content:
        print(f"  Skipping {file_path.name} - already has heroImage")
        return False
    
    # Find the end of frontmatter (second ---)
    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"  Error: {file_path.name} - invalid frontmatter")
        return False
    
    # Add heroImage to frontmatter
    frontmatter = parts[1].rstrip()
    new_frontmatter = f'{frontmatter}\nheroImage: "{image_url}"'
    
    new_content = f"---{new_frontmatter}\n---{parts[2]}"
    file_path.write_text(new_content)
    print(f"  Added heroImage to {file_path.name}")
    return True

def main():
    blog_dir = Path("/Users/algimantask/Personal/Miserable/blog/src/content/blog")
    
    updated = 0
    for post_file in sorted(blog_dir.glob("*.md")):
        slug = post_file.stem
        if slug in POST_IMAGES:
            if add_hero_image_to_post(post_file, POST_IMAGES[slug]):
                updated += 1
        else:
            print(f"  No image mapping for {slug}")
    
    print(f"\nUpdated {updated} posts with Unsplash hero images")

if __name__ == "__main__":
    main()
