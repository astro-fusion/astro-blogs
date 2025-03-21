#!/usr/bin/env python3
import json
import os
from pathlib import Path

def generate_index_from_meta(meta_file='_meta_new.json', output_file='index.mdx'):
    """Generate index.mdx file from the meta.json structure"""
    
    # Load meta data
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta_data = json.load(f)
    
    # Start building the index content
    content = [
        "# Vedic Astrology",
        "",
        "Welcome to the Astro-Blogs: Vedic Astrology documentation. This site is a comprehensive guide to the principles and practices of Vedic astrology, also known as Jyotisha. Explore the various facets of this ancient system, including the zodiac signs, houses, planets, dashas, and more. Click on any section below to delve deeper into the fascinating world of Vedic astrology.",
        "",
        "## Sections",
        ""
    ]
    
    # Process each category
    for category in meta_data.get("Vedic Astrology", []):
        # Add category header
        content.append(f"### [{category['title']}]({category['folder']})")
        
        # Add category description if needed
        description = get_category_description(category['title'])
        if description:
            content.append(f"_{description}_")
        
        # Process children
        process_children(category, content, 0)
        content.append("")  # Add spacing between categories
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"Generated {output_file} with {len(meta_data.get('Vedic Astrology', []))} main sections")

def process_children(item, content, level):
    """Recursively process children items and add them to content"""
    if "children" not in item:
        return
    
    for child in item["children"]:
        if "children" in child:  # This is a subcategory
            # Add subcategory with proper indentation
            indent = "  " * level
            content.append(f"{indent}- [{child['title']}]({child['folder']})")
            
            # Add description for subcategory if needed
            description = get_category_description(child['title'])
            if description:
                content.append(f"{indent}  _{description}_")
            
            # Process its children
            process_children(child, content, level + 1)
        else:  # This is a file
            indent = "  " * level
            content.append(f"{indent}- [{child['title']}]({child['path']})")

def get_category_description(category_name):
    """Return description for a category"""
    descriptions = {
        "Rasi": "The Rasi, or zodiac signs, represent the twelve divisions of the ecliptic, each with unique characteristics.",
        "Houses": "The twelve houses of the birth chart represent different areas of life, such as self, wealth, family, and career.",
        "Planets": "The planets are the primary actors in the astrological chart, influencing various aspects of life based on their positions.",
        "Dasha System": "Dasha systems are planetary periods that indicate the timing of events in a person's life.",
        "Vimsottari Dasha": "Vimsottari Dasha is a widely used dasha system based on a 120-year cycle.",
        "Yogani Dasha": "Yogini Dasha is another type of dasha system that focuses on the effects of the eight Yoginis.",
        "Nakshatra": "Nakshatras are the lunar mansions, or constellations, that the Moon passes through, adding another layer to astrological interpretation.",
        "Planet in Houses": "The placement of each planet in a specific house further defines their influence on the individual.",
        "House Lord Placements": "Analyzing where the lord of each house is placed reveals the strengths and weaknesses of that house's domain.",
        "Planet in Rasi Placement": "The Rasi (sign) in which a planet is placed modifies its nature and expression.",
        "Remedies": "Remedies in Vedic astrology provide ways to mitigate negative planetary influences and enhance positive ones.",
        "Lord in Houses": "This section explores the effects when the lord of one house is placed in another house.",
        "Planets Conjunctions": "Planetary conjunctions, where two or more planets are close together, create unique and significant effects.",
        "Chart Analysis": "This section covers the holistic process of interpreting a birth chart, integrating the knowledge of all the above elements.",
        "Planet in Nakshatra": "Understanding the placement of planets within specific nakshatras provides deeper insights.",
        "Ashtakavarga": "Ashtakavarga is a system for evaluating the strength and beneficence of each planet.",
        "Vastu": "Vastu Shastra is the ancient Indian science of architecture and environment, aiming to harmonize spaces with natural forces.",
        "Numerology": "Numerology explores the hidden meanings of numbers and their influence on human lives.",
        "Upagrahas": "Upagrahas are shadow planets or sub-planets that add further nuance to a chart analysis."
    }
    
    return descriptions.get(category_name, "")

if __name__ == "__main__":
    generate_index_from_meta()
    print("Index.mdx generation complete!")
    