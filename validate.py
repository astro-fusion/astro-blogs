#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

def load_meta(meta_path):
    """Load and parse the _meta.json file"""
    try:
        with open(meta_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading _meta.json: {str(e)}")
        sys.exit(1)

def validate_structure(entry, base_dir, errors):
    """Recursively validate all entries in the meta structure"""
    if "children" in entry:  # This is a folder
        for child in entry["children"]:
            validate_structure(child, base_dir, errors)
    else:  # This is a file entry
        full_path = base_dir / entry["path"]
        if not full_path.exists():
            errors.append(f"Missing file: {entry['path']} (referenced in {entry.get('title', 'unknown')})")

def main():
    base_dir = Path(__file__).parent
    meta_path = base_dir / "_meta.json"
    
    print(f"🔍 Validating structure in {base_dir}")
    
    meta_data = load_meta(meta_path)
    errors = []
    
    # Validate all categories and subcategories
    for category in meta_data.get("Vedic Astrology", []):
        validate_structure(category, base_dir, errors)
    
    # Print results with color coding
    if errors:
        print("\n❌ Validation errors:")
        for error in errors:
            print(f"  \033[91m{error}\033[0m")
        print(f"\nFound {len(errors)} errors in meta structure")
        sys.exit(1)
    else:
        print("\n\033[92m✅ All files validated successfully!\033[0m")
        print("Checked all entries in:")
        print(f" - {len(meta_data.get('Vedic Astrology', []))} main categories")
        sys.exit(0)

if __name__ == "__main__":
    main()
