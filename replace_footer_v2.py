import os
import re
import sys

def replace_footer(file_path, new_footer):
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    
    # Find the footer tag
    footer_start = content.find('<footer>')
    if footer_start == -1:
        # Try with attributes
        footer_start = content.find('<footer ')
        if footer_start == -1:
            print(f"No footer tag found in {file_path}")
            return False
    
    # Find the closing footer tag
    footer_end = content.find('</footer>', footer_start)
    if footer_end == -1:
        print(f"No closing footer tag found in {file_path}")
        return False
    
    # Add the length of the closing tag
    footer_end += len('</footer>')
    
    # Replace the footer
    new_content = content[:footer_start] + new_footer + content[footer_end:]
    
    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except UnicodeEncodeError:
        # Try with UTF-8 with BOM if needed
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
    
    return True

def main():
    # Read the new footer content
    try:
        with open('F:\\Study\\Project SItes\\new_footer.html', 'r', encoding='utf-8') as f:
            new_footer = f.read()
    except UnicodeDecodeError:
        with open('F:\\Study\\Project SItes\\new_footer.html', 'r', encoding='utf-8-sig') as f:
            new_footer = f.read()
    
    # Get all HTML files
    html_files = []
    for root, dirs, files in os.walk('F:\\Study\\Project SItes'):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    # Process each file except index.html
    processed = 0
    skipped = 0
    failed = 0
    for file_path in html_files:
        if os.path.basename(file_path).lower() == 'index.html':
            print(f"Skipping {file_path}")
            skipped += 1
            continue
        
        print(f"Processing {file_path}")
        if replace_footer(file_path, new_footer):
            processed += 1
        else:
            failed += 1
            print(f"Failed to process {file_path}")
    
    print(f"\nProcessed: {processed} files")
    print(f"Skipped: {skipped} files")
    print(f"Failed: {failed} files")

if __name__ == "__main__":
    main()