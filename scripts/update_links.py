#!/usr/bin/env python3
import os
import urllib.parse

# Mapping old file names (as they appeared in the repo) to new Vietnamese names (with diacritics)
# This script updates href references in all HTML files to point to the newly renamed files.
MAPPING = [
    ("Vng Tu.html", "Vũng Tàu.html"),
    ("Ty Ninh.html", "Tây Ninh.html"),
    ("Tour min Trung.html", "Tour miền Trung.html"),
    ("Tour Min Nam.html", "Tour miền Nam.html"),
    ("Tour min Bc.html", "Tour miền Bắc.html"),
    ("Tng quan cng ty.html", "Tổng quan công ty.html"),
    ("Thng tin lin h.html", "Thông tin liên hệ.html"),
    ("Si Gn.html", "Sài Gòn.html"),
    ("Phan Thit.html", "Phan Thiết.html"),
    ("PHIU GP_.html", "Phiếu góp ý.html"),
    ("Nng.html", "Đà Nẵng.html"),
    ("V my bay.html", "Vé máy bay.html"),
    ("Thng gia.html", "Thương gia.html"),
    ("t phng.html", "Đặt phòng.html"),
    ("Ph thng.html", "Phổ thông.html"),
    ("Hu.html", "Huế.html"),
    # Do not rename folders to avoid asset load issues; only Hu.html -> Huế.html mapping is kept
    # Support Hà Giang rename
    ("H Giang.html", "Hà Giang.html"),
    ("H Giang", "Hà Giang"),
    ("H Giang.html", "Hà Giang.html"),
    ("H Giang/", "Hà Giang/"),
    ("Hu.html", "Huế.html"),
]

def encode_target(name: str) -> str:
    # Encode the target filename for URL paths (UTF-8 percent-encoding)
    return urllib.parse.quote(name)

def update_file(path: str, old: str, new: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return
    updated = False
    # 1) Replace plain old filename occurrences (e.g., inside href="...old.html" or in text)
    if old in content:
        content = content.replace(old, new)
        updated = True
    # 2) Replace URL-encoded old filenames (e.g., old with %20 for spaces)
    old_enc = old.replace(' ', '%20')
    if old_enc in content:
        # Compute encoded form for the new name
        new_enc = encode_target(new)
        content = content.replace(old_enc, new_enc)
        updated = True
    if updated:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    # Walk through repo and update all HTML files
    for root, _, files in os.walk('.', topdown=True):
        for fname in files:
            if not fname.lower().endswith('.html'):
                continue
            full = os.path.join(root, fname)
            for old, new in MAPPING:
                update_file(full, old, new)
                # Also attempt replacements in case the filename appears without extension tweaks
                # (Less common, but harmless)
                update_file(full, old + '.html', new + '.html')

if __name__ == '__main__':
    main()
