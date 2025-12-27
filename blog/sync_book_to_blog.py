#!/usr/bin/env python3
"""
Sync book chapters to blog posts
Copies the lighter, funnier book content to blog posts while preserving frontmatter
"""

from pathlib import Path
import re

# Mapping of book chapters to blog posts
CHAPTER_TO_POST = {
    "circadian-shuffle.qmd": "2025-01-01-the-circadian-shuffle.md",
    "nutritional-nihilism.qmd": "2025-01-08-nutritional-nihilism.md",
    "sedentary-mastery.qmd": "2025-01-15-sedentary-mastery.md",
    "desert-strategy.qmd": "2025-01-22-the-desert-strategy.md",
    "anesthetic-of-neglect.qmd": "2025-01-29-the-aesthetic-of-neglect.md",
    "cacophony-of-the-city.qmd": "2025-02-05-cacophony-of-the-city.md",
    "architecture-of-anxiety.qmd": "2025-02-12-architecture-of-anxiety.md",
    "chronotypes-of-chaos.qmd": "2025-02-19-chronotypes-of-chaos.md",
    "artificial-light.qmd": "2025-02-26-artificial-light-bathing.md",
    "cold-shower-of-reality.qmd": "2025-03-05-the-cold-shower-of-reality.md",
    "recycling-sights.qmd": "2025-03-12-recycling-sights.md",
    "4am-inventory.qmd": "2025-03-19-the-4am-inventory.md",
    "grounding-of-ambition.qmd": "2025-03-26-the-grounding-of-ambition.md",
    "numerical-obsession.qmd": "2025-04-01-numerical-obsession.md",
    "antifragility-of-ego.qmd": "2025-04-08-the-antifragility-of-ego.md",
    "paradox-of-choice.qmd": "2025-04-15-the-paradox-of-choice.md",
    "sunk-cost-of-personality.qmd": "2025-04-22-sunk-cost-of-personality.md",
    "intellectualization-of-avoidance.qmd": "2025-04-29-intellectualization-of-avoidance.md",
    "negative-filtering.qmd": "2025-05-06-negative-filtering.md",
    "vapid-goals.qmd": "2025-05-13-the-vapid-goal.md",
    "fragility-of-comfort.qmd": "2025-05-20-the-fragility-of-comfort.md",
    "peak-end-engineering.qmd": "2025-05-27-peak-end-engineering.md",
    "mirage-of-completion.qmd": "2025-06-03-the-mirage-of-completion.md",
    "reverse-affirmations.qmd": "2025-06-10-reverse-affirmations.md",
    "cult-of-the-problem.qmd": "2025-06-17-the-cult-of-the-problem.md",
    "cognitive-dissonance-as-fuel.qmd": "2025-06-24-cognitive-dissonance-as-fuel.md",
    "linkedin-mirage.qmd": "2025-07-01-linkedin-mirage.md",
    "corporate-gaslighting.qmd": "2025-07-08-corporate-gaslighting.md",
    "gig-economy-of-the-soul.qmd": "2025-07-15-gig-economy-of-the-soul.md",
    "resume-of-regrets.qmd": "2025-07-22-the-resume-of-regrets.md",
    "digital-nomadic-nihilism.qmd": "2025-07-29-digital-nomadic-nihilism.md",
    "aesthetics-of-debt.qmd": "2025-08-05-aesthetics-of-debt.md",
    "market-mastery-in-reverse.qmd": "2025-08-12-market-mastery-in-reverse.md",
    "subscription-trap.qmd": "2025-08-19-the-subscription-trap.md",
    "ghosting-protocol.qmd": "2025-08-26-ghosting-protocol.md",
    "family-system-entropy.qmd": "2025-09-02-family-system-entropy.md",
    "performative-support.qmd": "2025-09-09-performative-support.md",
    "social-ledger-of-resentment.qmd": "2025-09-16-social-ledger-of-resentment.md",
    "broken-window-theory-of-despair.qmd": "2025-09-23-the-broken-window-theory-of-despair.md",
    "intimacy-of-reinforcement.qmd": "2025-09-30-intimacy-of-reinforcement.md",
    "small-talk-as-a-trench.qmd": "2025-10-07-the-small-talk-trench.md",
    "art-of-being-boring.qmd": "2025-10-14-the-art-of-being-boring.md",
    "dinner-party-of-discomfort.qmd": "2025-10-21-dinner-party-of-discomfort.md",
    "library-of-unread-books.qmd": "2025-10-29-library-of-unread-books.md",
    "cult-of-the-productivity-hack.qmd": "2025-11-05-cult-of-the-productivity-hack.md",
    "archive-of-incomplete-projects.qmd": "2025-11-12-archive-of-incomplete-projects.md",
    "somatic-shadow.qmd": "2025-11-19-the-somatic-shadow.md",
    "reverse-bibliography-annotated.qmd": "2025-11-26-the-reverse-bibliography.md",
    "shadow-mentors.qmd": "2025-12-03-shadow-mentors.md",
    "glossary-of-gaps.qmd": "2025-12-10-the-glossary-of-gaps.md",
    "year-in-review.qmd": "2025-12-17-the-year-in-review--a-failure.md",
}

def extract_frontmatter(content: str) -> tuple[str, str]:
    """Extract frontmatter from markdown file"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2].strip()
    return "", content

def sync_chapter_to_post(book_dir: Path, blog_dir: Path, chapter_file: str, post_file: str):
    """Sync a single chapter to its corresponding blog post"""
    chapter_path = book_dir / chapter_file
    post_path = blog_dir / post_file
    
    if not chapter_path.exists():
        print(f"⚠️  Chapter not found: {chapter_file}")
        return False
    
    if not post_path.exists():
        print(f"⚠️  Post not found: {post_file}")
        return False
    
    # Read chapter content
    with open(chapter_path, 'r', encoding='utf-8') as f:
        chapter_content = f.read()
    
    # Read post to get frontmatter
    with open(post_path, 'r', encoding='utf-8') as f:
        post_content = f.read()
    
    frontmatter, _ = extract_frontmatter(post_content)
    
    # Combine frontmatter with chapter content
    new_content = f"---\n{frontmatter}\n---\n\n{chapter_content}"
    
    # Write updated post
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    book_dir = Path(__file__).parent.parent / "book"
    blog_dir = Path(__file__).parent / "src/content/blog"
    
    print("📚 Syncing book chapters to blog posts...")
    print(f"   Book directory: {book_dir}")
    print(f"   Blog directory: {blog_dir}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for chapter_file, post_file in CHAPTER_TO_POST.items():
        print(f"[{success_count + fail_count + 1}/{len(CHAPTER_TO_POST)}] {chapter_file} → {post_file}...", end=" ")
        
        if sync_chapter_to_post(book_dir, blog_dir, chapter_file, post_file):
            print("✅")
            success_count += 1
        else:
            print("❌")
            fail_count += 1
    
    print()
    print(f"✅ Synced {success_count} posts")
    if fail_count > 0:
        print(f"❌ Failed {fail_count} posts")

if __name__ == "__main__":
    main()
