// Highlight the per-section TOC entry whose section is currently in view.
// Dependency-free: an IntersectionObserver over the headings the rail links to.
// Adapted from the legacy site's toc.js; the rail links carry full hrefs
// (e.g. /site/#records), so we key by each link's URL hash.
const rail = document.querySelector(".section-toc");

if (rail && "IntersectionObserver" in window) {
  const links = new Map<string, HTMLAnchorElement>();
  rail.querySelectorAll<HTMLAnchorElement>("a[href]").forEach((a) => {
    const hash = new URL(a.href, window.location.href).hash.slice(1);
    if (hash) links.set(decodeURIComponent(hash), a);
  });
  const ids = [...links.keys()];

  if (ids.length) {
    const visible = new Map<string, boolean>();
    const update = (): void => {
      let current: string | null = null;
      for (const id of ids) {
        if (visible.get(id)) {
          current = id;
          break;
        }
      }
      ids.forEach((id) => links.get(id)!.classList.toggle("active", id === current));
    };

    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => visible.set(e.target.id, e.isIntersecting));
        update();
      },
      // Trip a heading "active" once it reaches the upper third of the viewport.
      { rootMargin: "0px 0px -66% 0px" },
    );
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) obs.observe(el);
    });
  }
}
