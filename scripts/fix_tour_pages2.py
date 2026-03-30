import os
import re

WORKDIR = r"F:\Study\Project SItes"

all_ids = [
    "19567.html", "19069.html", "19068.html", "19067.html", "19066.html",
    "19062.html", "19036.html", "19022.html", "19021.html", "19012.html",
    "18978.html", "18949.html", "18946.html", "18941.html", "18921.html",
    "18920.html", "18912.html", "18910.html", "18875.html", "13579.html",
    "11338.html", "10942.html"
]

def find_section_end(html, start):
    """Find </section> matching the <section> at start."""
    pos = start
    depth = 0
    while pos < len(html):
        open_pos = html.find('<section', pos)
        close_pos = html.find('</section>', pos)
        if close_pos == -1:
            return -1
        if open_pos != -1 and open_pos < close_pos:
            depth += 1
            pos = open_pos + 8
        else:
            if depth == 0:
                return close_pos
            depth -= 1
            pos = close_pos + 10
    return -1

def extract_content_body(html, content_start):
    """From a content-inner div, extract the inner cell-content body."""
    # Find the cell-content image-wrapper or cell-content
    cell_match = re.search(r'<div class="cell-content(?:\s+image-wrapper)?">', html[content_start:])
    if not cell_match:
        return None
    body_start = content_start + cell_match.end()
    
    # Count div depth to find matching close
    pos = body_start
    depth = 1  # we're inside one div already
    while pos < len(html) and depth > 0:
        open_pos = html.find('<div', pos)
        close_pos = html.find('</div>', pos)
        if close_pos == -1:
            break
        if open_pos != -1 and open_pos < close_pos:
            depth += 1
            pos = open_pos + 4
        else:
            depth -= 1
            if depth == 0:
                return html[body_start:close_pos]
            pos = close_pos + 6
    return None

def find_and_wrap(html, search_text, summary_text):
    """Find section containing search_text and wrap in dropdown."""
    # Check if already wrapped
    idx = html.find(search_text)
    if idx == -1:
        return html, False
    
    # Check if already in a tour-dropdown
    before = html[max(0, idx-500):idx]
    if 'tour-dropdown' in before:
        return html, False
    
    # Find containing section
    sec_start = html.rfind('<section', 0, idx)
    if sec_start == -1:
        return html, False
    
    sec_end = find_section_end(html, sec_start)
    if sec_end == -1:
        return html, False
    sec_end += 10  # len('</section>')
    
    section = html[sec_start:sec_end]
    
    # Get section tag
    sec_tag_match = re.match(r'<section[^>]*>', section)
    if not sec_tag_match:
        return html, False
    sec_tag = sec_tag_match.group(0)
    
    # Find section-bg and section-content opening
    bg_match = re.search(r'<div class="section-bg">\s*</div>', section)
    if not bg_match:
        return html, False
    
    # Find all content-inner divs in the section
    # We need the LAST content-inner that has the actual service/note content
    # (not the one with heading+buttons)
    
    content_inners = []
    search_from = 0
    while True:
        ci_match = re.search(r'<div class="content-inner">', section[search_from:])
        if not ci_match:
            break
        ci_start = search_from + ci_match.start()
        
        # Find where this content-inner closes
        pos = ci_start + ci_match.end()
        depth = 1
        ci_end = -1
        while pos < len(section) and depth > 0:
            op = section.find('<div', pos)
            cp = section.find('</div>', pos)
            if cp == -1:
                break
            if op != -1 and op < cp:
                depth += 1
                pos = op + 4
            else:
                depth -= 1
                if depth == 0:
                    ci_end = cp + 6
                pos = cp + 6
        
        if ci_end != -1:
            content_inners.append((ci_start, ci_end))
        search_from = ci_start + ci_match.end()
    
    if len(content_inners) < 1:
        return html, False
    
    # The last content-inner usually has the actual content
    # But we need to find the one that contains our search text
    target_ci = None
    for ci_start, ci_end in content_inners:
        if search_text in section[ci_start:ci_end]:
            target_ci = (ci_start, ci_end)
            break
    
    if not target_ci:
        # Try finding the content-inner that's AFTER the heading
        # Use the last one
        target_ci = content_inners[-1]
    
    ci_start, ci_end = target_ci
    
    # Extract the cell-content from this content-inner
    inner = section[ci_start:ci_end]
    cell_match = re.search(r'<div class="cell-content(?:\s+image-wrapper)?">', inner)
    if not cell_match:
        return html, False
    
    cell_content_start = cell_match.end()
    
    # Find matching </div> for the cell-content div
    pos = cell_content_start
    depth = 1
    cell_end = -1
    while pos < len(inner) and depth > 0:
        op = inner.find('<div', pos)
        cp = inner.find('</div>', pos)
        if cp == -1:
            break
        if op != -1 and op < cp:
            depth += 1
            pos = op + 4
        else:
            depth -= 1
            if depth == 0:
                cell_end = cp
            pos = cp + 6
    
    if cell_end == -1:
        return html, False
    
    body = inner[cell_content_start:cell_end]
    
    # Build new section
    new_section = f'''{sec_tag}
<div class="section-bg">
</div>
<div class="section-content">
<div class="content-grid">
<div class="grid-column grid-stretch">
<div class="column-inner">
<details class="tour-dropdown">
<summary>{summary_text}</summary>
<div class="dropdown-body">
{body}
</div>
</details>
</div>
</div>
</div>
</div>
</section>'''
    
    html = html[:sec_start] + new_section + html[sec_end:]
    return html, True


def process_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        html = f.read()
    
    original = html
    
    # Remove iframe sections
    # Pattern: section containing class="pxjVId" (empty iframe)
    pattern = r'<section[^>]*class="section-content-block"[^>]*>\s*<div class="section-bg">\s*</div>\s*<div class="section-content">\s*<div class="content-grid">.*?</section>'
    
    def iframe_check(m):
        if 'pxjVId' in m.group(0) or 'WIdY2d M1aSXe' in m.group(0):
            return ''
        return m.group(0)
    
    html = re.sub(pattern, iframe_check, html, flags=re.DOTALL)
    
    # Wrap "Dịch vụ bao gồm"
    # Try different text patterns
    dv_found = False
    for txt in ['Dịch vụ bao gồm và không bao gồm', 'Dịch vụ bao gồm và không bao gồm(xem thêm)']:
        html, changed = find_and_wrap(html, txt, 'Dịch vụ bao gồm và không bao gồm')
        if changed:
            dv_found = True
            break
    
    if not dv_found:
        # Try partial match
        html, changed = find_and_wrap(html, 'Dịch vụ bao gồm', 'Dịch vụ bao gồm và không bao gồm')
        if changed:
            dv_found = True
    
    # Wrap "Ghi chú"
    gc_found = False
    for txt in ['Ghi chú (xem thêm)', 'Ghi chú(xem thêm)', 'Ghi chú']:
        html, changed = find_and_wrap(html, txt, 'Ghi chú')
        if changed:
            gc_found = True
            break
    
    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"OK: {filename} (dv={dv_found}, gc={gc_found})")
    else:
        print(f"SKIP: {filename}")
    
    return dv_found, gc_found

dv_total = 0
gc_total = 0
for fname in all_ids:
    filepath = os.path.join(WORKDIR, fname)
    if os.path.exists(filepath):
        dv, gc = process_file(filepath)
        if dv: dv_total += 1
        if gc: gc_total += 1

print(f"\nTotal: dv={dv_total}, gc={gc_total}")
