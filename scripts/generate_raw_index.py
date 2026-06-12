import os
import re
import json
import yaml

def clean_name(name):
    return re.sub(r'^\d+_+', '', name).replace('_', ' ').strip()

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def extract_sections(content):
    sections = []
    # Find ## and ### headings
    heading_pattern = re.compile(r'^(#{2,3})\s+(.*)$', re.MULTILINE)
    matches = list(heading_pattern.finditer(content))
    
    for i, match in enumerate(matches):
        heading_text = match.group(2).strip()
        # Remove markdown links or other formatting from heading
        heading_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', heading_text)
        
        start = match.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        section_content = content[start:end].strip()
        
        # Take first 200 chars for summary generation later or just use as is
        sections.append({
            "id": f"sec-{slugify(heading_text)}",
            "heading": heading_text,
            "content_sample": section_content[:500] # Give enough context for summary
        })
    return sections

def process_repo():
    tree = []
    top_level_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.') and d != 'scripts' and d != 'node_modules']
    top_level_dirs.sort()

    for d in top_level_dirs:
        category_name = clean_name(d)
        category_obj = {
            "category": category_name,
            "summary": "", # To be filled by LLM
            "children": []
        }
        
        # Walk through the directory to find all .mdx files
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.endswith('.mdx') and not file.startswith('_') and file not in ['README.mdx', 'GEMINI.mdx']:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract frontmatter
                        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                        if fm_match:
                            fm_content = fm_match.group(1)
                            body = content[fm_match.end():]
                            try:
                                fm = yaml.safe_load(fm_content)
                            except:
                                fm = {}
                        else:
                            fm = {}
                            body = content
                            
                        title = fm.get('title', file.replace('.mdx', ''))
                        summary = fm.get('description', '')
                        slug = slugify(os.path.splitext(file)[0])
                        
                        sections = extract_sections(body)
                        
                        category_obj["children"].append({
                            "title": title,
                            "slug": slug,
                            "summary": summary,
                            "sections": sections
                        })
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        if category_obj["children"]:
            tree.append(category_obj)
            
    return tree

if __name__ == "__main__":
    result = process_repo()
    with open('raw-index-structure.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f"Processed {len(result)} categories.")
