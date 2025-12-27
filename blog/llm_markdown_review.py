#!/usr/bin/env python3
"""
LLM-based markdown reviewer for blog posts.
Uses a small local LLM via Ollama to detect markdown formatting issues.
"""

import os
import json
import subprocess
import re
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent / "src/content/blog"
OLLAMA_MODEL = "qwen2.5:0.5b"  # Small, fast model
OUTPUT_FILE = "llm_markdown_report.txt"

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
        print("   Install: https://ollama.ai")
        print("   Start: ollama serve")
        return False

def review_markdown_with_llm(filepath: Path) -> list:
    """
    Use LLM to review markdown file for formatting issues.
    Returns list of tuples: (issue_description, suggested_fix)
    """
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Limit content size for faster processing
    if len(content) > 6000:
        content = content[:6000] + "\n... [truncated]"
    
    prompt = f"""Review this markdown blog post for formatting errors. For each error, provide:
1. The issue description
2. A suggested fix

Format each issue as:
ISSUE: [description]
FIX: [suggestion]

Look for:
- Unbalanced bold markers (** without closing **)
- Broken list items split across lines
- Mangled patterns like "** text**" or "**text** ."
- Merged paragraphs or headers

If NO errors found, respond with: "No issues found"

Markdown:
```
{content}
```

Issues and fixes:"""

    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        response = result.stdout.strip()
        
        # Parse response - look for actual issues
        if "no issues" in response.lower() or "no errors" in response.lower():
            return []
        
        # Parse ISSUE/FIX pairs
        issues = []
        lines = response.split('\n')
        current_issue = None
        current_fix = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('```'):
                continue
                
            if line.upper().startswith('ISSUE:'):
                if current_issue and current_fix:
                    issues.append((current_issue, current_fix))
                current_issue = line[6:].strip()
                current_fix = None
            elif line.upper().startswith('FIX:'):
                current_fix = line[4:].strip()
                if current_issue and current_fix:
                    issues.append((current_issue, current_fix))
                    current_issue = None
                    current_fix = None
        
        # Add last pair if exists
        if current_issue and current_fix:
            issues.append((current_issue, current_fix))
        
        return issues[:5]  # Limit to top 5 issues
            
    except subprocess.TimeoutExpired:
        return [("⚠️ LLM timeout", "Try running the script again")]
    except Exception as e:
        return [(f"⚠️ Error: {str(e)}", "Check Ollama is running")]

def main():
    """Review all blog posts with LLM."""
    
    if not check_ollama():
        return
    
    print(f"🔍 Reviewing blog posts with {OLLAMA_MODEL}...")
    print()
    
    results = []
    files = sorted(BASE_DIR.glob("*.md"))
    
    for i, filepath in enumerate(files, 1):
        filename = filepath.name
        print(f"[{i}/{len(files)}] {filename}...", end=" ", flush=True)
        
        issues = review_markdown_with_llm(filepath)
        
        if issues:
            print(f"❌ {len(issues)} issues")
            results.append((filename, issues))
        else:
            print("✅")
    
    # Save results
    if results:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("LLM Markdown Review Report\n")
            f.write("=" * 70 + "\n\n")
            
            for filename, issues in results:
                f.write(f"📄 {filename}\n")
                f.write("-" * 70 + "\n")
                for i, (issue, fix) in enumerate(issues, 1):
                    f.write(f"\n{i}. ISSUE: {issue}\n")
                    f.write(f"   FIX: {fix}\n")
                f.write("\n" + "=" * 70 + "\n\n")
        
        print()
        print(f"📝 Found issues in {len(results)} files")
        print(f"   Report saved to: {OUTPUT_FILE}")
        print()
        print("Summary:")
        for filename, issues in results[:10]:  # Show first 10
            print(f"  • {filename}: {len(issues)} issues")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more files")
    else:
        print()
        print("✅ No issues found in any blog posts!")

if __name__ == "__main__":
    main()
