#!/usr/bin/env python3
"""
Script to fix broken links in index.mdx based on actual file extensions in the filesystem.
"""

import os
import re
from pathlib import Path

def get_file_extension(filepath):
    """Get the actual file extension for a given path."""
    if os.path.exists(filepath + '.mdx'):
        return '.mdx'
    elif os.path.exists(filepath + '.md'):
        return '.md'
    else:
        return None

def fix_links_in_file():
    """Fix all the broken links in index.mdx."""
    index_file = 'index.mdx'

    # Read the file
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match markdown links with file paths
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)

        # Skip external links and anchor links
        if link_url.startswith('http') or '#' in link_url:
            return match.group(0)

        # Check if it's a file path that needs extension fixing
        if not link_url.endswith('.md') and not link_url.endswith('.mdx'):
            # This might be a directory link, leave it alone
            return match.group(0)

        # Remove extension to get base path
        base_path = link_url.rsplit('.', 1)[0]

        # Get the correct extension
        correct_ext = get_file_extension(base_path)

        if correct_ext:
            correct_url = base_path + correct_ext
            if correct_url != link_url:
                print(f"Fixing: {link_url} -> {correct_url}")
                return f'[{link_text}]({correct_url})'

        return match.group(0)

    # Fix all links
    fixed_content = re.sub(link_pattern, replace_link, content)

    # Additional fixes for specific issues

    # Fix double underscores in Moon Transit
    fixed_content = re.sub(r'20_Transit/02_Moon_Transit/(\d+)__([^)]+)', r'20_Transit/02_Moon_Transit/\1_\2', fixed_content)

    # Write back the file
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print("Links fixed!")

if __name__ == "__main__":
    fix_links_in_file()
