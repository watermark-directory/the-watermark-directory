// Dependency-free BM25 retrieval over the build-time ask-index (#209).
//
// Tokenization + scoring happen here, at *query* time, on the Workers runtime — so
// the build (frontend/src/lib/askIndex.ts) only ships raw text units and there is no
// way for build-time and query-time tokenization to drift apart. Mirrors the
// no-dependency posture of the site search (src/scripts/search.ts): plain JS, no lunr,
// no CDN, runs on Web platform globals only.
//
// The corpus is small (the citation-bearing bundle feeds — low hundreds of units), so
// preparing the postings once per loaded index and scoring linearly per request is
// cheap. The Worker caches the prepared index across requests in the same isolate.

/**
 * One retrieval unit — a citation-bearing thing in the bundle (a record, timeline
 * event, entity, …). The shape is duplicated in `src/lib/askIndex.ts` (the build-time
 * producer), exactly as `SearchDoc` is duplicated between `lib/search.ts` and
 * `scripts/search.ts`: the emitted `/ask-index.json` is the contract between them.
 */
export interface AskUnit {
  /** Stable id, `${feed}:${localId}` — what the model and the page cite by. */
  id: string;
  /** The bundle feed this came from (records, timeline, entities, …). */
  feed: string;
  title: string;
  /** Root-absolute deep link (pre-base) to the page this unit lives on. */
  url: string;
  /** The searchable blob (title is indexed separately, weighted). */
  text: string;
  /** Provenance lifted from the item's Citation (#213 resolves these). */
  source?: string | null;
  page?: number | null;
  source_kind?: string | null;
  confidence?: string | null;
  verified?: boolean;
  /** Site slug this unit belongs to (e.g. "lima"). Absent on legacy index entries. */
  site?: string;
}

/** One scored hit: the unit plus its BM25 score. */
export interface Hit {
  unit: AskUnit;
  score: number;
}

// A compact English stoplist — enough to keep BM25 from rewarding filler, small enough
// to stay honest about a record-search vocabulary (kept words like "no"/"not" matter).
const STOPWORDS = new Set([
  "a",
  "an",
  "and",
  "are",
  "as",
  "at",
  "be",
  "by",
  "for",
  "from",
  "has",
  "have",
  "in",
  "into",
  "is",
  "it",
  "its",
  "of",
  "on",
  "or",
  "that",
  "the",
  "to",
  "was",
  "were",
  "what",
  "when",
  "where",
  "which",
  "who",
  "why",
  "will",
  "with",
  "this",
  "these",
  "those",
  "they",
  "their",
  "there",
  "about",
  "how",
  "did",
  "does",
  "do",
]);

/**
 * Lowercase → alphanumeric runs → drop stopwords + 1-char noise, fold a trailing plural
 * "s" so "roundabouts" matches "roundabout". Deterministic and pure; the single source
 * of truth for both indexing and querying.
 */
export function tokenize(text: string): string[] {
  const out: string[] = [];
  for (const m of text.toLowerCase().matchAll(/[a-z0-9]+/g)) {
    let t = m[0];
    if (t.length < 2 || STOPWORDS.has(t)) continue;
    if (t.length > 3 && t.endsWith("s")) t = t.slice(0, -1);
    out.push(t);
  }
  return out;
}

// The title is high-signal, so its tokens are counted with extra weight.
const TITLE_WEIGHT = 2;
const K1 = 1.5;
const B = 0.75;

/** Token counts for one document, plus its length. */
interface Doc {
  tf: Map<string, number>;
  len: number;
}

/** A prepared index: postings + corpus stats, ready to score many queries against. */
export interface PreparedIndex {
  units: AskUnit[];
  docs: Doc[];
  df: Map<string, number>;
  avgdl: number;
  n: number;
}

function addTokens(tf: Map<string, number>, tokens: string[], weight: number): number {
  for (const tok of tokens) tf.set(tok, (tf.get(tok) ?? 0) + weight);
  return tokens.length * weight;
}

/** Precompute term frequencies, document frequencies, and the mean document length. */
export function prepare(units: AskUnit[]): PreparedIndex {
  const docs: Doc[] = [];
  const df = new Map<string, number>();
  let total = 0;
  for (const u of units) {
    const tf = new Map<string, number>();
    let len = addTokens(tf, tokenize(u.text), 1);
    len += addTokens(tf, tokenize(u.title), TITLE_WEIGHT);
    for (const tok of tf.keys()) df.set(tok, (df.get(tok) ?? 0) + 1);
    docs.push({ tf, len });
    total += len;
  }
  const n = units.length;
  return { units, docs, df, avgdl: n > 0 ? total / n : 0, n };
}

/** Robertson–Sparck-Jones idf, the BM25+ non-negative form. */
function idf(df: number, n: number): number {
  return Math.log(1 + (n - df + 0.5) / (df + 0.5));
}

/**
 * Score every unit against `query` and return the top `k` with a positive score,
 * highest first. Empty/irrelevant queries return `[]` — the caller treats that as
 * "not in the record" (the grounding layer refuses rather than inventing context).
 */
export function search(prepared: PreparedIndex, query: string, k = 6): Hit[] {
  const terms = tokenize(query);
  if (terms.length === 0 || prepared.n === 0) return [];
  const { docs, df, avgdl, n, units } = prepared;
  const qterms = [...new Set(terms)];

  const hits: Hit[] = [];
  for (let i = 0; i < docs.length; i++) {
    const { tf, len } = docs[i];
    let score = 0;
    for (const t of qterms) {
      const f = tf.get(t);
      if (!f) continue;
      const denom = f + K1 * (1 - B + (B * len) / (avgdl || 1));
      score += idf(df.get(t) ?? 0, n) * ((f * (K1 + 1)) / denom);
    }
    if (score > 0) hits.push({ unit: units[i], score });
  }
  hits.sort((a, b) => b.score - a.score);
  return hits.slice(0, k);
}

/** Convenience for tests / cold paths: prepare + search in one call. */
export function retrieve(units: AskUnit[], query: string, k = 6): Hit[] {
  return search(prepare(units), query, k);
}
