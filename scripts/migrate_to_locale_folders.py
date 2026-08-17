#!/usr/bin/env python3
"""
Migrate astro-blogs content into folder-based locale structure:
astro-blogs/
├── en/
│   ├── 01_Rasi/
│   ├── 06_Planet_in_Houses/
│   ├── 10_Lord_in_Houses/
│   └── ...
├── hi/
└── ne/

Maintains backward compatibility for root index and meta.
"""

import os
import shutil
import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
EN_DIR = ROOT_DIR / "en"
HI_DIR = ROOT_DIR / "hi"
NE_DIR = ROOT_DIR / "ne"

CATEGORIES = [
    "01_Rasi",
    "02_Houses",
    "03_Planets",
    "04_DashaSystem",
    "05_Nakshatra",
    "06_Planet_in_Houses",
    "07_Calculations",
    "07_House_Lord_Placements",
    "08_Conjunctions",
    "08_Planet_in_Rashi",
    "09_Lords_in_Houses",
    "09_Remedies",
    "10_Lord_in_Houses",
    "11_Planets_Conjunctions",
    "12_Articles",
    "14_Divisional_Charts",
    "16_Planet_in_Nakshatra",
    "17_Ashtakavarga",
    "18_Vastu",
    "19_Medical_Astrology",
    "20_Transit",
    "21_Numerology",
]

def inject_locale_metadata(file_path: Path, locale="en"):
    content = file_path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---", content)
    if not fm_match:
        # If no frontmatter, create one
        title = file_path.stem.replace("_", " ")
        header = f"---\ntitle: \"{title}\"\ndescription: \"Vedic astrology guide to {title}.\"\npubDate: '2026-08-17'\nmodifiedDate: '2026-08-17'\nlocale: '{locale}'\nsourceLocale: 'en'\nkeywords:\n  - \"{title}\"\n  - \"Vedic Astrology\"\n---\n\n"
        file_path.write_text(header + content, encoding="utf-8")
        return

    raw_yaml = fm_match.group(1)
    new_yaml = raw_yaml

    if "locale:" not in new_yaml:
        new_yaml = new_yaml.strip() + f"\nlocale: '{locale}'\nsourceLocale: 'en'\n"

    if "keywords:" not in new_yaml and "tags:" not in new_yaml:
        title_match = re.search(r"title:\s*['\"]?(.*?)['\"]?(?:\n|$)", new_yaml)
        title = title_match.group(1).strip() if title_match else file_path.stem
        new_yaml = new_yaml.strip() + f"\nkeywords:\n  - \"{title}\"\n  - \"Vedic Astrology\"\n"

    new_content = f"---\n{new_yaml.strip()}\n---\n" + content[fm_match.end():].lstrip("\n")
    file_path.write_text(new_content, encoding="utf-8")


def migrate_to_en(dry_run=True):
    print(f"[{'DRY-RUN' if dry_run else 'EXECUTE'}] Checking categories to copy into en/ folder...")
    EN_DIR.mkdir(exist_ok=True)
    HI_DIR.mkdir(exist_ok=True)
    NE_DIR.mkdir(exist_ok=True)

    for cat in CATEGORIES:
        src_path = ROOT_DIR / cat
        dst_path = EN_DIR / cat

        if src_path.exists() and src_path.is_dir():
            count = len(list(src_path.glob("**/*.md*")))
            print(f"  • {cat}: {count} markdown files -> {dst_path.relative_to(ROOT_DIR)}")
            if not dry_run:
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                # Inject frontmatter metadata into all markdown files in dst_path
                for doc in dst_path.glob("**/*.md*"):
                    if doc.is_file():
                        try:
                            inject_locale_metadata(doc, locale="en")
                        except Exception as e:
                            print(f"Warning: Failed injecting metadata to {doc}: {e}")

    print("\nMigration ready. To apply for real, run: python3 scripts/migrate_to_locale_folders.py --apply")

if __name__ == "__main__":
    import sys
    dry = "--apply" not in sys.argv
    migrate_to_en(dry_run=dry)

