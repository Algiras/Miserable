#!/usr/bin/env python3
"""
Test blog post simplifier on a single file
"""

import subprocess
import sys
from pathlib import Path

OLLAMA_MODEL = "qwen2.5:7b"

def simplify_single_post(filepath: str):
    """Test simplification on a single blog post."""
    
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    print(f"📝 Simplifying: {filepath.name}")
    print(f"   Using model: {OLLAMA_MODEL}")
    print()
    
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

    print("🤖 Processing with LLM...")
    
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        simplified = result.stdout.strip()
        
        # Save to test output
        output_path = filepath.parent / f"{filepath.stem}_simplified.md"
        
        if frontmatter:
            full_content = f"---\n{frontmatter}---\n\n{simplified}"
        else:
            full_content = simplified
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"\n✅ Simplified version saved to: {output_path.name}")
        print()
        print("📋 Compare the files:")
        print(f"   Original:   {filepath}")
        print(f"   Simplified: {output_path}")
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout - LLM took too long")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_simplify.py <blog_post.md>")
        print()
        print("Example:")
        print("  python3 blog/test_simplify.py blog/src/content/blog/2025-01-01-the-circadian-shuffle.md")
        sys.exit(1)
    
    simplify_single_post(sys.argv[1])
