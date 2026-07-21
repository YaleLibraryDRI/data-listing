import pandas as pd
import json
import re
from pathlib import Path

# ==================================================
# Configuration
# ==================================================

INPUT_FILE = "yale_library_data_listing_clean.xlsx"

OUTPUT_XLSX = "yale_library_data_listing_clean_updated.xlsx"
OUTPUT_CSV = "yale_library_data_listing_clean_updated.csv"
OUTPUT_JSON = "yale_library_data_listing.json"
OUTPUT_YML = "yale_library_data_listing.yml"

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def clean_text(value):
    """Clean common encoding artifacts and normalize whitespace."""
    if pd.isna(value):
        return ""

    text = str(value)

    replacements = {
        "╩": "",
        "ÔÇÖ": "'",
        "ÔÇ£": '"',
        "ÔÇ¥": '"',
        "ÔÇô": "-",
        "ÔÇö": "—",
        "�": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_values(value):
    """Split semicolon-separated taxonomy values."""
    value = clean_text(value)

    if not value:
        return []

    return [
        item.strip()
        for item in value.split(";")
        if item.strip()
    ]


def slugify(text):
    """Create image filename slug from title."""
    text = clean_text(text).lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def first_existing_column(row, candidates):
    """
    Return the first non-empty value from a list of possible column names.
    This allows the spreadsheet to use slightly different column names.
    """
    for col in candidates:
        if col in row and clean_text(row[col]):
            return clean_text(row[col])

    return ""


def yaml_quote(value):
    """Safely quote a value for simple YAML output."""
    return json.dumps(clean_text(value), ensure_ascii=False)


# ==================================================
# Load workbook
# ==================================================

df = pd.read_excel(INPUT_FILE).fillna("")

# ==================================================
# Normalize standard text fields
# ==================================================

for col in [
    "Title",
    "Description",
    "URL",
    "Access note",
    "Subjects",
    "Resource type",
    "Access model",
    "Provider",
]:
    if col in df.columns:
        df[col] = df[col].apply(clean_text)

# ==================================================
# Subject cleanup
# ==================================================

def normalize_subjects(value):
    subjects = split_values(value)

    normalized = []

    for subject in subjects:
        if subject == "GIS & Spatial Data":
            subject = "Geospatial Data"

        if subject == "Technology & Innovation":
            continue

        if subject not in normalized:
            normalized.append(subject)

    return "; ".join(normalized)


if "Subjects" in df.columns:
    df["Subjects"] = df["Subjects"].apply(normalize_subjects)

# ==================================================
# Title cleanup
# ==================================================

def normalize_title(title):
    title = clean_text(title)

    # Remove trailing period unless title appears to end in an abbreviation.
    if title.endswith(".") and not re.search(r"\b[A-Z]\.$", title):
        title = title[:-1].strip()

    title_fixes = {
        "Hartford courant dataset": "Hartford Courant Dataset",
        "Los Angeles times dataset": "Los Angeles Times Dataset",
        "Wall Street journal dataset": "Wall Street Journal Dataset",
        "Times of India dataset": "Times of India Dataset",
        "New York Times dataset": "New York Times Dataset",
        "Philadelphia tribune dataset": "Philadelphia Tribune Dataset",
        "Toronto star dataset": "Toronto Star Dataset",
        "Chicago tribune dataset": "Chicago Tribune Dataset",
        "Boston globe dataset": "Boston Globe Dataset",
        "Washington post dataset": "Washington Post Dataset",
        "San Francisco chronicle dataset": "San Francisco Chronicle Dataset",
        "Pittsburgh post-gazette dataset": "Pittsburgh Post-Gazette Dataset",
        "Minneapolis star tribune dataset": "Minneapolis Star Tribune Dataset",
        "Cleveland call and post dataset": "Cleveland Call and Post Dataset",
    }

    return title_fixes.get(title, title)


df["Title"] = df["Title"].apply(normalize_title)

# ==================================================
# Resource type cleanup
# ==================================================

TYPE_FIXES = {
    "Chinese newspapers collection dataset": "Text Corpus",
    "Chinese Newspapers Collection Dataset": "Text Corpus",

    "Communist historical newspaper collection dataset": "Text Corpus",
    "Communist Historical Newspaper Collection Dataset": "Text Corpus",

    "Chinese recorder and the Protestant missionary community in China dataset": "Text Corpus",
    "Chinese Recorder and the Protestant Missionary Community in China Dataset": "Text Corpus",

    "CoNLL shared task 2007: Arabic & Engish": "Linguistic Data",
    "CoNLL shared task 2007: Arabic & English": "Linguistic Data",

    "Wall Street Journal Online": "Data Platform",
}

if "Resource type" in df.columns:
    for title, resource_type in TYPE_FIXES.items():
        df.loc[df["Title"] == title, "Resource type"] = resource_type

# ==================================================
# Build access links
# ==================================================

PRIMARY_LABEL_COLUMNS = [
    "Primary Link Label",
    "Primary Access Label",
    "Primary Button Label",
    "Link Label 1",
    "Access Label 1",
]

PRIMARY_URL_COLUMNS = [
    "Primary URL",
    "Primary Link",
    "Primary Access URL",
    "URL 1",
    "Access URL 1",
]

SECONDARY_LABEL_COLUMNS = [
    "Secondary Link Label",
    "Secondary Access Label",
    "Secondary Button Label",
    "Link Label 2",
    "Access Label 2",
]

SECONDARY_URL_COLUMNS = [
    "Secondary URL",
    "Secondary Link",
    "Secondary Access URL",
    "URL 2",
    "Access URL 2",
]


def build_links(row):
    """
    Build one or two access-link objects.

    Output example:
    [
      {
        "label": "Access on Data Green",
        "url": "...",
        "type": "primary"
      },
      {
        "label": "Access through TDM Studio",
        "url": "...",
        "type": "secondary"
      }
    ]
    """

    links = []

    primary_label = first_existing_column(row, PRIMARY_LABEL_COLUMNS)
    primary_url = first_existing_column(row, PRIMARY_URL_COLUMNS)

    secondary_label = first_existing_column(row, SECONDARY_LABEL_COLUMNS)
    secondary_url = first_existing_column(row, SECONDARY_URL_COLUMNS)

    fallback_url = clean_text(row.get("URL", ""))

    # If there is no explicit primary URL, fall back to URL.
    if not primary_url and fallback_url:
        primary_url = fallback_url

    if not primary_label and primary_url:
        primary_label = "Access Resource"

    if primary_url:
        links.append({
            "label": primary_label,
            "url": primary_url,
            "type": "primary"
        })

    if secondary_url:
        if not secondary_label:
            secondary_label = "Secondary Access"

        links.append({
            "label": secondary_label,
            "url": secondary_url,
            "type": "secondary"
        })

    return links


# ==================================================
# Sort alphabetically
# ==================================================

df = df.sort_values("Title")

# ==================================================
# Save cleaned spreadsheet and CSV
# ==================================================

df.to_excel(OUTPUT_XLSX, index=False)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

# ==================================================
# Build JSON and YAML structures
# ==================================================

json_items = []

yaml_lines = [
    "items:"
]

for _, row in df.iterrows():

    title = clean_text(row.get("Title", ""))
    description = clean_text(row.get("Description", ""))

    if not title:
        continue

    subjects = split_values(row.get("Subjects", "")) or ["Uncategorized"]
    resource_types = split_values(row.get("Resource type", "")) or ["Dataset"]
    access_models = split_values(row.get("Access model", "")) or ["External platform"]

    links = build_links(row)

    tile = {
        "title": title,
        "description": description,
        "image": f"../Images/Datasets/{slugify(title)}.png"
    }

    # Keep site for backward compatibility with older listing.js versions.
    if links:
        tile["site"] = links[0]["url"]
        tile["links"] = links

    provider = clean_text(row.get("Provider", ""))
    if provider:
        tile["provider"] = provider

    access_note = clean_text(row.get("Access note", ""))
    if access_note:
        tile["access-note"] = access_note

    # JSON item
    json_items.append({
        "categories1": subjects,
        "categories2": resource_types,
        "categories3": access_models,
        "tile": tile
    })

    # YAML item
    yaml_lines.append("- categories1:")
    for subject in subjects:
        yaml_lines.append(f"  - {yaml_quote(subject)}")

    yaml_lines.append("  categories2:")
    for resource_type in resource_types:
        yaml_lines.append(f"  - {yaml_quote(resource_type)}")

    yaml_lines.append("  categories3:")
    for access_model in access_models:
        yaml_lines.append(f"  - {yaml_quote(access_model)}")

    yaml_lines.append("  tiles:")
    yaml_lines.append(f"  - title: {yaml_quote(tile['title'])}")
    yaml_lines.append(f"    description: {yaml_quote(tile['description'])}")
    yaml_lines.append(f"    image: {yaml_quote(tile['image'])}")

    if tile.get("site"):
        yaml_lines.append(f"    site: {yaml_quote(tile['site'])}")

    if tile.get("provider"):
        yaml_lines.append(f"    provider: {yaml_quote(tile['provider'])}")

    if tile.get("access-note"):
        yaml_lines.append(f"    access-note: {yaml_quote(tile['access-note'])}")

    if tile.get("links"):
        yaml_lines.append("    links:")

        for link in tile["links"]:
            yaml_lines.append(f"      - label: {yaml_quote(link['label'])}")
            yaml_lines.append(f"        url: {yaml_quote(link['url'])}")
            yaml_lines.append(f"        type: {yaml_quote(link['type'])}")

# ==================================================
# Write JSON
# ==================================================

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(
        {"items": json_items},
        f,
        ensure_ascii=False,
        indent=2
    )

# ==================================================
# Write YAML
# ==================================================

with open(OUTPUT_YML, "w", encoding="utf-8") as f:
    f.write("\n".join(yaml_lines) + "\n")

# ==================================================
# Summary
# ==================================================

print("Done.")
print(f"Records exported: {len(json_items)}")
print("Created:")
print(f"  {OUTPUT_XLSX}")
print(f"  {OUTPUT_CSV}")
print(f"  {OUTPUT_JSON}")
print(f"  {OUTPUT_YML}")