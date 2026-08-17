#!/usr/bin/env python3
"""
Rebuilds blog index trees and updates _meta.json for all supported locales:
- blog-en-index-tree.json
- blog-hi-index-tree.json
- blog-ne-index-tree.json
- _meta.json (Master multilingual index)
- _multilang_meta.json
"""

import os
import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

LOCALES = ["en", "hi", "ne"]

def extract_frontmatter(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n([\s\S]*?)\n---", content)
        if not match:
            return {}
        
        raw_yaml = match.group(1)
        meta = {}
        for line in raw_yaml.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("-") and not line.startswith("#"):
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip().strip("'\"")
        return meta
    except Exception:
        return {}

def scan_locale_tree(locale: str):
    locale_dir = ROOT_DIR / locale
    if not locale_dir.exists():
        return []

    articles = []
    for mdx_file in sorted(locale_dir.glob("**/*.md*")):
        rel_path = mdx_file.relative_to(locale_dir).as_posix()
        fm = extract_frontmatter(mdx_file)
        
        leaf_name = mdx_file.stem
        title = fm.get("title", leaf_name.replace("_", " "))
        desc = fm.get("description", "")
        
        articles.append({
            "path": rel_path,
            "title": title,
            "description": desc,
            "locale": locale,
        })
    return articles

def generate_indexes():
    print("Scanning and rebuilding locale indexes...")
    master_meta = {}

    for loc in LOCALES:
        articles = scan_locale_tree(loc)
        out_file = ROOT_DIR / f"blog-{loc}-index-tree.json"
        
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"locale": loc, "count": len(articles), "articles": articles}, f, ensure_ascii=False, indent=2)
        
        print(f"  • {out_file.name}: {len(articles)} articles indexed.")
        
        for art in articles:
            p = art["path"]
            if p not in master_meta:
                master_meta[p] = {
                    "path": p,
                    "availableLocales": [loc],
                    "title": art["title"],
                }
            else:
                if loc not in master_meta[p]["availableLocales"]:
                    master_meta[p]["availableLocales"].append(loc)

    # Master multilingual meta
    master_meta_file = ROOT_DIR / "_multilang_meta.json"
    with open(master_meta_file, "w", encoding="utf-8") as f:
        json.dump(master_meta, f, ensure_ascii=False, indent=2)
    print(f"Master index updated -> {master_meta_file.name}")

    # Also update _meta.json with multilingual indices
    meta_file = ROOT_DIR / "_meta.json"
    meta_content = {
        "locales": LOCALES,
        "totalArticles": len(master_meta),
        "articles": master_meta,
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta_content, f, ensure_ascii=False, indent=2)
    print(f"Master _meta.json updated -> {meta_file.name}")

    print("Index generation complete!")

if __name__ == "__main__":
    generate_indexes()

