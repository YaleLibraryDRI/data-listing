# Yale Library Data Listing

Prototype Quarto/GitHub Pages site for a Yale Library data listing.

## Main files

- `_quarto.yml` — Quarto website configuration
- `index.qmd` — home page
- `datasets.qmd` — searchable/filterable listing page
- `assets/listing.css` — compact Yale-themed card styling
- `assets/listing.js` — catalog search, filters, and card rendering
- `data/yale_library_data_listing.yml` — human-editable source listing data
- `data/yale_library_data_listing.json` — browser-friendly listing data used by `listing.js`
- `datasets/` — generated detail pages, one per resource
- `.github/workflows/publish.yml` — GitHub Pages deployment workflow

## Local preview

```bash
quarto preview
```

## Render

```bash
quarto render
```

## GitHub Pages setup

In the GitHub repository settings, enable Pages with GitHub Actions as the source. Then push to the `main` branch.

Before publishing, update `site-url` and `repo-url` in `_quarto.yml`.
