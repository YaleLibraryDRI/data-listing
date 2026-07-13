"""
Update Yale Library data listing YAML categories3 to the new access model values:
- External platform
- Locally hosted at Yale
- Open access
- Workstation access

Run this script from the root of the GitHub repository.
It updates:
  data/yale_library_data_listing.yml
and, if present:
  data/yale_library_data_listing.json

It creates .bak backup files before overwriting.
"""

from pathlib import Path
import json
import re
import shutil
import sys

try:
    import yaml
except ImportError:
    sys.exit("This script requires PyYAML. Install with: pip install pyyaml")

YAML_PATH = Path("data/yale_library_data_listing.yml")
JSON_PATH = Path("data/yale_library_data_listing.json")

ACCESS_MODELS = {
    "external": "External platform",
    "local": "Locally hosted at Yale",
    "open": "Open access",
    "workstation": "Workstation access",
}

# Explicit overrides make the classification easier to audit.
# Edit these lists as your team refines individual resources.
WORKSTATION_TITLES = {
    "Bloomberg Terminal",
    "Morningstar Direct",
}

LOCALLY_HOSTED_TITLES = {
    "CoreLogic",
    "Crunchbase",
    "Orbis Historical",
    "Panjiva",
    "Pyrra Discovery Platform",
}

# Titles treated as open resources based on their public/open web presence or public source role.
# Add/remove titles here as needed after review.
OPEN_ACCESS_TITLES = {
    "Ad*Access",
    "Global Development Finance",
    "International Financial Statistics - IMF",
    "Social Science Research Network (SSRN)",
    "UN Comtrade Premium",
    "UNdata",
    "World Development Indicators",
}

EXTERNAL_PLATFORM_TITLES = set()

OPEN_URL_PATTERNS = [
    "data.worldbank.org",
    "data.un.org",
    "uncomtrade.org",
    "repository.duke.edu",
    "ssrn.com",
]

WORKSTATION_PATTERNS = [
    "workstation",
    "dedicated machine",
    "terminal",
]

LOCAL_PATTERNS = [
    "locally hosted",
    "hosted at yale",
    "available by request",
    "excel/csv file",
    "request access",
]

EXTERNAL_HINT_PATTERNS = [
    "yale.idm.oclc.org",
    "library.yale.edu/eresources",
    "web.library.yale.edu/access",
    "hdl.handle.net/10079/yuldb",
    "wrds-www.wharton.upenn.edu",
    "proquest.com",
    "ebsco",
    "gale.com",
    "factiva",
    "statista",
    "scopus",
    "jstor",
]


def clean(value):
    return re.sub(r"\s+", " ", str(value or "").strip())


def tile_text(item, tile):
    parts = [
        tile.get("title", ""),
        tile.get("description", ""),
        tile.get("site", ""),
        tile.get("form", ""),
        tile.get("access-note", ""),
        " ".join(item.get("categories1", []) or []),
        " ".join(item.get("categories2", []) or []),
    ]
    return clean(" ".join(parts)).lower()


def classify_access_model(item):
    tile = (item.get("tiles") or [{}])[0]
    title = clean(tile.get("title", ""))
    text = tile_text(item, tile)
    site = clean(tile.get("site", "")).lower()
    form = clean(tile.get("form", ""))

    if title in WORKSTATION_TITLES or any(pattern in text for pattern in WORKSTATION_PATTERNS):
        return ACCESS_MODELS["workstation"]

    if title in LOCALLY_HOSTED_TITLES:
        return ACCESS_MODELS["local"]

    if title in OPEN_ACCESS_TITLES or any(pattern in site for pattern in OPEN_URL_PATTERNS):
        # If a Yale request form is present, treat that as local rather than open.
        if form:
            return ACCESS_MODELS["local"]
        return ACCESS_MODELS["open"]

    if title in EXTERNAL_PLATFORM_TITLES:
        return ACCESS_MODELS["external"]

    # A request form without a strong external-platform hint often means Yale-mediated/local delivery.
    if form and not any(pattern in text for pattern in EXTERNAL_HINT_PATTERNS):
        return ACCESS_MODELS["local"]

    # Everything else is a vendor/external platform by default.
    return ACCESS_MODELS["external"]


def update_yaml():
    if not YAML_PATH.exists():
        sys.exit(f"Could not find {YAML_PATH}. Run this from the repository root.")

    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    items = data.get("items", [])

    counts = {label: 0 for label in ACCESS_MODELS.values()}
    changed = 0

    for item in items:
        new_model = classify_access_model(item)
        old = item.get("categories3")
        item["categories3"] = [new_model]
        counts[new_model] += 1
        if old != item["categories3"]:
            changed += 1

    backup = YAML_PATH.with_suffix(YAML_PATH.suffix + ".bak")
    shutil.copy2(YAML_PATH, backup)
    YAML_PATH.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )

    print(f"Updated {YAML_PATH}")
    print(f"Backup written to {backup}")
    print(f"Items updated: {changed}")
    print("Access model counts:")
    for label, count in counts.items():
        print(f"  {label}: {count}")

    return data


def update_json_from_yaml(data):
    if not JSON_PATH.exists():
        print(f"Skipped JSON update because {JSON_PATH} was not found.")
        return

    backup = JSON_PATH.with_suffix(JSON_PATH.suffix + ".bak")
    shutil.copy2(JSON_PATH, backup)

    # The site's listing.js expects JSON shaped as: { items: [{ categories1, categories2, categories3, tile }] }
    json_items = []
    for item in data.get("items", []):
        tile = (item.get("tiles") or [{}])[0]
        json_items.append({
            "categories1": item.get("categories1", []),
            "categories2": item.get("categories2", []),
            "categories3": item.get("categories3", []),
            "tile": tile,
        })

    JSON_PATH.write_text(
        json.dumps({"items": json_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Updated {JSON_PATH}")
    print(f"Backup written to {backup}")


if __name__ == "__main__":
    updated = update_yaml()
    update_json_from_yaml(updated)
