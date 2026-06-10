/**
 * Wiki cross-linking (issue #68): resolve inline `[[wiki links]]` and compute
 * backlinks across the concepts, entities, and people feeds.
 *
 * A `[[Target]]` in a concept/profile body resolves — by normalized title, key,
 * slug, or alias — to the page for that concept, entity, or person. Unresolved
 * links render as a dotted "missing" span (a TODO marker), never a dead anchor.
 */
import { hasFeed, loadFeed } from "./bundle";
import { slugify, type ConceptItem, type EntityNode, type PersonItem } from "./feeds";
import { withBase } from "./site";

export interface WikiTarget {
  url: string;
  label: string;
  kind: "concept" | "entity" | "person";
}

/** Normalize any label/key/slug to a comparable token. */
export function norm(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

let cached: Map<string, WikiTarget> | undefined;

/** The resolution index: normalized name/alias/slug → its page. */
export function wikiIndex(): Map<string, WikiTarget> {
  if (cached) return cached;
  const index = new Map<string, WikiTarget>();
  const add = (names: (string | null | undefined)[], target: WikiTarget): void => {
    for (const n of names) {
      const k = n ? norm(n) : "";
      if (k && !index.has(k)) index.set(k, target);
    }
  };

  if (hasFeed("concepts")) {
    for (const c of loadFeed<ConceptItem[]>("concepts")) {
      add([c.slug, c.title, ...c.aliases], {
        url: `${withBase("/wiki/concepts/")}${c.slug}/`,
        label: c.title,
        kind: "concept",
      });
    }
  }
  if (hasFeed("entities")) {
    for (const e of loadFeed<EntityNode[]>("entities")) {
      add([e.key, e.display, ...e.variants], {
        url: `${withBase("/wiki/entities/")}${slugify(e.key)}/`,
        label: e.display,
        kind: "entity",
      });
    }
  }
  if (hasFeed("people")) {
    for (const p of loadFeed<PersonItem[]>("people")) {
      add([p.slug, p.name, ...p.aliases], {
        url: `${withBase("/site/people/")}${p.slug}/`,
        label: p.name,
        kind: "person",
      });
    }
  }
  cached = index;
  return index;
}

const escapeHtml = (s: string): string =>
  s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

/**
 * Render a markdown-ish body to HTML paragraphs: HTML-escape, then inline code
 * spans and `[[wiki links]]`. (Full markdown/MDX rendering is #69.)
 */
export function renderBody(body: string, index = wikiIndex()): string[] {
  return body
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean)
    .map((para) => {
      let html = escapeHtml(para);
      html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
      html = html.replace(/\[\[([^\]]+)\]\]/g, (_m, inner: string) => {
        const t = index.get(norm(inner));
        return t
          ? `<a href="${t.url}">${escapeHtml(inner)}</a>`
          : `<span class="wikilink-missing" title="unresolved wiki link">${escapeHtml(inner)}</span>`;
      });
      return html;
    });
}

/** Concepts that point at `slug` — via `related` or a `[[link]]` in their body. */
export function conceptBacklinks(slug: string): { url: string; label: string }[] {
  if (!hasFeed("concepts")) return [];
  const concepts = loadFeed<ConceptItem[]>("concepts");
  const self = concepts.find((c) => c.slug === slug);
  const names = self ? new Set([norm(self.slug), norm(self.title), ...self.aliases.map(norm)]) : new Set([slug]);
  const out: { url: string; label: string }[] = [];
  for (const c of concepts) {
    if (c.slug === slug) continue;
    const viaRelated = c.related.some((r) => norm(r) === norm(slug));
    const viaBody = [...c.body.matchAll(/\[\[([^\]]+)\]\]/g)].some((m) => names.has(norm(m[1])));
    if (viaRelated || viaBody) {
      out.push({ url: `${withBase("/wiki/concepts/")}${c.slug}/`, label: c.title });
    }
  }
  return out;
}
