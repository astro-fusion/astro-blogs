import json
import os

def split_json():
    with open('raw-index-structure.json', 'r') as f:
        data = json.load(f)
    
    os.makedirs('temp_categories', exist_ok=True)
    for category in data:
        name = category['category'].replace(' ', '_')
        with open(f'temp_categories/{name}.json', 'w') as f:
            json.dump(category, f, indent=2)

if __name__ == "__main__":
    split_json()
