/**
 * Resolve a curated Record Teardown against the live content bundle, at build
 * time. This is what keeps the guided walk and the reference library reading the
 * SAME feeds — the teardown's editorial framing stays curated, but its links and
 * provenance are confirmed against the actual bundle rows:
 *
 *   - `verify` deep-links to the exact `records` row (`/site/records/<group>#<rel>`)
 *     when that row is in the bundle; the row's `citation` is surfaced on the
 *     source card so the provenance is the library's own, not a restatement.
 *   - failing a records row, `verify` deep-links to the backing legal page.
 *   - `connect` concept chips deep-link to `/wiki/concepts/<slug>` when the slug
 *     exists in the `concepts` feed.
 *
 * Everything is PRESENT-CHECKED against the bundle being built, so a minimal
 * fixture (CI) gracefully falls back to the curated link rather than 404-ing.
 */
import { hasFeed, loadFeed } from "./bundle";
import { type Citation, type ConceptItem, type RecordItem, slugify } from "./feeds";
import { legalBySlug } from "./legal";
import { withBase } from "./site";
import type { TeardownConnect, TeardownRecord } from "./teardown";

/** Records in the bundle being built, by `rel` (built once). */
const recordsByRel: Map<string, RecordItem> = (() => {
  const map = new Map<string, RecordItem>();
  if (hasFeed("records")) for (const r of loadFeed<RecordItem[]>("records")) map.set(r.rel, r);
  return map;
})();

/** Concept slugs present in the bundle being built (built once). */
const conceptSlugs: Set<string> = (() => {
  const set = new Set<string>();
  if (hasFeed("concepts")) for (const c of loadFeed<ConceptItem[]>("concepts")) set.add(c.slug);
  return set;
})();

/** Pull the slug out of a `[[wiki-link]]` connect label, slugified. */
function conceptSlugOf(label: string): string | null {
  const m = label.match(/\[\[([^\]]+)\]\]/);
  return m ? slugify(m[1]) : null;
}

export interface ResolvedTeardown {
  teardown: TeardownRecord;
  /** The backing record's bundle citation, when the row is present. */
  liveCitation: Citation | null;
  /** True when `verify` was deep-linked to a real bundle target. */
  verifyResolved: boolean;
}

export function resolveTeardown(t: TeardownRecord): ResolvedTeardown {
  let check = t.check;
  let liveCitation: Citation | null = null;
  let verifyResolved = false;

  // 1. records-backed → deep-link verify to the exact record + surface its citation.
  if (t.recordRel && recordsByRel.has(t.recordRel)) {
    const row = recordsByRel.get(t.recordRel) as RecordItem;
    liveCitation = row.citation;
    check = { ...check, verifyHref: withBase(`/site/records/${row.group}/${slugify(t.recordRel)}`) };
    verifyResolved = true;
  } else if (t.legalSlug && legalBySlug.has(t.legalSlug)) {
    // 2. legal-backed → deep-link verify to the legal-history page.
    check = { ...check, verifyHref: withBase(`/site/legal/${t.legalSlug}`) };
    verifyResolved = true;
  }

  // 3. concept connect chips → deep-link when the slug is in the bundle.
  const connect: TeardownConnect[] = t.connect.map((c) => {
    if (c.kind !== "concept") return c;
    const slug = conceptSlugOf(c.label);
    return slug && conceptSlugs.has(slug) ? { ...c, href: withBase(`/wiki/concepts/${slug}`) } : c;
  });

  return { teardown: { ...t, check, connect }, liveCitation, verifyResolved };
}
