#!/usr/bin/env python3
"""
Offline batch updater for tour HTML files.
Input: CSV/TSV with columns: id, hl_text, incl_text, excl_text, notes_text
Format can be separated by comma or pipe (|).
This is a lightweight, safe temporary tool that appends new sections to end of each HTML file
before the closing </body> tag. It is intended for quick data entry and can operate in dry-run mode.
"""
import csv
import io
import os
import sys

ROOT = r"F:\Study\Project SItes"

def to_section_hl(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    return (
        '<section class="section-content-block">\n'
        '<div class="section-content">\n'
        '<div class="content-grid">\n'
        '<div class="grid-column grid-stretch">\n'
        '<div class="column-inner">\n'
        '<div class="content-inner">\n'
        f'<p dir="ltr" class="text-paragraph" style="line-height: 1.38;">'
        f'<span class="text-span" style="color: #333333; font-size: 10.5pt; vertical-align: baseline;">{text}</span>'
        '</p>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</section>\n'
    )

def to_section_dv(incl: str, excl: str) -> str:
    items = []
    if incl:
        items.append('<p dir="ltr" class="text-paragraph" style="line-height: 1.38;">'
                     f'<span class="text-span" style="color: #333333; font-size: 10.5pt; vertical-align: baseline;">{incl}</span>'
                     '</p>')
    if excl:
        items.append('<p dir="ltr" class="text-paragraph" style="line-height: 1.38;">'
                     f'<span class="text-span" style="color: #333333; font-size: 10.5pt; vertical-align: baseline;">{excl}</span>'
                     '</p>')
    if not items:
        return ''
    body = '\n'.join(items)
    return (
        '<section class="section-content-block">\n'
        '<div class="section-content">\n'
        '<div class="content-grid">\n'
        '<div class="grid-column grid-stretch">\n'
        '<div class="column-inner">\n'
        '<div class="content-inner">\n'
        f'{body}\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</section>\n'
    )

def to_section_notes(notes: str) -> str:
    if not (notes and notes.strip()):
        return ''
    return (
        '<section class="section-content-block">\n'
        '<div class="section-content">\n'
        '<div class="content-grid">\n'
        '<div class="grid-column grid-stretch">\n'
        '<div class="column-inner">\n'
        '<div class="content-inner">\n'
        f'<p dir="ltr" class="text-paragraph" style="line-height: 1.38;">'
        f'<span class="text-span" style="color: #333333; font-size: 10.5pt; vertical-align: baseline;">{notes}</span>'
        '</p>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '</section>\n'
    )

def append_before_body_end(html: str, addition: str) -> str:
    marker = '</body>'
    idx = html.rfind(marker)
    if idx == -1:
        return html + addition
    return html[:idx] + addition + html[idx:]

def process_line(line: str, line_no: int, dry_run: bool) -> bool:
    # Expect either CSV or pipe-delimited
    line = line.strip()
    if not line:
        return True
    delim = ',' if ',' in line else '|'
    parts = [p.strip() for p in line.split(delim)]
    if len(parts) < 5:
        print(f"Line {line_no}: skipping invalid, expected 5 columns, got {len(parts)}")
        return True
    tour_id, hl, incl, excl, notes = parts[:5]
    file_path = os.path.join(ROOT, tour_id + '.html')
    if not os.path.exists(file_path):
        print(f"Line {line_no}: file not found: {file_path}")
        return True
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    addition = ''
    hl_block = to_section_hl(hl)
    if hl_block:
        addition += hl_block
    dv_block = to_section_dv(incl, excl)
    if dv_block:
        addition += dv_block
    note_block = to_section_notes(notes)
    if note_block:
        addition += note_block
    if not addition:
        print(f"Line {line_no}: nothing to update for {tour_id}")
        return True
    new_html = append_before_body_end(html, addition)
    if not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
    print(f"Line {line_no}: updated {tour_id}.html (dry_run={dry_run})")
    return True

def main(csv_path: str, dry_run: bool = True):
    if not os.path.exists(csv_path):
        print(f"Batch file not found: {csv_path}")
        return
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, raw in enumerate(lines, start=1):
        if i == 1 and ('id' in raw or '|' in raw or ',' in raw):
            continue  # skip header if present
        process_line(raw, i, dry_run)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/batch_update_tours_offline.py path/to/batch.csv [--dry-run]')
        sys.exit(1)
    csv_path = sys.argv[1]
    dry = ('--dry-run' in sys.argv)
    main(csv_path, dry_run=dry)
