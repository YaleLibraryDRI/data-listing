import csv
import re
from pathlib import Path
import yaml

src = Path('/mnt/data/yale_library_data_listing_simplified.csv')
out = Path('/mnt/data/yale_library_data_listing_simplified.yml')


def clean(value):
    value = '' if value is None else str(value)
    value = value.replace('\r', ' ').replace('\n', ' ')
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def split_multi(value):
    value = clean(value)
    if not value:
        return []
    return [part.strip() for part in value.split(';') if part.strip()]


def slugify(value):
    value = clean(value).lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'resource'

with src.open('r', encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))

items = []
for row in rows:
    title = clean(row.get('Title'))
    description = clean(row.get('Description'))
    url = clean(row.get('URL'))
    access_note = clean(row.get('Access note'))
    subjects = split_multi(row.get('Subjects'))
    access_model = split_multi(row.get('Access model'))
    provider = clean(row.get('Provider'))

    # Keep records usable even if a subject was blank in the CSV.
    # This does not re-add removed vocabulary like General Research.
    if not subjects:
        subjects = ['Uncategorized']

    tile = {
        'title': title,
        'description': description,
        'image': f'../Images/Datasets/{slugify(title)}.png',
    }
    if provider:
        tile['provider'] = provider
    if url:
        tile['site'] = url
    if access_note:
        tile['access-note'] = access_note

    items.append({
        'categories1': subjects,
        'categories3': access_model,
        'tiles': [tile],
    })

# Write a compact YAML file with comments documenting the simplified taxonomy.
header = """## =============================================================================\n## Yale Library Data Listing\n## Generated from yale_library_data_listing_simplified.csv\n## Simplified filter groups:\n##   categories1: Subjects\n##   categories3: Access model\n## Note: categories2/data-resource type has been intentionally removed.\n## =============================================================================\n\n"""

body = yaml.safe_dump({'items': items}, sort_keys=False, allow_unicode=True, width=1000)
out.write_text(header + body, encoding='utf-8')

# Validation
with out.open('r', encoding='utf-8') as f:
    loaded = yaml.safe_load(f)
loaded_items = loaded.get('items', [])
remaining_categories2 = any('categories2' in item for item in loaded_items)
removed_subjects = []
for item in loaded_items:
    for subject in item.get('categories1', []):
        if subject in {'General Research', 'Scholarly Literature'}:
            removed_subjects.append((item['tiles'][0]['title'], subject))

print(f'Wrote {len(loaded_items)} items to {out}')
print(f'categories2 present: {remaining_categories2}')
print(f'Removed subjects still present: {len(removed_subjects)}')
if removed_subjects:
    print(removed_subjects[:20])
