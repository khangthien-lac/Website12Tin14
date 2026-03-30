import os
import re

WORKSPACE = r"F:\Study\Project SItes"

TOUR_IDS = [
    "10942", "11338", "13579", "18875", "18910", "18912", "18920", "18921",
    "18941", "18946", "18949", "18978", "19000", "19012", "19021", "19022",
    "19036", "19062", "19066", "19067", "19068", "19069", "19090", "19567", "19688"
]

LEAFLET_CSS = '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">'

LEAFLET_JS = '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>'

TOUR_MAP_JS = '<script src="tour-map.js"></script>'

updated = 0
skipped = 0

for tour_id in TOUR_IDS:
    filepath = os.path.join(WORKSPACE, f"{tour_id}.html")
    if not os.path.exists(filepath):
        print(f"SKIP: {filepath} not found")
        skipped += 1
        continue

    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    if "leaflet" in content.lower():
        print(f"SKIP: {tour_id}.html already has Leaflet")
        skipped += 1
        continue

    modified = False

    # Add Leaflet CSS after the existing style.css link
    if LEAFLET_CSS not in content:
        content = content.replace(
            '<link rel="stylesheet" href="style.css">',
            '<link rel="stylesheet" href="style.css">\n' + LEAFLET_CSS,
            1
        )
        modified = True

    # Add Leaflet JS and tour-map.js before </body>
    scripts_block = f'\n{LEAFLET_JS}\n{TOUR_MAP_JS}\n'
    if '</body>' in content and 'tour-map.js' not in content:
        content = content.replace('</body>', scripts_block + '</body>', 1)
        modified = True

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"UPDATED: {tour_id}.html")
        updated += 1
    else:
        print(f"NO CHANGE: {tour_id}.html")
        skipped += 1

print(f"\nDone! Updated: {updated}, Skipped: {skipped}")
