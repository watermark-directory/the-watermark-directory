// search_corpus MCP tool handler (#913).
// BM25 retrieval over the ask-index, with optional site and collection filters.
// Every result carries full provenance; clients must cite source + page, and
// must not paraphrase beyond what the source text says ([verified]/[inference] discipline).

import { loadAskIndex } from "../askIndexLoad";
import { prepare, search } from "../retrieval";

const MAX_LIMIT = 30;
const DEFAULT_LIMIT = 10;

interface SearchCorpusParams {
  query?: unknown;
  site?: unknown;
  collection?: unknown;
  limit?: unknown;
}

interface CorpusHit {
  id: string;
  feed: string;
  title: string;
  text: string;
  url: string;
  source: string | null;
  page: number | null;
  source_kind: string | null;
  confidence: string | null;
  verified: boolean;
  score: number;
}

export async function handleSearchCorpus(
  params: unknown,
  requestUrl: string,
): Promise<Array<{ type: "text"; text: string }>> {
  const p = (params ?? {}) as SearchCorpusParams;
  const query = typeof p.query === "string" ? p.query.trim() : "";
  if (!query) {
    return [{ type: "text", text: JSON.stringify([]) }];
  }

  const rawLimit = typeof p.limit === "number" ? p.limit : DEFAULT_LIMIT;
  const limit = Math.min(Math.max(1, Math.floor(rawLimit)), MAX_LIMIT);

  let units = await loadAskIndex(requestUrl);

  // Site filter: if any units carry a site tag (i.e. this is a tagged index build),
  // filter strictly — `!u.site` would silently leak cross-site results in a mixed
  // index. If NO units have a site tag (legacy index), skip filtering entirely.
  const siteFilter = typeof p.site === "string" && p.site ? p.site : null;
  if (siteFilter) {
    const hasTaggedUnits = units.some((u) => typeof u.site === "string" && u.site.length > 0);
    if (hasTaggedUnits) {
      units = units.filter((u) => u.site === siteFilter);
    }
  }

  // Collection filter maps to the `feed` field (e.g. "timeline", "entities", "records").
  const collectionFilter = typeof p.collection === "string" && p.collection ? p.collection : null;
  if (collectionFilter) {
    units = units.filter((u) => u.feed === collectionFilter);
  }

  const hits = search(prepare(units), query, limit);

  const results: CorpusHit[] = hits.map((h) => ({
    id: h.unit.id,
    feed: h.unit.feed,
    title: h.unit.title,
    text: h.unit.text,
    url: h.unit.url,
    source: h.unit.source ?? null,
    page: h.unit.page ?? null,
    source_kind: h.unit.source_kind ?? null,
    confidence: h.unit.confidence ?? null,
    verified: h.unit.verified ?? false,
    score: Math.round(h.score * 1000) / 1000,
  }));

  return [{ type: "text", text: JSON.stringify(results) }];
}
