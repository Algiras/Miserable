import os
import re
import requests
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "content", "blog"))
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "ministral-3:8b"

def get_critique(content):
    prompt = f"""You are a professional editor and proofreader. 
Review the following blog post excerpt for:
1. Typos or glaring grammatical errors.
2. Logic gaps or broken sentences.
3. Stylistic inconsistencies.

Format your response as a concise list of fixes. If no issues, reply "OK".

CONTENT:
{content}
"""
    try:
        data = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=data)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"

def main():
    report = []
    files = sorted([f for f in os.listdir(BASE_DIR) if f.endswith('.md')])
    
    # Let's process a few at a time for testing or provide a way to do all
    print(f"Total files: {len(files)}")
    
    for f in files:
        path = os.path.join(BASE_DIR, f)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Strip frontmatter
        parts = re.split(r'^---$', content, flags=re.MULTILINE)
        if len(parts) >= 3:
            body = "---".join(parts[2:]).strip()
        else:
            body = content

        print(f"Auditing {f}...")
        # To avoid context limits and speed up, we'll take the first 4000 chars or chunk it
        # Most of these are moderate length. 4000-8000 should be safe.
        critique = get_critique(body[:8000]) 
        
        if critique and critique != "OK":
            report.append(f"### {f}\n{critique}\n")

    with open("llm_audit_report.md", "w") as out:
        out.write("# LLM Proofread Report (ministral-3:8b)\n\n")
        out.write("\n".join(report))
    
    print("Audit complete. See llm_audit_report.md")

if __name__ == "__main__":
    main()
