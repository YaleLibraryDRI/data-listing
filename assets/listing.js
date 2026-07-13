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
  items.forEach(item => (item[key] || []).forEach(value => values.add(value)));
  return Array.from(values).sort((a, b) => a.localeCompare(b));
}

function fillSelect(select, values) {
  values.forEach(value => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function imageOrInitials(tile) {
  const image = tile.image || "";
  const title = tile.title || "Resource";
  const initials = title
    .replace(/[^A-Za-z0-9 ]/g, " ")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 3)
    .map(word => word[0])
    .join("")
    .toUpperCase();

  return `
    <div class="card-image">
      <img src="${escapeHtml(image)}" alt="" onerror="this.remove(); this.parentElement.textContent='${escapeHtml(initials)}';">
    </div>`;
}

function badgeList(values, className, max = 2) {
  return (values || []).slice(0, max).map(value =>
    `<span class="badge ${className}">${escapeHtml(value)}</span>`
  ).join("");
}

function cardTemplate(item) {
  const tile = item.tile || {};
  const title = tile.title || "Untitled resource";
  const detail = tile.detail || "#";
  const site = tile.site || "";
  const form = tile.form || "";
  const provider = tile.provider || "";

  return `
    <article class="dataset-card">
      ${imageOrInitials(tile)}
      <div class="card-body">
        <h3 class="card-title"><a href="${escapeHtml(detail)}">${escapeHtml(title)}</a></h3>
        <div class="card-provider">${escapeHtml(provider)}</div>
        <div class="card-badges">
          ${badgeList(item.categories1, "subject", 1)}
          ${badgeList(item.categories2, "type", 1)}
          ${badgeList(item.categories3, "access", 1)}
        </div>
        <p class="card-description">${escapeHtml(tile.description)}</p>
        <div class="card-footer">
          <a class="card-link secondary" href="${escapeHtml(detail)}">Details</a>
          ${site ? `<a class="card-link primary" href="${escapeHtml(site)}" target="_blank" rel="noopener">Access</a>` : ""}
          ${!site && form ? `<a class="card-link primary" href="${escapeHtml(form)}" target="_blank" rel="noopener">Request</a>` : ""}
        </div>
      </div>
    </article>`;
}

function searchableText(item) {
  const tile = item.tile || {};
  return [
    tile.title,
    tile.provider,
    tile.topic,
    tile.description,
    ...(item.categories1 || []),
    ...(item.categories2 || []),
    ...(item.categories3 || [])
  ].join(" ").toLowerCase();
}

function filteredItems() {
  const q = state.search.trim().toLowerCase();
  return state.items.filter(item => {
    const matchesSearch = !q || searchableText(item).includes(q);
    const matchesSubject = !state.subject || (item.categories1 || []).includes(state.subject);
    const matchesType = !state.type || (item.categories2 || []).includes(state.type);
    const matchesAccess = !state.access || (item.categories3 || []).includes(state.access);
    return matchesSearch && matchesSubject && matchesType && matchesAccess;
  });
}

function render() {
  const results = filteredItems();
  els.resultCount.textContent = `${results.length} resource${results.length === 1 ? "" : "s"} shown`;
  if (!results.length) {
    els.grid.innerHTML = `<div class="empty-state">No resources match the current filters.</div>`;
    return;
  }
  els.grid.innerHTML = results.map(cardTemplate).join("");
}

fetch(DATA_URL)
  .then(response => response.json())
  .then(data => {
    state.items = data.items || [];
    fillSelect(els.subject, uniqueSorted(state.items, "categories1"));
    fillSelect(els.type, uniqueSorted(state.items, "categories2"));
    fillSelect(els.access, uniqueSorted(state.items, "categories3"));
    render();
  })
  .catch(error => {
    console.error(error);
    els.grid.innerHTML = `<div class="empty-state">The listing data could not be loaded.</div>`;
  });

els.search.addEventListener("input", event => {
  state.search = event.target.value;
  render();
});

els.subject.addEventListener("change", event => {
  state.subject = event.target.value;
  render();
});

els.type.addEventListener("change", event => {
  state.type = event.target.value;
  render();
});

els.access.addEventListener("change", event => {
  state.access = event.target.value;
  render();
});

els.clear.addEventListener("click", () => {
  state.search = "";
  state.subject = "";
  state.type = "";
  state.access = "";
  els.search.value = "";
  els.subject.value = "";
  els.type.value = "";
  els.access.value = "";
  render();
});
