const DATA_URL = "data/yale_library_data_listing.json";

const state = {
  items: [],
  search: "",
  subject: "",
  type: "",
  access: "",
  page: 1,
  pageSize: 25
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

function getResourceTypeIcon(type) {

  if (!type) return "";

  const resourceType =
    type
      .toLowerCase()
      .replace(/\s+/g, "-");

  return `
    assets/icons/${resourceType}.svg
  `;
}

function cardTemplate(item) {

  const tile = item.tile || {};

  const resourceType =
    item.categories2?.[0]
      ?.toLowerCase()
      .replace(/\s+/g, "-");

  const icon =
    resourceType
      ? `<img
           class="resource-type-icon"
           src="assets/icons/${resourceType}.svg"
 e
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

          ${icon}

          <span>
            ${tile.title || "Untitled"}
          </span>

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

function renderPagination(totalPages) {

  let pagination =
    document.getElementById("pagination");

  if (!pagination) {

    pagination =
      document.createElement("div");

    pagination.id = "pagination";

    els.grid.after(pagination);
  }

  pagination.innerHTML = `
    <button
      id="prev-page"
      ${state.page === 1 ? "disabled" : ""}
    >
      Previous
    </button>

    <span>
      Page ${state.page} of ${totalPages}
    </span>

    <button
      id="next-page"
      ${
        state.page === totalPages
          ? "disabled"
          : ""
      }
    >
      Next
    </button>
  `;

  document
    .getElementById("prev-page")
    ?.addEventListener("click", () => {

      if (state.page > 1) {
        state.page--;
        render();
      }
    });

  document
    .getElementById("next-page")
    ?.addEventListener("click", () => {

      if (state.page < totalPages) {
        state.page++;
        render();
      }
    });
}

function render() {

  const results = filteredItems();

  const totalPages = Math.max(
    1,
    Math.ceil(
      results.length / state.pageSize
    )
  );

  if (state.page > totalPages) {
    state.page = totalPages;
  }

  const start =
    (state.page - 1) * state.pageSize;

  const end =
    start + state.pageSize;

  const pageResults =
    results.slice(start, end);

  if (els.resultCount) {

    els.resultCount.textContent =
      `${results.length} resources shown (page ${state.page} of ${totalPages})`;
  }

  if (!els.grid) return;

  els.grid.innerHTML =
    pageResults.map(cardTemplate).join("");

  renderPagination(totalPages);
}

fetch(DATA_URL)
  .then(response => response.json())
  .then(data => {

    state.items = data.items || [];

    state.items.sort((a, b) => {

      const aTitle =
        (a.tile?.title || "")
          .toLowerCase();

      const bTitle =
        (b.tile?.title || "")
          .toLowerCase();

      return aTitle.localeCompare(bTitle);
    });

    fillSelect(
      els.subject,
      uniqueSorted(
        state.items,
        "categories1"
      )
    );

    fillSelect(
      els.type,
      uniqueSorted(
        state.items,
        "categories2"
      )
    );

    fillSelect(
      els.access,
      uniqueSorted(
        state.items,
        "categories3"
      )
    );

    render();
  })
  .catch(error => {

    console.error(
      "Failed to load data:",
      error
    );
  });

if (els.search) {

  els.search.addEventListener(
    "input",
    e => {

      state.search =
        e.target.value;

      state.page = 1;

      render();
    }
  );
}

if (els.subject) {

  els.subject.addEventListener(
    "change",
    e => {

      state.subject =
        e.target.value;

      state.page = 1;

      render();
    }
  );
}

if (els.type) {

  els.type.addEventListener(
    "change",
    e => {

      state.type =
        e.target.value;

      state.page = 1;

      render();
    }
  );
}

if (els.access) {

  els.access.addEventListener(
    "change",
    e => {

      state.access =
        e.target.value;

      state.page = 1;

      render();
    }
  );
}

if (els.clear) {

  els.clear.addEventListener(
    "click",
    () => {

      state.search = "";
      state.subject = "";
      state.type = "";
      state.access = "";
      state.page = 1;

      if (els.search)
        els.search.value = "";

      if (els.subject)
        els.subject.value = "";

      if (els.type)
        els.type.value = "";

      if (els.access)
        els.access.value = "";

      render();
    }
  );
}