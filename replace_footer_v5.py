import os
import re
import sys

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        # Try to encode and replace unsupported characters
        try:
            encoded = msg.encode('cp1252', errors='replace')
            print(encoded.decode('cp1252'))
        except:
            print("[Message contains unsupported characters]")

def replace_footer(file_path, new_footer):
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    
    # Try to find the footer tag first
    footer_start = content.find('<footer>')
    if footer_start == -1:
        # Try with attributes
        footer_start = content.find('<footer ')
    
    if footer_start != -1:
        # Found footer tag, find the closing tag
        footer_end = content.find('</footer>', footer_start)
        if footer_end == -1:
            safe_print(f"No closing footer tag found in {os.path.basename(file_path)}")
            return False
        
        # Add the length of the closing tag
        footer_end += len('</footer>')
        
        # Replace the footer
        new_content = content[:footer_start] + new_footer + content[footer_end:]
        safe_print(f"Replaced existing footer in {os.path.basename(file_path)}")
    else:
        # No footer found, try to insert before </body>
        body_end = content.find('</body>')
        if body_end != -1:
            # Insert footer before </body>
            new_content = content[:body_end] + new_footer + content[body_end:]
            safe_print(f"Inserted footer before </body> in {os.path.basename(file_path)}")
        else:
            # No </body> found, append to end
            new_content = content + new_footer
            safe_print(f"Appended footer to end of {os.path.basename(file_path)}")
    
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
    failed_files = []
    for file_path in html_files:
        filename = os.path.basename(file_path)
        if filename.lower() == 'index.html':
            safe_print(f"Skipping {filename}")
            skipped += 1
            continue
        
        safe_print(f"Processing {filename}")
        if replace_footer(file_path, new_footer):
            processed += 1
        else:
            failed += 1
            failed_files.append(filename)
            safe_print(f"Failed to process {filename}")
    
    safe_print(f"\nProcessed: {processed} files")
    safe_print(f"Skipped: {skipped} files")
    safe_print(f"Failed: {failed} files")
    if failed > 0:
        safe_print("Failed files:")
        for f in failed_files:
            safe_print(f"  {f}")

if __name__ == "__main__":
    main()