#!/usr/bin/env python3
"""
Convert book chapters to proper blog posts using Ministral 8B
- Adapts content to blog format with custom intros/conclusions
- Preserves satirical tone and recipe structure
"""

import subprocess
from pathlib import Path
import sys
import re

OLLAMA_MODEL = "ministral-3:8b"

def check_ollama():
    """Check if Ollama is running and the model is available."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if OLLAMA_MODEL.split(":")[0] not in result.stdout:
            print(f"⚠️  Model {OLLAMA_MODEL} not found. Pulling...")
            subprocess.run(["ollama", "pull", OLLAMA_MODEL], check=True)
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama is not running or not installed.")
        return False

def convert_chapter_to_post(filepath: Path) -> str:
    """Use LLM to convert book chapter to blog post format."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter and body
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()
        else:
            frontmatter = ""
            body = content
    else:
        frontmatter = ""
        body = content
    
    # Remove the generic intro/outro if present
    body = re.sub(r'^Welcome to another installment.*?devastatingly effective\.\n\n', '', body, flags=re.DOTALL)
    body = re.sub(r'\n---\n\n\*This post is part of.*?$', '', body, flags=re.DOTALL)
    
    prompt = f"""You are a satirical writer adapting a book chapter into a standalone blog post. The original is written as a darkly humorous "recipe for failure."

Your task:
1. Write a compelling 2-3 paragraph introduction that:
   - Sets up the topic with wit and relatability
   - Hooks the reader with dark humor
   - Transitions naturally into the "recipe"

2. Keep the recipe format EXACTLY as is:
   - Title with "Yields:" subtitle
   - Ingredients list
   - Instructions (numbered steps)
   - "Note from the Chef" section

3. Add brief commentary between some steps if it enhances the humor

4. Write a 1-2 paragraph conclusion that:
   - Ties back to the intro
   - Ends with a memorable quip or observation
   - Doesn't preach or get preachy

CRITICAL: Maintain the satirical tone. This is dark comedy about self-sabotage, not actual advice.

Original chapter:
{body}

Blog post version:"""
    
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes per post
        )
        
        if result.returncode != 0:
            print(f"⚠️  Ollama error: {result.stderr}")
            return None
        
        blog_content = result.stdout.strip()
        
        # Validate we got actual content
        if not blog_content or len(blog_content) < 100:
            print(f"⚠️  Empty/short output ({len(blog_content)} chars)")
            return None
        
        # Reconstruct with frontmatter
        if frontmatter:
            full_content = f"---\n{frontmatter}---\n\n{blog_content}"
        else:
            full_content = blog_content
        
        return full_content
            
    except subprocess.TimeoutExpired:
        print(f"⚠️  Timeout")
        return None
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None

def main():
    if not check_ollama():
        return
    
    blog_dir = Path(__file__).parent / "src/content/blog"
    
    # Process specific files or all
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
        print(f"📝 Converting {len(files)} specific posts...")
    else:
        files = sorted(blog_dir.glob("2025-*.md"))
        print(f"📝 Converting all {len(files)} blog posts...")
    
    print(f"   Using model: {OLLAMA_MODEL}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {filepath.name}...", end=" ", flush=True)
        
        converted = convert_chapter_to_post(filepath)
        
        if converted:
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(converted)
            print("✅")
            success_count += 1
        else:
            print("❌")
            fail_count += 1
    
    print()
    print(f"✅ Converted {success_count} posts")
    if fail_count > 0:
        print(f"❌ Failed {fail_count} posts")

if __name__ == "__main__":
    main()
