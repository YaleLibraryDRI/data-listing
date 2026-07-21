const DATA_URL = "data/yale_library_data_listing.json";

const state = {
  items: [],
  search: "",
  subject: "",
  type: "",
  access: ""
};

const els = {
  grid: document.getElementById("dataset-grid"),
  search: document.getElementById("listing-search"),
  subject: document.getElementById("subject-filter"),
  type: document.getElementById("type-filter"),
  access: document.getElementById("access-filter"),
  clear: document.getElementById("clear-filters"),
  resultCount: document.getElementById("result-count")
};

function uniqueSorted(items, key) {
  const values = new Set();

  items.forEach(item => {
    (item[key] || []).forEach(v => values.add(v));
  });

  return Array.from(values).sort();
}

function fillSelect(select, values) {
  if (!select) return;

  values.forEach(value => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

function cardTemplate(item) {
  const tile = item.tile || {};

  const links =
    tile.links ||
    (tile.site
      ? [{
          label: "Access Resource",
          url: tile.site,
          type: "primary"
        }]
      : []);

  return `
    <article class="dataset-card">
      <div class="card-body">

        <h3 class="card-title">
          ${tile.title || "Untitled"}
        </h3>

        <div class="card-description">
          ${tile.description || ""}
        </div>

        <div class="card-footer">
          ${links.map(link => `
  <a
    class="card-link ${link.type || "primary"}"
    href="${link.url}"
    target="_blank"
    rel="noopener noreferrer"
  >
    ${link.label || "Access Resource"}
  </a>
`).join("")}
        </div>

      </div>
    </article>
  `;
}

function searchableText(item) {
  const tile = item.tile || {};

  return [
    tile.title,
    tile.description,
    ...(item.categories1 || []),
    ...(item.categories2 || []),
    ...(item.categories3 || [])
  ]
    .join(" ")
    .toLowerCase();
}

function filteredItems() {
  const q = state.search.toLowerCase();

  return state.items.filter(item => {

    const matchesSearch =
      !q || searchableText(item).includes(q);

    const matchesSubject =
      !state.subject ||
      (item.categories1 || []).includes(state.subject);

    const matchesType =
      !state