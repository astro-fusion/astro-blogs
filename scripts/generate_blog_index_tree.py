import os
import re
import json
import yaml

def clean_name(name):
    # Strip leading digits and underscores/spaces
    name = re.sub(r'^\d+_+', '', name)
    name = re.sub(r'^\d+\s+', '', name)
    # Replace underscores with spaces and strip trailing spaces
    return name.replace('_', ' ').strip()

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def clean_text_for_summary(text):
    # Remove FAQBlock or any react component tags/imports
    text = re.sub(r'<FAQBlock.*?>.*?</FAQBlock>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[A-Za-z0-9]+[^>]*/>', '', text)
    text = re.sub(r'<[A-Za-z0-9]+[^>]*>.*?</[A-Za-z0-9]+>', '', text, flags=re.DOTALL)
    
    # Remove markdown links
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove formatting (bold, italics, etc)
    text = re.sub(r'\*\*|__|\*|_', '', text)
    # Remove table markup
    text = re.sub(r'\|', ' ', text)
    # Remove standard bullets/list markers
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_sentences(text, max_sentences=2):
    # Split text by sentence endings (. ! ?) while avoiding splitting on abbreviations or numbers
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

def extract_sections(content, title):
    sections = []
    # Find ## and ### headings
    heading_pattern = re.compile(r'^(#{2,3})\s+(.*)$', re.MULTILINE)
    matches = list(heading_pattern.finditer(content))
    
    for i, match in enumerate(matches):
        heading_text = match.group(2).strip()
        # Remove formatting/links from heading
        heading_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', heading_text)
        heading_text = re.sub(r'\*\*|__|\*|_', '', heading_text)
        
        # Check if the heading is structural and should be skipped
        lower_heading = heading_text.lower()
        structural_keywords = [
            'table of contents', 
            'keywords', 
            'summary of article', 
            'navigation', 
            'related articles', 
            'external references', 
            'frequently asked questions', 
            'faq'
        ]
        if any(kw in lower_heading for kw in structural_keywords):
            continue
            
        start = match.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        section_content = content[start:end].strip()
        
        # Check if there is an AIBlufSummary tag
        bluf_match = re.search(r'<AIBlufSummary>(.*?)</AIBlufSummary>', section_content, re.DOTALL)
        if bluf_match:
            summary = clean_text_for_summary(bluf_match.group(1))
        else:
            cleaned = clean_text_for_summary(section_content)
            summary = extract_sentences(cleaned, 2)
            
        if not summary:
            summary = f"This section discusses the astrological characteristics, significance, and details of {heading_text} in relation to {title}."
            
        # Ensure it has a trailing period
        if not summary.endswith('.'):
            summary += '.'
            
        sections.append({
            "id": f"sec-{slugify(heading_text)}",
            "heading": heading_text,
            "summary": summary
        })
    return sections

def get_category_summary(category_name):
    summaries = {
        "Rasi": "Explores the twelve zodiac signs (Rasis) of Vedic astrology, detailing their characteristics, planetary rulers, nakshatra divisions, and house placements.",
        "Houses": "Covers the twelve astrological houses (Bhavas), explaining their significance, areas of life influenced, and planetary relationships.",
        "Planets": "Provides in-depth profiles of the nine grahas (planets) in Vedic astrology, including their characteristics, significations, and cosmic roles.",
        "DashaSystem": "Explains the planetary period systems (Dashas), particularly Vimshottari Dasha, detailing their timing mechanics and life effects.",
        "Nakshatra": "Details the 27 lunar mansions (Nakshatras), exploring their mythological symbols, ruling deities, planetary lords, and psychological profiles.",
        "Planet in Houses": "Analyzes the specific astrological impact, benefits, and challenges of different planets placed across the twelve houses.",
        "Calculations": "Covers mathematical and astronomical calculations in Jyotish, including planetary positions, divisional charts, and strength measurements.",
        "House Lord Placements": "Analyzes the placements and effects of house lords residing in different houses.",
        "Conjunctions": "Explores planetary alignments and conjunctions, detailing how combined energies of grahas affect human life and destiny.",
        "Planet in Rashi": "Details the characteristics and astrological outcomes of various planets residing in the twelve zodiac signs.",
        "Lords in Houses": "Analyzes the placements and effects of house lords residing in different houses.",
        "Remedies": "Suggests Vedic remedial measures (Upayas) such as mantras, gemstones, fasting, and charity to balance planetary energies.",
        "Lord in Houses": "Analyzes the placements and effects of house lords residing in different houses.",
        "Planets Conjunctions": "Explores planetary alignments and conjunctions, detailing how combined energies of grahas affect human life and destiny.",
        "Articles": "Miscellaneous articles on Vedic astrology concepts, advanced techniques, and historical contexts.",
        "Divisional Charts": "Explores divisional charts (Vargas) like Navamsa (D9) and Dashamsa (D10) for micro-analysis of specific life areas.",
        "Planet in Nakshatra": "Analyzes the placement of different planets in the 27 nakshatras and their specific life predictions.",
        "Ashtakavarga": "Explores the Ashtakavarga system, a quantitative scoring method used to evaluate planetary strength and transit effects.",
        "Vastu": "Covers Vastu Shastra, the ancient Vedic science of architecture and spatial design for harmony and prosperity.",
        "Medical Astrology": "Details the correlation between astrological configurations, planets, signs, houses, and physical health, diseases, and remedies.",
        "Transit": "Explores transit (Gochar) analysis, detailing the movement of planets through houses and signs and their timing of events.",
        "Numerology": "Covers Vedic numerology, analyzing numbers, birth dates, name numbers, and their astrological vibrations."
    }
    return summaries.get(category_name, f"Comprehensive guide and articles about {category_name} in Vedic astrology.")

def process_repo():
    tree = []
    
    # List top level directories starting with a digit
    dirs = [d for d in os.listdir('.') if os.path.isdir(d) and re.match(r'^\d+_', d)]
    dirs.sort()
    
    for d in dirs:
        category_name = clean_name(d)
        category_obj = {
            "category": category_name,
            "summary": get_category_summary(category_name),
            "children": []
        }
        
        # Walk to find all .mdx files
        for root, _, files in os.walk(d):
            # Sort files to ensure deterministic output
            files.sort()
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
                            except Exception as ye:
                                fm = {}
                                # Fallback regex matching for title and description
                                title_m = re.search(r"^title:\s*['\"]?(.*?)['\"]?$", fm_content, re.MULTILINE)
                                desc_m = re.search(r"^description:\s*['\"]?(.*?)['\"]?$", fm_content, re.MULTILINE)
                                if title_m: fm['title'] = title_m.group(1)
                                if desc_m: fm['description'] = desc_m.group(1)
                        else:
                            fm = {}
                            body = content
                            
                        # Use clean slug based on title if filename is not preferred, or filename without prefix
                        # Clean filename prefix (e.g. 0101_Mesha -> Mesha -> mesha)
                        base_file = os.path.splitext(file)[0]
                        clean_base = re.sub(r'^\d+_+', '', base_file)
                        slug = slugify(clean_base)
                        
                        title = fm.get('title', clean_name(base_file))
                        summary = fm.get('description', '')
                        
                        sections = extract_sections(body, title)
                        
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
    with open('blog-index-tree.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Successfully processed {len(result)} categories and generated blog-index-tree.json.")
