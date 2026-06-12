import os
import re
import json
import yaml

def clean_category_name(name):
    name = re.sub(r'^\d+_+', '', name)
    name = name.replace('_', ' ').strip()
    return name

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def normalize_slug(filename):
    base = os.path.splitext(filename)[0]
    base = re.sub(r'^\d+_+', '', base)
    slug = slugify(base)
    slug = slug.replace('-in-conjunction', '')
    return slug

def parse_frontmatter(fm_content):
    try:
        # First try direct yaml load
        data = yaml.safe_load(fm_content)
        if data:
            return data
    except:
        pass
    
    # If it fails, try to fix common issues like unquoted colons in title
    lines = fm_content.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('title:'):
            val = line[len('title:'):].strip()
            if val and not (val.startswith("'") or val.startswith('"')):
                # Quote the value
                new_lines.append(f"title: {json.dumps(val)}")
                continue
        if line.startswith('description:'):
            val = line[len('description:'):].strip()
            # If it's using > or |, don't mess with it yet
            if val and val not in ['>', '|']:
                if not (val.startswith("'") or val.startswith('"')):
                    new_lines.append(f"description: {json.dumps(val)}")
                    continue
        new_lines.append(line)
    
    try:
        data = yaml.safe_load('\n'.join(new_lines))
        if data:
            return data
    except:
        pass

    # Fallback to regex if yaml still fails
    data = {}
    title_match = re.search(r'^title:\s*(.*)$', fm_content, re.MULTILINE)
    if title_match:
        data['title'] = title_match.group(1).strip().strip("'").strip('"')
    
    desc_match = re.search(r'^description:\s*(.*)$', fm_content, re.MULTILINE)
    if desc_match:
        data['description'] = desc_match.group(1).strip().strip("'").strip('"')
        
    return data

def extract_sections(content):
    sections = []
    heading_pattern = re.compile(r'^(#{2,3})\s+(.*)$', re.MULTILINE)
    matches = list(heading_pattern.finditer(content))
    
    for i, match in enumerate(matches):
        heading_text = match.group(2).strip()
        heading_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', heading_text)
        
        # Filter out structural sections
        structural = ["Table of Contents", "Keywords", "Summary of Article", "Navigation", "Related Articles", "External References", "Conclusion", "FAQs", "Introduction"]
        # Wait, the prompt said:
        # Remove structural sections: "Table of Contents", "Keywords", "Summary of Article", 
        # "Navigation", "Related Articles", "External References", "FAQs about X".
        # I'll stick to those.
        
        if any(s.lower() == heading_text.lower() or heading_text.lower().startswith("faqs about") for s in ["Table of Contents", "Keywords", "Summary of Article", "Navigation", "Related Articles", "External References"]):
            continue
            
        sections.append({
            "id": f"sec-{slugify(heading_text)}",
            "heading": heading_text,
            "summary": "" 
        })
    return sections

def normalize_tree():
    tree = []
    top_level_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.') and d != 'scripts' and d != 'node_modules' and d != 'temp_categories']
    top_level_dirs.sort()

    category_map = {
        "House Lord Placements": "Lord in Houses",
        "Lords in Houses": "Lord in Houses",
        "Conjunctions": "Planets Conjunctions"
    }

    normalized_tree = {}
    
    slugs_normalized = 0
    summaries_filled = 0
    categories_merged = 0

    for d in top_level_dirs:
        raw_cat_name = clean_category_name(d)
        target_cat = category_map.get(raw_cat_name, raw_cat_name)
        
        if target_cat != raw_cat_name:
            categories_merged += 1
            
        if target_cat not in normalized_tree:
            normalized_tree[target_cat] = {
                "category": target_cat,
                "summary": "", 
                "children": []
            }
        
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.endswith('.mdx') and not file.startswith('_') and file not in ['README.mdx', 'GEMINI.mdx']:
                    file_path = os.path.join(root, file)
                    
                    old_slug = slugify(os.path.splitext(file)[0])
                    new_slug = normalize_slug(file)
                    if new_slug != old_slug:
                        slugs_normalized += 1
                    
                    # Read content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                    title = file.replace('.mdx', '')
                    description = ""
                    
                    if fm_match:
                        fm_content = fm_match.group(1)
                        fm = parse_frontmatter(fm_content)
                        title = fm.get('title', title)
                        description = fm.get('description', '')
                        body = content[fm_match.end():]
                    else:
                        body = content

                    if not description or len(description) < 80:
                        summaries_filled += 1
                        if not description or description == ">":
                            # Try to find first paragraph
                            paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and not p.strip().startswith('#') and not p.strip().startswith('<')]
                            if paragraphs:
                                description = f"Comprehensive guide to {title}. {paragraphs[0][:150]}..."
                            else:
                                description = f"In-depth analysis of {title} in Vedic astrology."

                    sections = extract_sections(body)
                    
                    normalized_tree[target_cat]['children'].append({
                        "title": title,
                        "slug": new_slug,
                        "summary": description.strip().replace('\n', ' ') if description else "",
                        "sections": sections
                    })

    # Convert back to list
    final_tree = list(normalized_tree.values())
    
    # Sort children by title for consistency
    for cat in final_tree:
        cat['children'].sort(key=lambda x: x['title'])

    # Specific Category Summary Fixes
    cat_summaries = {
        "Rasi": "Comprehensive guide to the twelve zodiac signs (Rashis) of Vedic astrology, detailing their characteristics, planetary rulers, and symbolic meanings.",
        "Houses": "Exploration of the twelve astrological houses (Bhavas), representing different life areas such as self, wealth, career, and spirituality.",
        "Planets": "Detailed analysis of the nine grahas (planets) in Vedic astrology, including their mythology, significations, and cosmic influences.",
        "DashaSystem": "Introduction to the predictive time cycles of Vedic astrology, including Vimsottari and Yogini dasha systems for timing life events.",
        "Nakshatra": "In-depth study of the 27 lunar mansions (Nakshatras) and their profound influence on personality and destiny.",
        "Planet in Houses": "Analyzing the impact and results of each planet's placement across the twelve houses of the birth chart.",
        "Planet in Rashi": "How planets manifest their energies when placed in different zodiac signs, from Aries to Pisces.",
        "Lord in Houses": "Detailed results of house lords placed in various houses, a key component of predictive Vedic astrology.",
        "Planets Conjunctions": "The results of multiple planets combining their energies in a single house (Yogas and Doshas).",
        "Ashtakavarga": "Numerical system of Vedic astrology used to determine the strength and auspiciousness of planetary transits.",
        "Divisional Charts": "Advanced study of Varga charts like Navamsha (D9) and Dashamamsha (D10) for micro-analysis of life areas.",
        "Transit": "Understanding the dynamic movement of planets and their current impact on the natal birth chart.",
        "Medical Astrology": "The relationship between planetary positions and physical health, body parts, and potential ailments.",
        "Vastu": "The ancient Indian science of architecture and spatial arrangement in harmony with cosmic energies.",
        "Numerology": "Exploring the mystical relationship between numbers, planetary vibrations, and human life.",
        "Planet in Nakshatra": "Refined analysis of planetary results based on their placement in specific lunar mansions.",
        "Calculations": "Technical methodologies for calculating planetary strengths (Shadbala) and other mathematical aspects of Jyotish.",
        "Articles": "General articles, chart analyses, and blog posts exploring various facets of Vedic wisdom.",
        "Remedies": "Practical Vedic solutions, mantras, and rituals to balance planetary energies and mitigate challenges."
    }

    for cat in final_tree:
        if cat['category'] in cat_summaries:
            cat['summary'] = cat_summaries[cat['category']]

    with open('blog-index-tree.json', 'w') as f:
        json.dump(final_tree, f, indent=2)

    print(f"Categories Merged: {categories_merged}")
    print(f"Slugs Normalized: {slugs_normalized}")
    print(f"Summaries Checked/Filled: {summaries_filled}")

if __name__ == "__main__":
    normalize_tree()
