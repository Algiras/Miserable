#!/usr/bin/env python3
"""
Add blog post framing to book chapters
Adds intro and outro to make chapters feel like standalone posts
"""

from pathlib import Path
import re

def add_blog_framing(filepath: Path) -> bool:
    """Add intro and outro to make chapter feel like a blog post."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter and body
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()
        else:
            return False
    else:
        return False
    
    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if not title_match:
        return False
    
    title = title_match.group(1)
    
    # Check if already has intro (starts with paragraph before first heading)
    lines = body.split('\n')
    first_heading_idx = next((i for i, line in enumerate(lines) if line.startswith('#')), -1)
    
    if first_heading_idx > 0:
        # Already has intro content
        print(f"   Already has intro, skipping")
        return False
    
    # Add intro paragraph
    intro = f"""Welcome to another installment in our ongoing series: *Miserable: How to Fail at Life*. Today's topic is a personal favorite—a masterclass in self-sabotage that's both accessible and devastatingly effective.

"""
    
    # Add outro
    outro = """

---

*This post is part of the "Miserable" series—a satirical guide to failing at life with style. For more recipes for disaster, check out the full collection at [miserable.cloud](https://miserable.cloud/).*
"""
    
    # Combine
    new_body = intro + body + outro
    new_content = f"---\n{frontmatter}---\n\n{new_body}"
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    blog_dir = Path(__file__).parent / "src/content/blog"
    
    print("📝 Adding blog post framing to chapters...")
    print()
    
    files = sorted(blog_dir.glob("2025-*.md"))
    success_count = 0
    
    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {filepath.name}...", end=" ")
        
        if add_blog_framing(filepath):
            print("✅")
            success_count += 1
        else:
            print("⏭️")
    
    print()
    print(f"✅ Added framing to {success_count} posts")

if __name__ == "__main__":
    main()
