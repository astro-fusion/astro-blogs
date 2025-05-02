import os
import json
import argparse
from pathlib import Path

def generate_nav_links(folder_path_str):
    """
    Generates and appends previous/next navigation links to MD/MDX files
    in a folder based on the order specified in a _meta.json file.

    Args:
        folder_path_str (str): The path to the folder containing the files
                               and _meta.json.
    """
    folder_path = Path(folder_path_str)
    meta_file_path = folder_path / "_meta.json"
    base_folder_name = folder_path.name

    if not folder_path.is_dir():
        print(f"Error: Folder not found at '{folder_path_str}'")
        return

    if not meta_file_path.is_file():
        print(f"Error: '_meta.json' not found in '{folder_path_str}'")
        return

    try:
        with open(meta_file_path, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)

        # Assuming the list of files is the first value in the top-level dictionary
        if not meta_data or not isinstance(meta_data, dict):
             print(f"Error: Invalid format in '{meta_file_path}'. Expected a dictionary.")
             return

        file_list_key = next(iter(meta_data))
        files_info = meta_data[file_list_key]

        if not isinstance(files_info, list):
            print(f"Error: Invalid format in '{meta_file_path}'. Expected a list under the key '{file_list_key}'.")
            return

        # Sort files based on the 'order' key
        sorted_files = sorted(files_info, key=lambda x: x.get('order', float('inf')))
        num_files = len(sorted_files)

        if num_files == 0:
            print("No files found in the '_meta.json' list.")
            return

        print(f"Processing {num_files} files in '{base_folder_name}'...")

        for i, current_item in enumerate(sorted_files):
            current_file_name = current_item.get('file')
            current_file_path = folder_path / current_file_name

            if not current_file_name or not current_file_path.is_file():
                print(f"Warning: Skipping invalid or missing file entry: {current_item}")
                continue

            # Determine previous and next items (circular)
            prev_idx = (i - 1 + num_files) % num_files
            next_idx = (i + 1) % num_files

            prev_item = sorted_files[prev_idx]
            next_item = sorted_files[next_idx]

            prev_title = prev_item.get('title', 'Previous')
            prev_file_name = prev_item.get('file')
            next_title = next_item.get('title', 'Next')
            next_file_name = next_item.get('file')

            if not prev_file_name or not next_file_name:
                 print(f"Warning: Missing file name for prev/next links for '{current_file_name}'. Skipping append.")
                 continue

            # Construct links
            prev_link = f"/blogs-md/{base_folder_name}/{prev_file_name}"
            next_link = f"/blogs-md/{base_folder_name}/{next_file_name}"

            # Construct Markdown snippet
            nav_snippet = f"""
---

## Previous Article
- [{prev_title}]({prev_link})

---

## Next Article
- [{next_title}]({next_link})

---
"""
            # Append to the file
            try:
                with open(current_file_path, 'a', encoding='utf-8') as f:
                    f.write(nav_snippet)
                print(f"Appended navigation links to '{current_file_name}'")
            except IOError as e:
                print(f"Error writing to file '{current_file_path}': {e}")

        print("Finished processing folder.")

    except json.JSONDecodeError as e:
        print(f"Error parsing '{meta_file_path}': {e}")
    except KeyError as e:
        print(f"Error: Missing expected key '{e}' in '_meta.json' entries.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Append Previous/Next article links to MD/MDX files based on _meta.json."
    )
    parser.add_argument(
        "folder_path",
        help="Path to the folder containing the MD/MDX files and _meta.json."
    )
    args = parser.parse_args()

    generate_nav_links(args.folder_path)