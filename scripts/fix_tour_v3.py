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

def find_matching_close_section(html, start):
    """Find the </section> that matches the <section> at position start."""
    depth = 0
    pos = start
    while True:
        next_open = html.find('<section', pos)
        next_close = html.find('</section>', pos)
        if next_close == -1:
            return -1
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 8
        else:
            depth -= 1
            if depth < 0:
                return next_close
            pos = next_close + 10

def find_section_by_content(html, text):
    """Find the <section> tag that contains the given text."""
    idx = html.find(text)
    if idx == -1:
        return -1, -1
    # Walk backwards to find <section
    sec_start = html.rfind('<section', 0, idx)
    if sec_start == -1:
        return -1, -1
    sec_end = find_matching_close_section(html, sec_start)
    if sec_end == -1:
        return -1, -1
    return sec_start, sec_end + 10  # +10 for len('</section>')

def extract_body(html, section_start, section_end):
    """Extract the content body from a section-content-block section."""
    section = html[section_start:section_end]
    
    # Get section tag
    tag_match = re.match(r'<section[^>]*>', section)
    if not tag_match:
        return None, None
    sec_tag = tag_match.group(0)
    
    # Find all content-inner blocks
    ci_pattern = r'<div class="content-inner">'
    positions = []
    pos = 0
    while True:
        m = re.search(ci_pattern, section[pos:])
        if not m:
            break
        abs_pos = pos + m.start()
        positions.append(abs_pos)
        pos = abs_pos + len(m.group())
    
    if not positions:
        return None, None
    
    # Find the LAST content-inner that contains our target content
    # (not the one with heading+buttons)
    last_ci_start = positions[-1]
    
    # Find where this content-inner closes (div depth counting)
    search_start = last_ci_start + len('<div class="content-inner">')
    depth = 1
    p = search_start
    ci_end = -1
    while p < len(section) and depth > 0:
        o = section.find('<div', p)
        c = section.find('</div>', p)
        if c == -1:
            break
        if o != -1 and o < c:
            depth += 1
            p = o + 4
        else:
            depth -= 1
            if depth == 0:
                ci_end = c
            p = c + 6
    
    if ci_end == -1:
        return None, None
    
    ci_content = section[search_start:ci_end]
    
    # Extract just the cell-content inner
    cell_match = re.search(r'<div class="cell-content(?:\s+image-wrapper)?">\s*', ci_content)
    if not cell_match:
        # Try without the outer wrapper
        return sec_tag, ci_content
    
    body_start = cell_match.end()
    
    # Find matching close for cell-content
    depth = 1
    p = body_start
    cell_end = -1
    while p < len(ci_content) and depth > 0:
        o = ci_content.find('<div', p)
        c = ci_content.find('</div>', p)
        if c == -1:
            break
        if o != -1 and o < c:
            depth += 1
            p = o + 4
        else:
            depth -= 1
            if depth == 0:
                cell_end = c
            p = c + 6
    
    if cell_end != -1:
        body = ci_content[body_start:cell_end]
    else:
        body = ci_content[body_start:]
    
    return sec_tag, body

def wrap_dropdown(html, search_texts, summary_text):
    """Find section containing one of search_texts and wrap in dropdown."""
    for text in search_texts:
        sec_start, sec_end = find_section_by_content(html, text)
        if sec_start == -1:
            continue
        
        section = html[sec_start:sec_end]
        
        # Skip if already has tour-dropdown
        if 'tour-dropdown' in section:
            return html, False
        
        sec_tag, body = extract_body(html, sec_start, sec_end)
        if sec_tag is None or body is None:
            continue
        
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
    
    return html, False

def process_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        html = f.read()
    
    original = html
    
    # Remove iframe sections
    def remove_iframe_sections(h):
        pattern = r'<section[^>]*class="section-content-block"[^>]*>\s*<div class="section-bg">\s*</div>\s*<div class="section-content">\s*<div class="content-grid">.*?</section>'
        def check(m):
            if 'pxjVId' in m.group(0) or 'WIdY2d M1aSXe' in m.group(0):
                return ''
            return m.group(0)
        return re.sub(pattern, check, h, flags=re.DOTALL)
    
    html = remove_iframe_sections(html)
    
    # Wrap "Dịch vụ bao gồm"
    html, dv = wrap_dropdown(html, [
        'Dịch vụ bao gồm và không bao gồm',
        'Dịch vụ bao gồm và không bao gồm(xem thêm)'
    ], 'Dịch vụ bao gồm và không bao gồm')
    
    # Wrap "Ghi chú"
    html, gc = wrap_dropdown(html, [
        'Ghi chú (xem thêm)',
        'Ghi chú(xem thêm)',
        'Ghi chú'
    ], 'Ghi chú')
    
    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"OK: {filename} dv={dv} gc={gc}")
    else:
        print(f"SKIP: {filename} dv={dv} gc={gc}")

for fname in all_ids:
    fp = os.path.join(WORKDIR, fname)
    if os.path.exists(fp):
        process_file(fp)
