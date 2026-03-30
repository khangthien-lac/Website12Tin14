#!/usr/bin/env python3
# Batch updater for tour detail pages
# Usage: python scripts/batch_update_tours.py <path-to-batch-csv>

import os
import sys
import re

WORKDIR = r"F:\Study\Project SItes"
ROOT = WORKDIR

def find_section_bounds(html: str, header: str) -> (int, int):
    # naive approach: find the first occurrence of header text and locate enclosing section
    idx = html.find(header)
    if idx == -1:
        return -1, -1
    sec_start = html.rfind('<section', 0, idx)
    if sec_start == -1:
        return -1, -1
    # find matching closing </section> for this start
    depth = 0
    i = sec_start
    end = -1
    while i < len(html):
        if html.startswith('<section', i):
            depth += 1
            i += 8
        elif html.startswith('</section>', i):
            depth -= 1
            i += 10
            if depth == 0:
                end = i
                break
        else:
            i += 1
    return sec_start, end

def replace_section_content(html: str, header_text: str, new_body_html: str) -> str:
    s, e = find_section_bounds(html, header_text)
    if s == -1 or e == -1:
        return html
    # Build a minimal replacement preserving the outer <section> tags but replacing inner content where possible
    # We'll replace everything between the first occurrence of 
    # '<div class="section-content">' up to the icon close of the section.
    inner_start = html.find('<div class="section-content">', s, e)
    inner_end = html.rfind('</div>', s, e)
    if inner_start == -1 or inner_end == -1:
        new_section = html[s:e]
        # fallback: replace whole section
        new_section = re.sub(r'<section[^>]*>.*?</section>', new_body_html, html[s:e], flags=re.S)
        return html[:s] + new_body_html + html[e:]
    # Replace inner content only
    pre = html[:inner_start]
    post = html[e:]
    return pre + new_body_html + post

def main(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]

    # Expect header: id|hl|incl|excl|notes
    header = lines[0] if lines else ''
    if 'id' not in header and '|' not in header:
        # proceed anyway
        pass
    for line in lines[1:]:
        parts = line.split('|')
        if len(parts) < 5:
            print(f"Skipping invalid line: {line}")
            continue
        tour_id, hl, incl, excl, notes = [p.strip() for p in parts[:5]]
        if not tour_id:
            continue
        file_path = os.path.join(ROOT, f"{tour_id}.html")
        if not os.path.exists(file_path):
            print(f"Tour file not found: {file_path}")
            continue
        with open(file_path, 'r', encoding='utf-8') as fh:
            html = fh.read()

        # Prepare new bodies: wrap each text as a single paragraph
        def make_para(t):
            t = (t or '').strip()
            if not t:
                return ''
            return f'<p dir="ltr" class="text-paragraph" style="line-height: 1.38; margin-bottom: 0.0pt; padding: 0.0pt;">' 
                   f'<span class="text-span" style="color: #333333; font-size: 10.5pt; vertical-align: baseline;">{t}</span>'
                   '</p>\n'

        hl_html = make_para(hl)
        incl_html = make_para(incl)
        excl_html = make_para(excl)
        notes_html = make_para(notes)

        # Build replacement blocks for three sections
        dv_block = ''
        if incl_html or excl_html:
            dv_block = '<details class="tour-dropdown">\n<summary>Dịch vụ bao gồm và không bao gồm</summary>\n<div class="dropdown-body">\n'
            if incl_html:
                dv_block += incl_html
            if excl_html:
                dv_block += excl_html
            dv_block += '</div>\n</details>'

        # Headings to identify: Điểm nhấn hành trình block - replace inner with hl_html only
        # For simplicity, replace the entire 'Điểm nhấn hành trình' text content by hl_html.
        new_hl = f''
        if hl_html:
            new_hl = hl_html
        # Replace sections sequentially
        # Replace Điểm nhấn hành trình content if found
        header_hl = 'Điểm nhấn hành trình'
        html2 = html
        if header_hl in html2 and hl_html:
            html2 = replace_section_content(html2, header_hl, hl_html)
        # Replace Dịch vụ block if exists
        if dv_block and ('Dịch vụ bao gồm' in html2 or 'Dịch vụ không bao gồm' in html2):
            html2 = replace_section_content(html2, 'Dịch vụ bao gồm và không bao gồm', dv_block)
        # Replace Ghi chú block (three paragraphs)
        if notes_html:
            html2 = replace_section_content(html2, 'Ghi chú', notes_html)

        with open(file_path, 'w', encoding='utf-8') as fw:
            fw.write(html2)
        print(f"Updated: {tour_id}.html")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/batch_update_tours.py path/to/batch_updates.csv")
        sys.exit(1)
    main(sys.argv[1])
