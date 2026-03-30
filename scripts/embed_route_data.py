import os
import json

WORKSPACE = r"F:\Study\Project SItes"

# Load tour routes
with open(os.path.join(WORKSPACE, "tour-routes.json"), "r", encoding="utf-8") as f:
    routes = json.load(f)

TOUR_IDS = [
    "10942", "11338", "13579", "18875", "18910", "18912", "18920", "18921",
    "18941", "18946", "18949", "18978", "19000", "19012", "19021", "19022",
    "19036", "19062", "19066", "19067", "19068", "19069", "19090", "19567", "19688"
]

updated = 0
skipped = 0

for tour_id in TOUR_IDS:
    filepath = os.path.join(WORKSPACE, f"{tour_id}.html")
    if not os.path.exists(filepath):
        print(f"SKIP: {filepath} not found")
        skipped += 1
        continue

    if tour_id not in routes:
        print(f"SKIP: no route data for {tour_id}")
        skipped += 1
        continue

    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Remove any existing inline route data
    if "TOUR_ROUTE_WAYPOINTS" in content:
        # Remove the old inline script
        import re
        content = re.sub(
            r'\s*<script>\s*window\.TOUR_ROUTE_WAYPOINTS\s*=\s*\[.*?\];\s*</script>',
            '',
            content,
            flags=re.DOTALL
        )

    # Generate inline script with route data
    waypoints_json = json.dumps(routes[tour_id]["waypoints"], ensure_ascii=False)
    inline_script = f'\n<script>\nwindow.TOUR_ROUTE_WAYPOINTS = {waypoints_json};\n</script>\n'

    # Insert before tour-map.js script
    marker = '<script src="tour-map.js"></script>'
    if marker in content:
        content = content.replace(marker, inline_script + marker)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"UPDATED: {tour_id}.html")
        updated += 1
    else:
        print(f"SKIP: {tour_id}.html - no tour-map.js marker found")
        skipped += 1

print(f"\nDone! Updated: {updated}, Skipped: {skipped}")
