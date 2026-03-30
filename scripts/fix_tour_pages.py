import re
import os

WORKDIR = r"F:\Study\Project SItes"
# Files already done
DONE = {"19090.html", "19000.html", "19688.html"}

# All tour ID files
all_ids = [
    "19567.html", "19069.html", "19068.html", "19067.html", "19066.html",
    "19062.html", "19036.html", "19022.html", "19021.html", "19012.html",
    "18978.html", "18949.html", "18946.html", "18941.html", "18921.html",
    "18920.html", "18912.html", "18910.html", "18875.html", "13579.html",
    "11338.html", "10942.html"
]

def remove_iframe_sections(html):
    """Remove entire sections that contain only an empty iframe (WIdY2d M1aSXe pattern)."""
    # Pattern: <section ...>...WIdY2d M1aSXe...<iframe...>...</section>
    # These sections have the iframe placeholder with padding-top creating big blank boxes
    pattern = r'<section[^>]*class="section-content-block"[^>]*>\s*<div class="section-bg">\s*</div>\s*<div class="section-content">\s*<div class="content-grid">\s*<div class="hJDwNd-AhqUyc-qWD73c[^"]*"[^>]*>.*?</section>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    
    # Also try with other grid classes
    pattern2 = r'<section[^>]*class="section-content-block"[^>]*>\s*<div class="section-bg">\s*</div>\s*<div class="section-content">\s*<div class="content-grid">.*?class="pxjVId".*?</section>'
    html = re.sub(pattern2, '', html, flags=re.DOTALL)
    
    return html

def wrap_section_in_dropdown(html, heading_text, summary_text):
    """Find a section containing heading_text and wrap its content in a details dropdown."""
    
    # Find the heading h2 containing the text
    # Pattern: look for the h2 heading and the toggle buttons, then wrap
    
    # Strategy: Find the section that contains the heading text
    # Then replace the complex inner structure with a simple dropdown
    
    # Find heading with exact text (case insensitive, flexible whitespace)
    heading_pattern = re.escape(heading_text)
    
    # Find position of heading in html
    match = re.search(heading_pattern, html)
    if not match:
        return html, False
    
    # Find the section containing this heading
    # Go backwards to find <section
    section_start = html.rfind('<section', 0, match.start())
    if section_start == -1:
        return html, False
    
    # Find the closing </section>
    section_end = html.find('</section>', match.end())
    if section_end == -1:
        return html, False
    section_end += len('</section>')
    
    section_html = html[section_start:section_end]
    
    # Check if already has tour-dropdown
    if 'tour-dropdown' in section_html:
        return html, False
    
    # Find the section-content-block opening tag
    section_tag_match = re.search(r'<section[^>]*class="section-content-block"[^>]*>', section_html)
    if not section_tag_match:
        return html, False
    
    section_tag = section_tag_match.group(0)
    
    # Find the content-grid div and its first column div
    # Replace the complex column wrapper with simple grid-column grid-stretch
    # Find: <div class="hJDwNd-AhqUyc-... or <div class="grid-column ... >
    
    # Find the first column-inner after content-grid
    content_grid_match = re.search(r'<div class="content-grid">', section_html)
    if not content_grid_match:
        return html, False
    
    # Find the actual content: everything from the heading to the section closing
    # that has the service/note content
    
    # Extract inner content between heading and </section>
    heading_pos_in_section = section_html.find(heading_text)
    
    # Find the heading element start (go back to find the h2 or heading div)
    h2_start = section_html.rfind('<div id=', content_grid_match.end(), heading_pos_in_section)
    if h2_start == -1:
        h2_start = section_html.rfind('<h2', content_grid_match.end(), heading_pos_in_section)
    
    # Find the content block after heading (after toggle buttons)
    # Look for "cell-content image-wrapper" after the heading that contains the actual content
    # There are usually two content-inner blocks: one with heading+buttons, one with content
    
    # Find all content-inner divs
    content_inners = list(re.finditer(r'<div class="content-inner">', section_html))
    
    if len(content_inners) < 2:
        # Only one content-inner, try different approach
        # Find the cell-content image-wrapper that contains the actual content
        pass
    
    # Find the content that starts after the heading/buttons area
    # The actual content typically starts with "Giá tour bao gồm" or "Giá vé dành cho trẻ em"
    content_start_keywords = ['Giá tour bao gồm', 'Giá vé dành cho trẻ em', 'Không bao gồm']
    
    content_start = -1
    for kw in content_start_keywords:
        pos = section_html.find(kw)
        if pos != -1:
            # Go back to find the enclosing div
            content_start = section_html.rfind('<div class="cell-content image-wrapper">', 0, pos)
            if content_start == -1:
                content_start = section_html.rfind('<div class="cell-content">', 0, pos)
            break
    
    if content_start == -1:
        return html, False
    
    # Find the first content-inner that wraps the content
    content_wrapper_start = section_html.rfind('<div class="content-inner">', 0, content_start)
    if content_wrapper_start == -1:
        return html, False
    
    # The section structure is:
    # <section>
    #   <div class="section-bg"></div>
    #   <div class="section-content">
    #     <div class="content-grid">
    #       [complex column wrappers]
    #       <div class="content-inner"> [heading+buttons] </div>
    #       <div class="content-inner"> [actual content] </div>
    #     </div>
    #   </div>
    # </section>
    
    # Build new section
    # Everything before content-grid stays the same
    before_grid = section_html[:content_grid_match.start()]
    
    # Find the last </div> before </section> to get the closing structure
    # The content div (actual content) goes from content_wrapper_start to end
    
    # Find content-inner for the actual content
    # Content goes from content_wrapper_start to the end of content-grid
    content_grid_close = section_html.rfind('</div>\n</div>\n</div>\n</section>')
    if content_grid_close == -1:
        content_grid_close = section_html.rfind('</div>')
        # Try to find proper closing
        # Just take everything from content_start to section end minus closing divs
    
    # Simpler approach: extract the content block
    # Find the cell-content that wraps the service/note content
    content_cell_start = content_start
    
    # Find the end: look for the closing structure after the content
    # Count div nesting from content_wrapper_start
    remaining = section_html[content_wrapper_start:]
    
    # Find where the content-inner closes
    depth = 0
    pos = 0
    inner_end = -1
    while pos < len(remaining):
        open_tag = remaining.find('<div', pos)
        close_tag = remaining.find('</div>', pos)
        
        if open_tag == -1 and close_tag == -1:
            break
        
        if open_tag != -1 and (close_tag == -1 or open_tag < close_tag):
            depth += 1
            pos = open_tag + 4
        elif close_tag != -1:
            depth -= 1
            pos = close_tag + 6
            if depth == 0:
                inner_end = close_tag + 6
                break
    
    if inner_end == -1:
        return html, False
    
    actual_content = remaining[:inner_end]
    
    # Remove the outer content-inner wrapper to get just the cell-content
    # Find first > after <div class="content-inner">
    ci_match = re.search(r'<div class="content-inner">\s*', actual_content)
    if ci_match:
        content_body = actual_content[ci_match.end():]
        # Remove closing </div> at end
        content_body = content_body.rstrip()
        if content_body.endswith('</div>'):
            content_body = content_body[:-6].rstrip()
    else:
        content_body = actual_content
    
    # Build new section with dropdown
    new_section = f'''{section_tag}
<div class="section-bg">
</div>
<div class="section-content">
<div class="content-grid">
<div class="grid-column grid-stretch">
<div class="column-inner">
<details class="tour-dropdown">
<summary>{summary_text}</summary>
<div class="dropdown-body">
{content_body}
</div>
</details>
</div>
</div>
</div>
</div>
</section>'''
    
    html = html[:section_start] + new_section + html[section_end:]
    return html, True


def process_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        html = f.read()
    
    original = html
    
    # 1. Remove iframe sections
    html = remove_iframe_sections(html)
    
    # 2. Wrap "Dịch vụ bao gồm" in dropdown
    html, dv_changed = wrap_section_in_dropdown(html, 'Dịch vụ bao gồm', 'Dịch vụ bao gồm và không bao gồm')
    
    # 3. Wrap "Ghi chú" in dropdown  
    html, gc_changed = wrap_section_in_dropdown(html, 'Ghi chú', 'Ghi chú')
    
    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  OK: {filename} (dv={dv_changed}, gc={gc_changed})")
    else:
        print(f"  SKIP: {filename} (no changes)")
    
    return dv_changed, gc_changed


# Process all files
results = {"dv_ok": 0, "gc_ok": 0, "files": 0, "errors": []}
for fname in all_ids:
    filepath = os.path.join(WORKDIR, fname)
    if not os.path.exists(filepath):
        results["errors"].append(f"NOT FOUND: {fname}")
        continue
    try:
        dv, gc = process_file(filepath)
        results["files"] += 1
        if dv: results["dv_ok"] += 1
        if gc: results["gc_ok"] += 1
    except Exception as e:
        results["errors"].append(f"ERROR {fname}: {e}")

print(f"\nDone: {results['files']} files processed")
print(f"  Dịch vụ dropdown: {results['dv_ok']}")
print(f"  Ghi chú dropdown: {results['gc_ok']}")
if results["errors"]:
    print(f"  Errors: {results['errors']}")
