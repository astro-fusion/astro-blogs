import os
import json
import re
import yaml
from pathlib import Path

def extract_frontmatter(content):
    """Extract frontmatter from markdown content."""
    frontmatter_match = re.match(r'^---\s*(.*?)\s*---', content, re.DOTALL)
    if frontmatter_match:
        try:
            # Add safe handling for multi-line strings
            return yaml.safe_load(frontmatter_match.group(1).replace('\t', '  '))
        except yaml.YAMLError as e:
            print(f"Error parsing frontmatter: {e}")
            return {'title': 'INVALID FRONTMATTER'}  # Add fallback
    return {}

def process_directory(directory, root_path):
    """Recursively process directories and build meta structure"""
    entries = []
    
    for item in sorted(os.listdir(directory)):
        item_path = Path(directory) / item
        rel_path = item_path.relative_to(root_path)
        
        if item.startswith('.'):
            continue
            
        if item_path.is_dir():
            # Process directory
            dir_entry = {
                "title": format_title(item),
                "folder": str(rel_path),
                "children": process_directory(item_path, root_path)
            }
            entries.append(dir_entry)
        elif item.endswith('.md'):
            # Process markdown file
            try:
                content = item_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⛔ Error reading {rel_path}: {e}")
                continue
                
            frontmatter = extract_frontmatter(content)
            entries.append({
                "name": item,
                "title": frontmatter.get('title', format_title(item)),
                "path": str(rel_path)
            })
    
    return entries

def format_title(filename):
    """Convert filename to human-readable title"""
    # Remove numeric prefixes and extensions
    name = re.sub(r'^\d+_', '', filename).replace('.md', '')
    # Convert underscores and hyphens to spaces, then title case
    return ' '.join([word.capitalize() for word in re.split(r'[_-]+', name)])

def generate_meta_json(root_dir='.'):
    """Generate _meta.json file with proper hierarchy"""
    root_path = Path(root_dir).resolve()
    meta_structure = {"Vedic Astrology": []}
    
    # Process each main category directory (sorted alphabetically)
    for item in sorted(os.listdir(root_path)):
        item_path = root_path / item
        if item.startswith('.') or not item_path.is_dir():
            continue
            
        category_entry = {
            "title": format_title(item),
            "folder": item,
            "children": process_directory(item_path, root_path)
        }
        meta_structure["Vedic Astrology"].append(category_entry)
    
    # Save to file
    with open('_meta_new.json', 'w', encoding='utf-8') as f:
        json.dump(meta_structure, f, indent=2, ensure_ascii=False)
    
    total_entries = sum(len(c["children"]) for c in meta_structure["Vedic Astrology"])
    print(f"Generated _meta.json with {total_entries} entries across {len(meta_structure['Vedic Astrology'])} categories")

if __name__ == "__main__":
    generate_meta_json()
