import os
import re
import yaml

def clean_yaml_text_pre_parse(text):
    lines = text.split('\n')
    fixed_lines = []
    for line in lines:
        # If line contains unescaped single quote inside single quoted string
        if re.search(r":\s*'.*?\\'.*?'", line):
            # Convert to double quotes and replace \' with '
            line = re.sub(r":\s*'(.*)'\s*$", lambda m: ': "' + m.group(1).replace("\\'", "'").replace('"', '\\"') + '"', line)
        elif "\\'" in line:
            line = line.replace("\\'", "'")
            
        # Quote unquoted colons
        m = re.match(r'^([a-zA-Z0-9_-]+)\s*:\s*([^"\'|>].*)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if ':' in val:
                line = f'{key}: "{val.replace(chr(34), chr(92)+chr(34))}"'
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not fm_match:
        return False
        
    fm_text = fm_match.group(1)
    body = content[fm_match.end():]
    
    # Check if there are duplicate keys
    keys = []
    for line in fm_text.split('\n'):
        m = re.match(r'^([a-zA-Z0-9_-]+)\s*:', line)
        if m:
            keys.append(m.group(1))
    has_duplicates = len(keys) != len(set(keys))
    
    needs_fix = False
    parsed_data = None
    
    # Try parsing original
    try:
        parsed_data = yaml.safe_load(fm_text)
        if has_duplicates:
            needs_fix = True
    except Exception:
        needs_fix = True
        
    if not needs_fix:
        return False
        
    # If original failed or had duplicates, try cleaning pre-parse and then parse
    if parsed_data is None:
        cleaned_text = clean_yaml_text_pre_parse(fm_text)
        try:
            parsed_data = yaml.safe_load(cleaned_text)
        except Exception as e:
            print(f"Could not parse frontmatter in {file_path} even after cleaning: {e}")
            return False
            
    # Now we have parsed_data. Dump it cleanly!
    try:
        # Use safe_dump to generate perfect YAML
        fixed_fm = yaml.safe_dump(parsed_data, default_flow_style=False, sort_keys=False, allow_unicode=True).strip()
        new_content = f"---\n{fixed_fm}\n---\n{body}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully fixed and regenerated frontmatter in {file_path}")
        return True
    except Exception as e:
        print(f"Failed to dump frontmatter in {file_path}: {e}")
        return False

def main():
    modified_count = 0
    for root, _, files in os.walk('.'):
        if 'node_modules' in root or '.git' in root or 'temp_categories' in root:
            continue
        for file in files:
            if file.endswith('.mdx'):
                file_path = os.path.join(root, file)
                if process_file(file_path):
                    modified_count += 1
    print(f"\nCompleted. Fixed {modified_count} files.")

if __name__ == '__main__':
    main()
