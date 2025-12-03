import os
import re

def validate_rahu_blogs():
    directory = "/Users/bishalghimire/Documents/WORK/Code/AstroFusion/astro-blogs/20_Transit/08_Rahu_Transit"
    csv_path = os.path.join(directory, "rahu_transit_natal_moon.csv")
    
    # Read CSV content
    csv_descriptions = {}
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    house_num = parts[0].strip()
                    description = ",".join(parts[2:]).strip().strip('"')
                    csv_descriptions[house_num] = description
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return

    print(f"Found {len(csv_descriptions)} descriptions in CSV.")

    # Iterate through blog posts
    for filename in os.listdir(directory):
        if filename.endswith(".md") and "Rahu_transit" in filename:
            filepath = os.path.join(directory, filename)
            
            # Extract ID from filename (first 6 digits)
            file_id = filename[:6]
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            print(f"Validating {filename} (ID {file_id})...")
            
            # 1. Validate Description
            if file_id in csv_descriptions:
                expected_desc = csv_descriptions[file_id]
                # Normalize whitespace for comparison
                normalized_content = re.sub(r'\s+', ' ', content)
                normalized_desc = re.sub(r'\s+', ' ', expected_desc)
                
                if normalized_desc not in normalized_content:
                     # Check if description is in frontmatter (it might be wrapped or have different whitespace)
                    frontmatter_match = re.search(r'description:\s*\|?\s*(.*?)\n\w+:', content, re.DOTALL)
                    if frontmatter_match:
                        frontmatter_desc = frontmatter_match.group(1).strip()
                        normalized_frontmatter_desc = re.sub(r'\s+', ' ', frontmatter_desc)
                        if normalized_desc not in normalized_frontmatter_desc:
                             print(f"  [WARNING] Description might not match CSV.")
                             print(f"   Expected: {expected_desc[:50]}...")
                             print(f"   Found: {frontmatter_desc[:50]}...")
                    else:
                        print(f"  [WARNING] Could not find description in frontmatter.")

            else:
                print(f"  [WARNING] No CSV description found for ID {file_id}")

            # 2. Validate Author
            if 'author: "Gemini 3 Pro"' not in content:
                print(f"  [ERROR] Author field missing or incorrect.")
            
            # 3. Validate Footer (Check for duplicates)
            prev_article_count = content.count("## Previous Article")
            next_article_count = content.count("## Next Article")
            
            if prev_article_count > 1:
                print(f"  [ERROR] Duplicate 'Previous Article' section found ({prev_article_count} times).")
            if next_article_count > 1:
                print(f"  [ERROR] Duplicate 'Next Article' section found ({next_article_count} times).")

            # 4. Validate Predictions Section
            if "## Predictions by Life Area" not in content:
                print(f"  [ERROR] 'Predictions by Life Area' section missing.")
            else:
                # Check for at least one prediction subsection
                if "### Prediction:" not in content:
                     print(f"  [ERROR] No specific predictions found under 'Predictions by Life Area'.")

            print("  Validation complete.")

if __name__ == "__main__":
    validate_rahu_blogs()
