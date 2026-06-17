// Dependency-free client search over the build-time index (/search-index.json).
// All-terms substring match across title + body; title hits rank first. No lunr,
// no CDN — works on any static host. Ported from the legacy site's search.js.
//
// Config is read off the search input's data attributes (set server-side):
//   data-index  — URL of the search index JSON (already base-prefixed)
//   data-base   — site base path, prefixed onto each hit's root-absolute url
interface SearchDoc {
  title: string;
  url: string;
  section: string;
  text: string;
}

const box = document.getElementById("bosc-search") as HTMLInputElement | null;
const panel = document.getElementById("bosc-search-results");

if (box && panel) {
  const indexUrl = box.dataset.index || "/search-index.json";
  const base = (box.dataset.base || "/").replace(/\/$/, "");

  let index: SearchDoc[] | null = null;
  const load = (): Promise<SearchDoc[]> => {
    if (index) return Promise.resolve(index);
    return fetch(indexUrl)
      .then((r) => r.json())
      .then((d: SearchDoc[]) => (index = d))
      .catch(() => (index = []));
  };

  const esc = (s: string): string =>
    s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

  // A ~140-char window around the first matched term, with the term marked.
  const snippet = (text: string, terms: string[]): string => {
    const lower = text.toLowerCase();
    let at = -1;
    let hit = "";
    for (const t of terms) {
      const p = lower.indexOf(t);
      if (p >= 0 && (at < 0 || p < at)) {
        at = p;
        hit = t;
      }
    }
    if (at < 0) return esc(text.slice(0, 140));
    const start = Math.max(0, at - 50);
    const frag = `${(start > 0 ? "…" : "") + text.slice(start, at + 90)}…`;
    const re = new RegExp(`(${hit.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig");
    return esc(frag).replace(re, "<mark>$1</mark>");
  };

  const render = (hits: SearchDoc[], terms: string[]): void => {
    if (!hits.length) {
      panel.innerHTML = '<div class="search-empty">No matches</div>';
      panel.hidden = false;
      return;
    }
    panel.innerHTML = hits
      .map(
        (d) =>
          '<a class="search-hit" href="' +
          base +
          esc(d.url) +
          '">' +
          '<span class="search-hit-title">' +
          esc(d.title) +
          "</span>" +
          '<span class="search-hit-meta">' +
          esc(d.section) +
          "</span>" +
          '<span class="search-hit-snip">' +
          snippet(d.text, terms) +
          "</span></a>",
      )
      .join("");
    panel.hidden = false;
  };

  const run = (): void => {
    const q = box.value.trim().toLowerCase();
    if (q.length < 2) {
      panel.hidden = true;
      panel.innerHTML = "";
      return;
    }
    const terms = q.split(/\s+/);
    void load().then((docs) => {
      const hits: [number, SearchDoc][] = [];
      for (const d of docs) {
        const title = (d.title || "").toLowerCase();
        const hay = `${title} ${(d.text || "").toLowerCase()}`;
        if (!terms.every((t) => hay.indexOf(t) >= 0)) continue;
        const score = title.indexOf(q) >= 0 ? 0 : terms.every((t) => title.indexOf(t) >= 0) ? 1 : 2;
        hits.push([score, d]);
      }
      hits.sort((a, b) => a[0] - b[0]);
      render(
        hits.slice(0, 20).map((h) => h[1]),
        terms,
      );
    });
  };

  box.addEventListener("input", run);
  box.addEventListener("focus", run);
  box.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      box.blur();
      panel.hidden = true;
    }
    if (e.key === "Enter") {
      const first = panel.querySelector<HTMLAnchorElement>("a.search-hit");
      if (first) window.location.href = first.getAttribute("href")!;
    }
  });
  document.addEventListener("click", (e) => {
    const target = e.target as Node;
    if (!panel.contains(target) && target !== box) panel.hidden = true;
  });
}
