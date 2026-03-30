import os
import re
import sys

def replace_footer(file_path, new_footer):
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the last occurrence of <footer
    last_footer_start = content.rfind('<footer')
    if last_footer_start == -1:
        print(f"No footer tag found in {file_path}")
        return False
    
    # Find the closing </footer> tag after the last <footer
    # We need to handle nested tags properly
    footer_content = content[last_footer_start:]
    # Find the matching closing tag
    open_tags = 1
    pos = 0
    while pos < len(footer_content) and open_tags > 0:
        # Look for opening or closing footer tags
        open_match = re.search(r'<footer[^>]*>', footer_content[pos:], re.IGNORECASE)
        close_match = re.search(r'</footer[^>]*>', footer_content[pos:], re.IGNORECASE)
        
        # Determine which comes first
        if open_match and close_match:
            if open_match.start() < close_match.start():
                open_tags += 1
                pos += open_match.end()
            else:
                open_tags -= 1
                pos += close_match.end()
        elif open_match:
            open_tags += 1
            pos += open_match.end()
        elif close_match:
            open_tags -= 1
            pos += close_match.end()
        else:
            break
    
    if open_tags != 0:
        print(f"Could not find matching closing footer tag in {file_path}")
        return False
    
    # Calculate the end position
    footer_end = last_footer_start + pos
    
    # Replace the footer
    new_content = content[:last_footer_start] + new_footer + content[footer_end:]
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    # Read the new footer content
    with open('F:\\Study\\Project SItes\\new_footer.html', 'r', encoding='utf-8') as f:
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
    for file_path in html_files:
        if os.path.basename(file_path).lower() == 'index.html':
            print(f"Skipping {file_path}")
            skipped += 1
            continue
        
        print(f"Processing {file_path}")
        if replace_footer(file_path, new_footer):
            processed += 1
        else:
            print(f"Failed to process {file_path}")
    
    print(f"\nProcessed: {processed} files")
    print(f"Skipped: {skipped} files")

if __name__ == "__main__":
    main()