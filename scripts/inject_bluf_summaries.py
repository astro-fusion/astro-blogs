import os
import re

def clean_text_for_summary(text):
    text = re.sub(r'<FAQBlock.*?>.*?</FAQBlock>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[A-Za-z0-9]+[^>]*/>', '', text)
    text = re.sub(r'<[A-Za-z0-9]+[^>]*>.*?</[A-Za-z0-9]+>', '', text, flags=re.DOTALL)
    # Strip any remaining tags (e.g. nested tags or loose closing tags)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'\*\*|__|\*|_', '', text)
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_sentences(text, max_sentences=3):
    sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
    sentences = sentence_endings.split(text)
    cleaned_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) > 10:
            cleaned_sentences.append(s)
        if len(cleaned_sentences) >= max_sentences:
            break
    return " ".join(cleaned_sentences)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Pattern to find headings
    heading_pattern = re.compile(r'^(##\s+.*)$', re.MULTILINE)
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this line is a H2 heading
        if line.startswith('## '):
            heading_text = line[3:].strip()
            lower_heading = heading_text.lower()
            
            # Skip structural headings
            structural_keywords = [
                'table of contents', 
                'keywords', 
                'summary', 
                'navigation', 
                'related articles', 
                'external references', 
                'frequently asked questions', 
                'faq'
            ]
            if any(kw in lower_heading for kw in structural_keywords):
                i += 1
                continue
                
            # Check if the next non-empty line starts with <AIBlufSummary>
            next_non_empty = None
            next_idx = i + 1
            while next_idx < len(lines):
                if lines[next_idx].strip():
                    next_non_empty = lines[next_idx].strip()
                    break
                next_idx += 1
                
            if next_non_empty and next_non_empty.startswith('<AIBlufSummary>'):
                # Already has BLUF summary, skip
                i += 1
                continue
                
            # Extract content of this section to summarize
            section_lines = []
            scan_idx = i + 1
            while scan_idx < len(lines):
                if lines[scan_idx].startswith('##'):
                    break
                section_lines.append(lines[scan_idx])
                scan_idx += 1
                
            section_content = '\n'.join(section_lines).strip()
            cleaned = clean_text_for_summary(section_content)
            summary = extract_sentences(cleaned, 3)
            
            if summary:
                # Format summary nicely
                bluf_block = f"\n<AIBlufSummary>\n{summary}\n</AIBlufSummary>\n"
                new_lines.append(bluf_block)
                modified = True
                
        i += 1
        
    if modified:
        # Reconstruct and write back
        new_content = '\n'.join(new_lines)
        # Normalize double empty lines around AIBlufSummary block
        new_content = re.sub(r'\n{3,}', '\n\n', new_content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    # Find all directories that start with a digit
    dirs = [d for d in os.listdir('.') if os.path.isdir(d) and re.match(r'^\d+_', d)]
    dirs.sort()
    
    count = 0
    for d in dirs:
        for root, _, files in os.walk(d):
            files.sort()
            for file in files:
                if file.endswith('.mdx') and not file.startswith('_') and file not in ['README.mdx', 'GEMINI.mdx']:
                    file_path = os.path.join(root, file)
                    if process_file(file_path):
                        print(f"Injected BLUF summaries into {file_path}")
                        count += 1
    print(f"Successfully modified {count} MDX files across all categories.")

if __name__ == '__main__':
    main()
