#!/usr/bin/env python3
"""
Fixes any improperly folded titles in frontmatter and <KundaliChart /> tags.
"""

import os
import re
import yaml
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def fix_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # 1. Extract proper title
    fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---", content)
    real_title = None
    if fm_match:
        try:
            parsed = yaml.safe_load(fm_match.group(1))
            if isinstance(parsed, dict) and parsed.get("title") and parsed.get("title") != ">-":
                real_title = parsed["title"]
        except Exception:
            pass

    if not real_title or real_title == ">-":
        # Search for # Heading
        h1_match = re.search(r"^#\s+(.*)$", content, re.MULTILINE)
        if h1_match:
            real_title = h1_match.group(1).strip()
        else:
            real_title = file_path.stem.replace("_", " ")

    # Clean title
    real_title = real_title.strip("'\"")

    # Replace title=">-" or title="|" in KundaliChart
    content = re.sub(r'<KundaliChart\s+title=["\'][>|]-?["\']', f'<KundaliChart\n  title="{real_title}"', content)

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        print(f"Fixed: {file_path.relative_to(ROOT_DIR)}")

def run_fix():
    print("Fixing all multiline titles in <KundaliChart>...")
    for ext in ["*.mdx", "*.md"]:
        for f in ROOT_DIR.glob(f"**/{ext}"):
            if "node_modules" in f.parts or ".git" in f.parts or "scripts" in f.parts:
                continue
            fix_file(f)
    print("Done fixing titles!")

if __name__ == "__main__":
    run_fix()
