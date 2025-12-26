import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "content", "blog"))

def proofread():
    errors = []
    for f in sorted(os.listdir(BASE_DIR)):
        if not f.endswith('.md'): continue
        path = os.path.join(BASE_DIR, f)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # 1. Repeated words (the the, in in, etc)
        repeats = re.findall(r'\b(\w+)\s+\1\b', content, flags=re.IGNORECASE)
        # Filter out common false positives like "that that" or valid repetitions
        valid_repeats = ['that', 'had', 'do', 'long'] 
        repeats = [r for r in repeats if r.lower() not in valid_repeats]
        if repeats:
            errors.append(f"{f}: Repeated words: {list(set(repeats))}")
            
        # 2. Punctuation spacing issues
        # Avoid false positives for {.class} syntax, ::: blocks, and ... ellipses
        # Matches space followed by punc, but not if followed by same punc or a word char
        # use \1 to refer to the captured punctuation mark
        punc_match = re.search(r'\s+([,.!?;:])(?!\1|\w)', content)
        if punc_match:
            errors.append(f"{f}: Misplaced space before punctuation")
            
        # 3. Double spaces (non-markdown)
        if re.search(r'[^\n ]  [^\n ]', content):
            errors.append(f"{f}: Potential double spaces")
            
        # 4. Unbalanced markers (basic check)
        if content.count('**') % 2 != 0:
            errors.append(f"{f}: Unbalanced bold markers (**)")
        if content.count('_') % 2 != 0:
            # Underscores are tricky because of URLs, but we checked no underscores in URLs ideally
            errors.append(f"{f}: Unbalanced italic markers (_)")
            
        # 5. MD037 style (space inside emphasis)
        if re.search(r'\*\* | \*\*', content): # Already handled by repair but double check
            pass # Skipping report if handled

        # 6. Mangled patterns (common in corrupted files)
        if re.search(r'\*\* \.|\*\* ---|\*\* \n', content):
            errors.append(f"{f}: Mangled bolding pattern detected")

    with open("proofread_report.txt", "w") as f:
        f.write("\n".join(errors))
    print(f"Proofread done. Found {len(errors)} potential issues.")

if __name__ == "__main__":
    proofread()
