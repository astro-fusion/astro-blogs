#!/usr/bin/env python3
"""
Validation script for Saturn transit blogs.
Checks for common issues in Saturn transit content files.
"""

import os
import sys
import yaml
import re
from pathlib import Path

def validate_frontmatter(content, file_path):
    """Validate frontmatter in a markdown file."""
    errors = []

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Missing or invalid frontmatter (should start and end with ---)")
        return errors

    frontmatter_text = frontmatter_match.group(1)

    try:
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in frontmatter: {e}")
        return errors

    # Required fields
    required_fields = ['title', 'description', 'pubDate']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate title format
    if 'title' in data and not isinstance(data['title'], str):
        errors.append("Title must be a string")

    # Validate description
    if 'description' in data and not isinstance(data['description'], str):
        errors.append("Description must be a string")

    return errors

def validate_content(content, file_path):
    """Validate the content structure."""
    errors = []

    # Check for required sections
    required_sections = [
        '## Keywords',
        '## Summary',
        '## The Transit of'
    ]

    content_lower = content.lower()
    for section in required_sections:
        if section.lower() not in content_lower:
            # More flexible check - look for variations
            section_variations = [
                section.lower(),
                section.lower().replace('## ', ''),
                section.lower().replace('the transit of', 'saturn transit')
            ]
            found = any(var in content_lower for var in section_variations)
            if not found:
                errors.append(f"Missing required section: {section}")

    # Check for broken links (basic check)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)
    for link_text, link_url in links:
        if not link_url.endswith('.md') and not link_url.startswith('http'):
            errors.append(f"Potentially broken link: [{link_text}]({link_url})")

    return errors

def validate_file(file_path):
    """Validate a single file."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Failed to read file: {e}"]

    # Validate frontmatter
    errors.extend(validate_frontmatter(content, file_path))

    # Validate content
    errors.extend(validate_content(content, file_path))

    return errors

def main():
    # Use relative path from script location
    directory = os.path.dirname(os.path.abspath(__file__))

    print(f"Validating Saturn transit blogs in: {directory}")

    # Find all .md files in the directory
    md_files = []
    for file in os.listdir(directory):
        if file.endswith('.md') and not file.startswith('.'):
            md_files.append(os.path.join(directory, file))

    if not md_files:
        print("No .md files found to validate.")
        return

    total_errors = 0

    for file_path in sorted(md_files):
        file_name = os.path.basename(file_path)
        errors = validate_file(file_path)

        if errors:
            print(f"\n❌ {file_name}:")
            for error in errors:
                print(f"  - {error}")
            total_errors += len(errors)
        else:
            print(f"✅ {file_name}: OK")

    print(f"\nValidation complete. Total errors: {total_errors}")

    if total_errors > 0:
        print("Please fix the errors above.")
        sys.exit(1)
    else:
        print("All files validated successfully!")

if __name__ == "__main__":
    main()
