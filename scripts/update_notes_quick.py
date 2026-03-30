#!/usr/bin/env python3
"""Batch update Ghi chú (Notes) sections for tour HTML pages.
Input CSV/TSV: id, notes_text
For each tour_id, replace the content inside the Ghi chú details block with a single paragraph containing notes_text.
Supports --dry-run to preview changes without writing files.
"""
import csv
import sys
import os
import re

ROOT = r"F:\Study\Project SItes"

PATTERN = re.compile(
    r'(<details[^>]*>\s*<summary>Ghi chú</summary>\s*<div class="dropdown-body">)(.*?)(</div>\s*</details>)',
    re.DOTALL
)

def update_notes_in_html(html: str, note: str) -> str:
    if not note:
        return html
    # Build a single paragraph for the note
    note_html = (
        '<p dir="ltr" class="text-paragraph" style="line-height: 1.38; margin-bottom: 0.0pt; padding: 0.0pt;">'
        '<span class="text-span" style="color: #000000; font-size: 11.0pt; vertical-align: baseline;">' + note + '</span>'
        '</p>'
    )
    m = PATTERN.search(html)
    if not m:
        return html
    groups = m.groups()
    new_mid = note_html
    return html[:m.start()] + groups[0] + new_mid + groups[2] + html[m.end():]

def process_line(line: str, line_no: int, dry_run: bool) -> bool:
    line = line.strip()
    if not line:
        return True
    delim = ',' if ',' in line else '|'
    parts = [p.strip() for p in line.split(delim)]
    if len(parts) < 2:
        print(f"Line {line_no}: skip invalid (need id + notes)")
        return True
    tour_id, note = parts[0], parts[1]
    path = os.path.join(ROOT, f"{tour_id}.html")
    if not os.path.exists(path):
        print(f"Line {line_no}: file not found: {path}")
        return True
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    new_html = update_notes_in_html(html, note)
    if not dry_run:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
    print(f"Line {line_no}: updated {tour_id}.html (dry_run={dry_run})")
    return True

def main(batch_csv: str, dry_run: bool = True):
    if not os.path.exists(batch_csv):
        print(f"Batch file not found: {batch_csv}")
        return
    with open(batch_csv, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f if ln.strip()]
    for i, line in enumerate(lines, start=1):
        if i == 1 and ('id' in line or line.find('|') != -1 or line.find(',') != -1):
            # skip header if present on first line
            if any(ch.isalpha() for ch in line):
                continue
        process_line(line, i, dry_run)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/update_notes_quick.py path/to/batch.csv [--dry-run]')
        sys.exit(1)
    batch = sys.argv[1]
    dry = ('--dry-run' in sys.argv)
    main(batch, dry_run=dry)
