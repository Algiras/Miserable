import os
import re
import textwrap

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "content", "blog"))
MAX_WIDTH = 110

def clean_punctuation_spacing(text):
    # Fix "word , word" -> "word, word"
    text = re.sub(r'(\w)\s+([,!?;:])', r'\1\2', text)
    # Fix cases where a space is missing after punctuation: "word.Word" -> "word. Word"
    # Negative lookahead for common abbreviations or decimal points
    text = re.sub(r'([,!?;:])([A-Za-z])', r'\1 \2', text)
    # Fix double spaces
    text = re.sub(r'  +', ' ', text)
    return text

def balance_bold(text):
    # Strip any ** that are clearly malformed or trailing
    # One common issue is "** - " at start being counted in pairs wrongly.
    # We want to balance bold ONLY within the block of text.
    
    # MD037 fix: " ** " -> " **" and "** " -> "**"
    text = re.sub(r'\s+\*\*', ' **', text)
    text = re.sub(r'\*\*\s+', '** ', text)
    
    count = text.count('**')
    if count % 2 == 0:
        return text
    
    # If the last word has ** at the end of a sentence but no opener, or vice versa
    # Heuristic: Append ** if it seems to be an unclosed opener
    return text.rstrip() + "**"

def repair_post(path, title):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r'^---$', content, flags=re.MULTILINE)
    if len(parts) < 3: return
    fm = parts[1]
    body = "---".join(parts[2:]).strip()

    # Split into blocks
    raw_lines = body.split('\n')
    blocks = []
    current_type = None
    current_lines = []
    in_code = False

    def flush():
        nonlocal current_lines, current_type
        if current_lines:
            blocks.append((current_type, current_lines))
        current_lines = []
        current_type = None

    for line in raw_lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            if not in_code: flush(); in_code = True; current_type = 'code'; current_lines.append(line)
            else: current_lines.append(line); in_code = False; flush()
            continue
        if in_code: current_lines.append(line); continue
        if not stripped: flush(); continue

        line_type = 'text'
        if stripped.startswith('#'): line_type = 'head'
        elif stripped.startswith('>'): line_type = 'quote'
        elif stripped.startswith('|'): line_type = 'table'
        elif stripped == '---': line_type = 'sep'
        elif re.match(r'^([\*\-\+]\s|\d+\.\s|✅\s)', stripped): line_type = 'list'
        elif stripped.startswith(':::'): line_type = 'callout'
        
        if line_type == 'head' or line_type == 'sep':
            flush()
            blocks.append((line_type, [stripped]))
            continue
            
        if line_type != current_type:
            flush()
            current_type = line_type
        current_lines.append(stripped)
    flush()

    output = []
    for b_type, b_lines in blocks:
        if b_type == 'text':
            text = " ".join(b_lines)
            text = clean_punctuation_spacing(text)
            text = balance_bold(text)
            wrapped = textwrap.fill(text, width=MAX_WIDTH, break_long_words=False)
            output.append(wrapped + "\n\n")
        elif b_type == 'quote':
            text = " ".join([l.lstrip('>').strip() for l in b_lines])
            text = clean_punctuation_spacing(text)
            text = balance_bold(text)
            wrapped = textwrap.fill(text, width=MAX_WIDTH, initial_indent="> ", subsequent_indent="> ", break_long_words=False)
            output.append(wrapped + "\n\n")
        elif b_type == 'list':
            items = []
            curr_item = None
            for l in b_lines:
                m = re.match(r'^([\*\-\+]\s|\d+\.\s|✅\s)', l)
                if m:
                    if curr_item: items.append(curr_item)
                    curr_item = {'prefix': m.group(0), 'content': l[len(m.group(0)):].strip()}
                else:
                    if curr_item: curr_item['content'] += " " + l
            if curr_item: items.append(curr_item)
            for item in items:
                content = balance_bold(clean_punctuation_spacing(item['content']))
                wrapped = textwrap.fill(content, width=MAX_WIDTH, initial_indent=item['prefix'], subsequent_indent=" " * len(item['prefix']), break_long_words=False)
                output.append(wrapped + "\n")
            output.append("\n")
        elif b_type == 'head':
            output.append(balance_bold(b_lines[0]) + "\n\n")
        elif b_type == 'callout':
            output.append("\n".join(b_lines) + "\n\n")
        elif b_type == 'sep':
            output.append("---\n\n")
        else:
            output.append("\n".join(b_lines) + "\n\n")

    healed_body = "".join(output).strip()
    
    # Final global spacing cleanup
    # Remove any stray ** at end of file if odd (rare)
    if healed_body.count('**') % 2 != 0:
         healed_body = healed_body.rstrip() + "**"

    final_content = f"---\n{fm.strip()}\n---\n\n{healed_body}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(final_content)

if __name__ == "__main__":
    for f in sorted(os.listdir(BASE_DIR)):
        if not f.endswith('.md'): continue
        path = os.path.join(BASE_DIR, f)
        with open(path, "r", encoding="utf-8") as file:
            c = file.read()
        parts = re.split(r'^---$', c, flags=re.MULTILINE)
        if len(parts) < 3: continue
        title_m = re.search(r'title:\s*"(.*?)"', parts[1])
        title = title_m.group(1) if title_m else ""
        repair_post(path, title)
        print(f"Proofed {f}")
