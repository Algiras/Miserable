#!/usr/bin/env python3
"""
Blog Enhancement Pipeline
Processes all blog posts sequentially with context awareness.
"""

import asyncio
import re
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from preprocessor import (
    MCPManager, NarrationMemory, agent_reasoning_loop,
    MCP_CONFIG_PATH, BLOG_DIR, BOOK_DIR, CACHE_DIR
)

def extract_frontmatter(content: str):
    """Extract YAML frontmatter and body from markdown."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        frontmatter = f"---\n{match.group(1)}\n---"
        body = match.group(2).strip()
        return frontmatter, body
    return "", content

def get_ordered_posts():
    """Get all blog posts in chronological order."""
    posts = []
    for post_file in sorted(BLOG_DIR.glob("*.md")):
        match = re.match(r'(\d{4}-\d{2}-\d{2})-(.*?)\.md', post_file.name)
        if match:
            date_str, slug = match.groups()
            title = slug.replace('-', ' ').title()
            posts.append((post_file, date_str, title, slug))
    return posts

def find_matching_chapter(post_slug: str):
    """Find the corresponding book chapter for a blog post."""
    # Try various patterns to match blog post to chapter
    chapter_patterns = [
        f"{post_slug}.qmd",
        f"{post_slug.replace('-', '_')}.qmd",
        f"{post_slug.replace('the-', '')}.qmd",
        f"{'_'.join(post_slug.split('-'))}.qmd",
    ]
    
    for pattern in chapter_patterns:
        chapter_file = BOOK_DIR / pattern
        if chapter_file.exists():
            with open(chapter_file, 'r') as f:
                content = f.read()
                # Extract just the content, skip frontmatter if present
                _, body = extract_frontmatter(content)
                return body if body else content
    
    return ""

def build_previous_posts_summary(all_posts, current_index, window=2):
    """Build context summary from previous posts."""
    if current_index == 0:
        return ""
    
    context_parts = ["PREVIOUS POSTS (for continuity):"]
    start = max(0, current_index - window)
    
    for i in range(start, current_index):
        _, date, title, _ = all_posts[i]
        context_parts.append(f"- {date}: {title}")
    
    return "\n".join(context_parts)

async def enhance_blog_post(
    post_file: Path,
    post_title: str,
    mcp_manager,
    book_chapter_content: str = "",
    previous_posts_context: str = "",
    memory = None
):
    """Enhance a single blog post using the ReAct agent."""
    print(f"\n📝 Processing: {post_title}", flush=True)
    
    # Check cache
    cache_file = CACHE_DIR / f"{post_file.stem}.md"
    if cache_file.exists():
        print(f"   ✓ Using cached version", flush=True)
        with open(cache_file, 'r') as f:
            cached_content = f.read()
            if memory:
                _, body = extract_frontmatter(cached_content)
                memory.add_chapter(post_title, body)
            return cached_content
    
    # Read existing post
    with open(post_file, 'r') as f:
        existing_content = f.read()
    
    frontmatter, body = extract_frontmatter(existing_content)
    
    # Get semantic context from previous posts
    semantic_context = ""
    if memory:
        query_text = book_chapter_content if book_chapter_content else body
        semantic_context = memory.get_semantic_context(query_text)
    
    # Prepare the input text for the agent
    input_text = f"""
BLOG POST TITLE: {post_title}

{previous_posts_context}

BOOK CHAPTER (source material to expand from):
{book_chapter_content if book_chapter_content else "[No matching chapter found - create original content]"}

CURRENT STUB CONTENT:
{body}

TASK: Transform this into a comprehensive blog post (2,500-4,000 words).
- Use markdown formatting (headers, lists, callouts, blockquotes)
- Research historical/cultural references
- Build on previous posts for narrative continuity
- Maintain the "Reverse Maven" voice
- Return ONLY the body content (no frontmatter)
"""
    
    print(f"   🧠 Maven is researching & writing...", flush=True)
    
    try:
        # Use the agent reasoning loop
        enhanced_body = await agent_reasoning_loop(
            input_text,
            mcp_manager,
            previous_context=previous_posts_context,
            next_context="",
            semantic_context=semantic_context
        )
        
        # Combine frontmatter with enhanced body
        full_content = f"{frontmatter}\n\n{enhanced_body}"
        
        # Cache the result
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            f.write(full_content)
        
        # Add to memory for future posts
        if memory:
            memory.add_chapter(post_title, enhanced_body)
        
        word_count = len(enhanced_body.split())
        print(f"   ✅ Enhanced ({word_count:,} words)", flush=True)
        return full_content
        
    except Exception as e:
        print(f"   ❌ Enhancement Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return existing_content

async def enhance_all_posts():
    """Process all blog posts sequentially with context."""
    print("🚀 Starting Blog Enhancement Pipeline\n", flush=True)
    print(f"📂 Blog Directory: {BLOG_DIR}", flush=True)
    print(f"📂 Book Directory: {BOOK_DIR}", flush=True)
    print(f"📂 Cache Directory: {CACHE_DIR}\n", flush=True)
    
    # Initialize MCP and Memory
    mcp_manager = MCPManager(MCP_CONFIG_PATH)
    await mcp_manager.connect_all()
    
    try:
        memory = NarrationMemory()
        all_posts = get_ordered_posts()
        
        print(f"📚 Found {len(all_posts)} blog posts to process\n", flush=True)
        
        for i, (post_file, date, title, slug) in enumerate(all_posts):
            print(f"[{i+1}/{len(all_posts)}] {date} - {title}", flush=True)
            
            # Find matching book chapter
            chapter_content = find_matching_chapter(slug)
            if chapter_content:
                print(f"   📖 Found matching chapter ({len(chapter_content.split())} words)", flush=True)
            
            # Build context from previous posts
            prev_context = build_previous_posts_summary(all_posts, i, window=2)
            
            # Enhance the post
            enhanced_content = await enhance_blog_post(
                post_file,
                title,
                mcp_manager,
                book_chapter_content=chapter_content,
                previous_posts_context=prev_context,
                memory=memory
            )
            
            # Write back to the same file
            with open(post_file, 'w') as f:
                f.write(enhanced_content)
        
        print(f"\n🎉 All {len(all_posts)} posts enhanced successfully!", flush=True)
        print(f"💾 Cache saved to: {CACHE_DIR}", flush=True)
        
    finally:
        await mcp_manager.disconnect_all()

if __name__ == "__main__":
    asyncio.run(enhance_all_posts())
