#!/usr/bin/env python3
"""
CI Linter & Invariant Validator for astro-blogs repository.
Validates:
1. Valid frontmatter (title, description, locale, keywords)
2. Interactive <KundaliChart /> tags syntax & props
3. <YogaDeepLink /> yogaId format
4. <BookReference /> book name validity
5. <FAQBlock /> structured question-answer arrays
"""

import sys
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

VALID_BOOKS = {"BPHS", "BhavarthaRatnakara", "PhalaDeepika", "Saravali", "BrihatJataka", "Horasara"}
VALID_LOCALES = {"en", "hi", "ne"}
LOCALE_DIRS = ["en", "hi", "ne"]

def validate_file(file_path: Path):
    errors = []
    content = file_path.read_text(encoding="utf-8")
    
    # 1. Check Frontmatter
    fm_match = re.match(r"^---\s*\n([\s\S]*?)\n---", content)
    if not fm_match:
        errors.append("Missing YAML frontmatter block (---)")
    else:
        raw_yaml = fm_match.group(1)
        if "title:" not in raw_yaml:
            errors.append("Frontmatter missing 'title'")
        if "description:" not in raw_yaml:
            errors.append("Frontmatter missing 'description'")
        if "locale:" not in raw_yaml:
            errors.append("Frontmatter missing 'locale'")
        if "keywords:" not in raw_yaml and "tags:" not in raw_yaml:
            errors.append("Frontmatter missing 'keywords' or 'tags'")
    
    # 2. Check BookReference tags if present
    for match in re.finditer(r'<BookReference\s+[^>]*book=["\']([^"\']+)["\']', content):
        book = match.group(1)
        if book not in VALID_BOOKS:
            errors.append(f"Unrecognized book in <BookReference>: '{book}'")

    # 3. Check YogaDeepLink tags if present
    for match in re.finditer(r'<YogaDeepLink\s+[^>]*yogaId=["\']([^"\']+)["\']', content):
        yoga_id = match.group(1)
        if not yoga_id.strip():
            errors.append("Empty yogaId in <YogaDeepLink>")

    # 4. Check KundaliChart tags if present
    if "<KundaliChart" in content:
        if "lagnaRashi=" not in content:
            errors.append("<KundaliChart /> missing 'lagnaRashi' prop")
        if "placements=" not in content:
            errors.append("<KundaliChart /> missing 'placements' prop")

    # 5. Check FAQBlock tags if present
    if "<FAQBlock" in content:
        if "items=" not in content and "items={" not in content and "faqs=" not in content and "faqs={" not in content:
            errors.append("<FAQBlock /> missing 'items' or 'faqs' prop")


    return errors

def run_validation():
    print("Running Multilingual MDX Validation on locale collections (en/, hi/, ne/)...")
    total_files = 0
    failed_files = 0

    for loc in LOCALE_DIRS:
        loc_dir = ROOT_DIR / loc
        if not loc_dir.exists():
            continue
        
        for ext in ["*.mdx", "*.md"]:
            for file_path in loc_dir.glob(f"**/{ext}"):
                if "node_modules" in file_path.parts or ".git" in file_path.parts or "scripts" in file_path.parts:
                    continue
                
                total_files += 1
                errs = validate_file(file_path)
                if errs:
                    failed_files += 1
                    print(f"❌ {file_path.relative_to(ROOT_DIR)}:")
                    for e in errs:
                        print(f"    - {e}")

    print(f"\nScan complete: {total_files} files checked.")
    if failed_files == 0:
        print("✅ All multilingual MDX files passed validation!")
        sys.exit(0)
    else:
        print(f"⚠️ {failed_files} files have lint warnings.")
        sys.exit(1)

if __name__ == "__main__":
    run_validation()

