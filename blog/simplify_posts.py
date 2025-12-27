#!/usr/bin/env python3
"""
Blog Post Simplifier - Replace originals with simplified versions
Uses LLM to rewrite blog posts with only headings and paragraphs.
No bold, italic, quotes, lists, callouts, or other complex formatting.
"""

import subprocess
import shutil
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent / "src/content/blog"
OLLAMA_MODEL = "qwen2.5:7b"  # Larger model for better rewriting
BACKUP_DIR = Path(__file__).parent / "backup_originals"

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

def simplify_blog_post(filepath: Path) -> str:
    """
    Use LLM to rewrite blog post with only headings and paragraphs.
    Removes all bold, italic, quotes, lists, callouts, etc.
    """
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
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
    
    prompt = f"""Rewrite this blog post to use ONLY headings and paragraphs. Remove ALL formatting:

RULES:
1. Keep headings (# ## ### ####) - preserve the hierarchy
2. Convert everything else to plain paragraphs
3. NO bold (**text**)
4. NO italic (*text*)
5. NO quotes (> text)
6. NO lists (- or 1.)
7. NO callouts (::: blocks)
8. NO code blocks
9. NO tables
10. Convert list items into flowing paragraph text
11. Convert quotes into regular paragraphs
12. Preserve the meaning and content, just simplify the formatting

Original content:
{body}

Rewritten (headings and paragraphs only):"""

    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        simplified = result.stdout.strip()
        
        # Reconstruct with frontmatter
        if frontmatter:
            return f"---\n{frontmatter}---\n\n{simplified}"
        else:
            return simplified
            
    except subprocess.TimeoutExpired:
        print(f"⚠️  Timeout processing {filepath.name}")
        return None
    except Exception as e:
        print(f"⚠️  Error processing {filepath.name}: {e}")
        return None

def main():
    """Simplify all blog posts and replace originals."""
    import sys
    
    if not check_ollama():
        return
    
    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Check for specific files in arguments
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
        print(f"📝 Retrying {len(files)} specific blog posts...")
    else:
        print(f"📝 Simplifying blog posts with {OLLAMA_MODEL}...")
        files = sorted(BASE_DIR.glob("*.md"))
        # Filter out the test simplified file
        files = [f for f in files if not f.name.endswith('_simplified.md')]
        print(f"📚 Found {len(files)} blog posts to process")

    print("   Removing: bold, italic, quotes, lists, callouts, etc.")
    print("   Keeping: headings and paragraphs only")
    print()
    print(f"⚠️  WARNING: This will REPLACE the original files!")
    print(f"   Backups will be saved to: {BACKUP_DIR}")
    print()
    
    for i, filepath in enumerate(files, 1):
        filename = filepath.name
        print(f"[{i}/{len(files)}] Processing {filename}...", end=" ", flush=True)
        
        # Backup original
        backup_path = BACKUP_DIR / filename
        shutil.copy2(filepath, backup_path)
        
        simplified = simplify_blog_post(filepath)
        
        if simplified:
            # Replace original
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(simplified)
            print("✅")
        else:
            print("❌ (original preserved)")
    
    print()
    print(f"✅ Simplified posts saved to: {BASE_DIR}")
    print(f"📦 Original backups saved to: {BACKUP_DIR}")
    print()
    print("📋 Next steps:")
    print("   1. Review the simplified posts")
    print("   2. If you need to restore originals: cp backup_originals/* src/content/blog/")

if __name__ == "__main__":
    main()
