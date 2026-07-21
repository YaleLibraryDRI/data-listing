import pandas as pd
import json
import re
from pathlib import Path

INPUT_FILE = "yale_library_data_listing_reviewed_v2.xlsx"

# --------------------------------------------------
# Load workbook
# --------------------------------------------------

df = pd.read_excel(INPUT_FILE).fillna("")

# --------------------------------------------------
# Subject cleanup
# --------------------------------------------------

def normalize_subjects(value):
    if not value:
        return ""

    subjects = [x.strip() for x in str(value).split(";")]

    subjects = [
        "Geospatial Data"
        if s == "GIS & Spatial Data"
        else s
        for s in subjects
    ]

    return "; ".join(subjects)

df["Subjects"] = df["Subjects"].apply(normalize_subjects)

# --------------------------------------------------
# Encoding cleanup
# --------------------------------------------------

def clean_text(text):
    text = str(text)

    replacements = {
        "╩": "",
        "ÔÇÖ": "'",
        "ÔÇ£": '"',
        "ÔÇ¥": '"',
        "ÔÇô": "-",
        "ÔÇö": "--",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()

    return text

for col in ["Title", "Description", "Access note"]:
    df[col] = df[col].apply(clean_text)

# --------------------------------------------------
# Title cleanup
# --------------------------------------------------

TITLE_FIXES = {
    "Hartford courant dataset":
        "Hartford Courant Dataset",

    "Los Angeles times dataset":
        "Los Angeles Times Dataset",

    "Wall Street journal dataset":
        "Wall Street Journal Dataset",

    "Times of India dataset":
        "Times of India Dataset",

    "New York Times dataset":
        "New York Times Dataset",

    "Philadelphia tribune dataset":
        "Philadelphia Tribune Dataset",

    "Toronto star dataset":
        "Toronto Star Dataset",
}

df["Title"] = df["Title"].replace(TITLE_FIXES)

# --------------------------------------------------
# Resource type corrections
# --------------------------------------------------

TYPE_FIXES = {
    "Chinese newspapers collection dataset":
        "Text Corpus",

    "Communist historical newspaper collection dataset":
        "Text Corpus",

    "Chinese recorder and the Protestant missionary community in China dataset":
        "Text Corpus",

    "CoNLL shared task 2007: Arabic & Engish":
        "Linguistic Data",

    "Wall Street Journal Online":
        "Data Platform",
}

for title, new_type in TYPE_FIXES.items():
    df.loc[df["Title"] == title, "Resource type"] = new_type

# --------------------------------------------------
# Sort alphabetically
# --------------------------------------------------

df = df.sort_values("Title")

# --------------------------------------------------
# Save cleaned workbook
# --------------------------------------------------

df.to_excel(
    "yale_library_data_listing_clean.xlsx",
    index=False
)

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def split_values(value):
    return [
        x.strip()
        for x in str(value).split(";")
        if x.strip()
    ]

def slugify(text):
    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text
    )

    return text.strip("-")

# --------------------------------------------------
# Build JSON structure
# --------------------------------------------------

items = []

for _, row in df.iterrows():

    tile = {
        "title": row["Title"],
        "description": row["Description"],
        "image":
            f"../Images/Datasets/{slugify(row['Title'])}.png"
    }

    if row["URL"]:
        tile["site"] = row["URL"]

    if row["Provider"]:
        tile["provider"] = row["Provider"]

    if row["Access note"]:
        tile["access-note"] = row["Access note"]

    items.append({
        "categories1":
            split_values(row["Subjects"]),

        "categories2":
            split_values(row["Resource type"]),

        "categories3":
            split_values(row["Access model"]),

        "tile":
            tile
    })

# --------------------------------------------------
# Write JSON
# --------------------------------------------------

with open(
    "yale_library_data_listing.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        {"items": items},
        f,
        indent=2,
        ensure_ascii=False
    )

# --------------------------------------------------
# Write YAML
# --------------------------------------------------

try:
    import yaml

    with open(
        "yale_library_data_listing.yml",
        "w",
        encoding="utf-8"
    ) as f:

        yaml.dump(
            {"items": items},
            f,
            sort_keys=False,
            allow_unicode=True
        )

except ImportError:

    print(
        "Install PyYAML with: pip install pyyaml"
    )

print("Done.")
print("Created:")
print("  yale_library_data_listing_clean.xlsx")
print("  yale_library_data_listing.json")
print("  yale_library_data_listing.yml")