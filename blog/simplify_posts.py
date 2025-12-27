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
OLLAMA_MODEL = "ministral:8b"  # Better model for preserving quality
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
    Use LLM to clean up problematic markdown formatting while preserving writing quality.
    Only removes elements that cause transcription issues.
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
    
    prompt = f"""You are a professional editor preparing this blog post for audio transcription. Your goal is to preserve the sophisticated writing style and intellectual depth while removing ONLY the markdown formatting that causes transcription problems.

PRESERVE:
- All sophisticated vocabulary and complex sentence structures
- The author's unique voice and tone
- Philosophical depth and nuanced arguments
- Headings (# ## ### ####) - keep the hierarchy exactly as is
- Paragraph breaks and flow

REMOVE/CONVERT (these cause transcription issues):
- Bold (**text**) → convert to regular text, preserving the emphasis through word choice
- Italic (*text*) → convert to regular text
- Block quotes (> text) → convert to regular paragraphs, you may add "As noted:" or similar if needed for context
- Lists (- or 1.) → convert to flowing paragraphs with transition words
- Callout blocks (::: blocks) → convert to regular paragraphs, preserving the warning/note content
- Code blocks → convert to regular text if present
- Tables → convert to prose if present

CRITICAL: Do NOT dumb down the writing. Do NOT simplify vocabulary. Do NOT shorten sentences unnecessarily. The goal is ONLY to remove markdown formatting, not to change the writing quality.

Original content:
{body}

Cleaned version (preserve sophistication, remove only formatting):"""

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
