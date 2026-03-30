# -*- coding: utf-8 -*-
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

WORKDIR = r"F:\Study\Project SItes"

all_ids = [
    "19567", "19069", "19068", "19067", "19066",
    "19062", "19036", "19022", "19021", "19012",
    "18978", "18949", "18946", "18941", "18921",
    "18920", "18912", "18910", "18875", "13579",
    "11338", "10942"
]

# Use unicode escapes to avoid encoding issues
DV_TEXT = 'D\u1ecbch v\u1ee5 bao g\u1ed3m'
DV_FULL = 'D\u1ecbch v\u1ee5 bao g\u1ed3m v\u00e0 kh\u00f4ng bao g\u1ed3m'
DV_FULL_ALT = 'D\u1ecbch v\u1ee5 bao g\u1ed3m v\u00e0 kh\u00f4ng bao g\u1ed3m(xem th\u00eam)'
GC_TEXT1 = 'Ghi ch\u00fa (xem th\u00eam)'
GC_TEXT2 = 'Ghi ch\u00fa(xem th\u00eam)'
GC_TEXT3 = 'Ghi ch\u00fa'
SUMMARY_DV = 'D\u1ecbch v\u1ee5 bao g\u1ed3m v\u00e0 kh\u00f4ng bao g\u1ed3m'
SUMMARY_GC = 'Ghi ch\u00fa'

def find_matching_close_section(html, start):
    depth = 0
    pos = start + 8  # skip past opening <section tag
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
    idx = html.find(text)
    if idx == -1:
        return -1, -1
    sec_start = html.rfind('<section', 0, idx)
    if sec_start == -1:
        return -1, -1
    sec_end = find_matching_close_section(html, sec_start)
    if sec_end == -1:
        return -1, -1
    return sec_start, sec_end + 10

def extract_body(html, section_start, section_end):
    section = html[section_start:section_end]
    tag_match = re.match(r'<section[^>]*>', section)
    if not tag_match:
        return None, None
    sec_tag = tag_match.group(0)
    
    # Find all content-inner blocks
    ci_pattern = '<div class="content-inner">'
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
    
    # Use last content-inner (has actual content, not heading+buttons)
    last_ci_start = positions[-1]
    search_start = last_ci_start + len(ci_pattern)
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
    
    # Extract cell-content inner
    cell_match = re.search(r'<div class="cell-content(?:\s+image-wrapper)?">\s*', ci_content)
    if not cell_match:
        return sec_tag, ci_content
    
    body_start = cell_match.end()
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
    for text in search_texts:
        sec_start, sec_end = find_section_by_content(html, text)
        if sec_start == -1:
            continue
        
        section = html[sec_start:sec_end]
        if 'tour-dropdown' in section:
            return html, False
        
        sec_tag, body = extract_body(html, sec_start, sec_end)
        if sec_tag is None or body is None:
            continue
        
        new_section = (
            f'{sec_tag}\n'
            '<div class="section-bg">\n</div>\n'
            '<div class="section-content">\n'
            '<div class="content-grid">\n'
            '<div class="grid-column grid-stretch">\n'
            '<div class="column-inner">\n'
            '<details class="tour-dropdown">\n'
            f'<summary>{summary_text}</summary>\n'
            '<div class="dropdown-body">\n'
            f'{body}\n'
            '</div>\n'
            '</details>\n'
            '</div>\n</div>\n</div>\n</div>\n'
            '</section>'
        )
        
        html = html[:sec_start] + new_section + html[sec_end:]
        return html, True
    
    return html, False

def process_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        html = f.read()
    
    original = html
    
    # Remove iframe sections
    pattern = r'<section[^>]*class="section-content-block"[^>]*>\s*<div class="section-bg">\s*</div>\s*<div class="section-content">\s*<div class="content-grid">.*?</section>'
    def check(m):
        if 'pxjVId' in m.group(0) or 'WIdY2d M1aSXe' in m.group(0):
            return ''
        return m.group(0)
    html = re.sub(pattern, check, html, flags=re.DOTALL)
    
    # Wrap DV
    html, dv = wrap_dropdown(html, [DV_FULL, DV_FULL_ALT, DV_TEXT], SUMMARY_DV)
    
    # Wrap GC
    html, gc = wrap_dropdown(html, [GC_TEXT1, GC_TEXT2, GC_TEXT3], SUMMARY_GC)
    
    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"OK: {filename} dv={dv} gc={gc}")
    else:
        print(f"SKIP: {filename} dv={dv} gc={gc}")

for fid in all_ids:
    fp = os.path.join(WORKDIR, fid + '.html')
    if os.path.exists(fp):
        process_file(fp)
