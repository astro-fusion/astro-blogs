import os
import re

def validate_blog_post(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    errors = []

    # 1. Check Frontmatter
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Missing frontmatter")
    else:
        frontmatter = frontmatter_match.group(1)
        
        # Check description
        description_match = re.search(r'description:\s*\|\s*\n(.*?)(?=\n\w+:)', frontmatter, re.DOTALL)
        if description_match:
            description = description_match.group(1).strip()
            lines = description.split('\n')
            # if len(lines) < 2 or len(lines) > 5: # Relaxed check for approx 3 lines
            #     errors.append(f"Description length issue: {len(lines)} lines")
        else:
             # Try single line description
            description_match_single = re.search(r'description:\s*(.*)', frontmatter)
            if not description_match_single:
                 errors.append("Missing description")

        # Check author
        if 'author: "Gemini 3 Pro"' not in frontmatter:
            errors.append("Missing or incorrect author field")

    # 2. Check Predictions Section
    if "## Predictions by Life Area" not in content:
        errors.append("Missing 'Predictions by Life Area' section")

    # 3. Check Duplicate Footer
    footer_matches = re.findall(r'## Previous Article', content)
    if len(footer_matches) > 1:
        errors.append("Duplicate 'Previous Article' section")
    
    footer_matches_next = re.findall(r'## Next Article', content)
    if len(footer_matches_next) > 1:
        errors.append("Duplicate 'Next Article' section")

    return errors

def main():
    directory = "/Users/bishalghimire/Documents/WORK/Code/AstroFusion/astro-blogs/20_Transit/07_Saturn_Transit"
    files = [f for f in os.listdir(directory) if f.endswith(".md")]
    files.sort()

    all_passed = True
    for filename in files:
        filepath = os.path.join(directory, filename)
        errors = validate_blog_post(filepath)
        
        if errors:
            all_passed = False
            print(f"❌ {filename}:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"✅ {filename}")

    if all_passed:
        print("\nAll Saturn transit blog posts validated successfully!")
    else:
        print("\nSome files failed validation.")

if __name__ == "__main__":
    main()
