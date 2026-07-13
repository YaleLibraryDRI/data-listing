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
  resultCount: document.getElementById("result-count"),
  search: document.getElementById("listing-search"),
  subject: document.getElementById("subject-filter"),
  type: document.getElementById("type-filter"),
  access: document.getElementById("access-filter"),
  clear: document.getElementById("clear-filters")
};

function uniqueSorted(items, key) {
  const values = new Set();

  items.forEach(item => {
    (item[key] || []).forEach(value => values.add(value));
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

  return `
    <div class="dataset-card">
      <div class="card-body">

        <h3 class="card-title">
          ${tile.title || "Untitled"}
        </h3>

        <p class="card-description">
          ${tile.description || ""}
        </p>

        ${
          tile.site
            ? `
              <div class="card-footer">
                <a
                  href="${tile.site}"
                  target="_blank"
                  rel="noopener"
                  class="card-link primary">
                  Access Resource
                </a>
              </div>
            `
            : ""
        }

      </div>
    </div>
  `;
}
``

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
      !state.type ||
      (item.categories2 || []).includes(state.type);

    const matchesAccess =
      !state.access ||
      (item.categories3 || []).includes(state.access);

    return (
      matchesSearch &&
      matchesSubject &&
      matchesType &&
      matchesAccess
    );
  });
}

function render() {
  const results = filteredItems();

  if (els.resultCount) {
    els.resultCount.textContent =
      `${results.length} resources shown`;
  }

  if (!els.grid) return;

  els.grid.innerHTML =
    results.map(cardTemplate).join("");
}

fetch(DATA_URL)
  .then(response => response.json())
  .then(data => {

    state.items = data.items || [];

    fillSelect(
      els.subject,
      uniqueSorted(state.items, "categories1")
    );

    fillSelect(
      els.type,
      uniqueSorted(state.items, "categories2")
    );

    fillSelect(
      els.access,
      uniqueSorted(state.items, "categories3")
    );

    render();
  })
  .catch(error => {
    console.error(error);
  });

if (els.search) {
  els.search.addEventListener("input", e => {
    state.search = e.target.value;
    render();
  });
}

if (els.subject) {
  els.subject.addEventListener("change", e => {
    state.subject = e.target.value;
    render();
  });
}

if (els.type) {
  els.type.addEventListener("change", e => {
    state.type = e.target.value;
    render();
  });
}

if (els.access) {
  els.access.addEventListener("change", e => {
    state.access = e.target.value;
    render();
  });
}

if (els.clear) {
  els.clear.addEventListener("click", () => {
    state.search = "";
    state.subject = "";
    state.type = "";
    state.access = "";

    if (els.search) els.search.value = "";
    if (els.subject) els.subject.value = "";
    if (els.type) els.type.value = "";
    if (els.access) els.access.value = "";

    render();
  });
}