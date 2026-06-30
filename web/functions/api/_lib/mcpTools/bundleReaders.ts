// Bundle reader MCP tool handlers (#914): get_timeline, get_entities,
// get_hypotheses, get_documents.
//
// Each handler fetches its feed from a root-absolute static JSON endpoint emitted at
// build time (src/pages/feeds/*.json.ts), so there is no database or model call —
// these are pure deterministic JSON readers. Tool descriptions embed the evidentiary
// contract: clients must cite sources and must not fabricate missing fields.

import { fetchWithTimeout } from "../http";

type McpContent = { type: "text"; text: string };

function feedUrl(name: string, requestUrl: string): string {
  return new URL(`/feeds/${name}.json`, requestUrl).toString();
}

async function fetchFeed<T>(name: string, requestUrl: string): Promise<T> {
  const res = await fetchWithTimeout(feedUrl(name, requestUrl));
  if (!res.ok) throw new Error(`feed ${name} returned ${res.status}`);
  return res.json() as Promise<T>;
}

// --- get_timeline ----------------------------------------------------------------

interface TimelineEntry {
  date: string;
  category: string;
  title: string;
  ref?: string;
  parties?: string[];
  detail?: string;
  source?: string;
  citation?: { verified?: boolean; confidence?: string; source_kind?: string; page?: number | null };
}

interface GetTimelineParams {
  since?: unknown;
  until?: unknown;
  category?: unknown;
}

export async function handleGetTimeline(params: unknown, requestUrl: string): Promise<McpContent[]> {
  const p = (params ?? {}) as GetTimelineParams;
  const since = typeof p.since === "string" ? p.since : null;
  const until = typeof p.until === "string" ? p.until : null;
  const category = typeof p.category === "string" && p.category ? p.category : null;

  let entries = await fetchFeed<TimelineEntry[]>("timeline", requestUrl);

  if (since) entries = entries.filter((e) => e.date >= since);
  if (until) entries = entries.filter((e) => e.date <= until);
  if (category) entries = entries.filter((e) => e.category === category);

  // Return ascending (oldest-first); clients may reverse as needed.
  entries = [...entries].sort((a, b) => a.date.localeCompare(b.date));

  return [{ type: "text", text: JSON.stringify(entries) }];
}

// --- get_entities ----------------------------------------------------------------

interface EntityNode {
  key: string;
  display: string;
  kind: string;
  classification?: string | null;
  variants?: string[];
  roles?: Record<string, number>;
  parcels?: string[];
  addresses?: string[];
  sources?: string[];
  signals?: string[];
}

interface GetEntitiesParams {
  type?: unknown;
}

export async function handleGetEntities(params: unknown, requestUrl: string): Promise<McpContent[]> {
  const p = (params ?? {}) as GetEntitiesParams;
  const typeFilter = typeof p.type === "string" && p.type ? p.type : null;

  let entities = await fetchFeed<EntityNode[]>("entities", requestUrl);

  if (typeFilter) {
    entities = entities.filter((e) => e.kind === typeFilter);
  }

  return [{ type: "text", text: JSON.stringify(entities) }];
}

// --- get_hypotheses --------------------------------------------------------------

interface HypothesisItem {
  id: string;
  number: string;
  name: string;
  claim: string;
  thesis: string;
  status: string;
  signals: string[];
  groups: string[];
}

interface HypothesisAssessmentItem {
  site: string;
  hypothesis: string;
  signal: string;
  tag: string;
  sub_thesis?: string | null;
  group?: string;
  fields?: Record<string, unknown>;
  citations?: unknown[];
}

interface HypothesesPayload {
  hypotheses: HypothesisItem[];
  assessments: HypothesisAssessmentItem[];
}

interface JoinedHypothesis extends HypothesisItem {
  assessments: HypothesisAssessmentItem[];
}

interface GetHypothesesParams {
  site?: unknown;
}

export async function handleGetHypotheses(params: unknown, requestUrl: string): Promise<McpContent[]> {
  const p = (params ?? {}) as GetHypothesesParams;
  const siteFilter = typeof p.site === "string" && p.site ? p.site : null;

  const payload = await fetchFeed<HypothesesPayload>("hypotheses", requestUrl);
  const { hypotheses, assessments } = payload;

  let filteredAssessments = assessments;
  if (siteFilter) {
    filteredAssessments = assessments.filter((a) => a.site === siteFilter);
  }

  const joined: JoinedHypothesis[] = hypotheses.map((h) => ({
    ...h,
    assessments: filteredAssessments.filter((a) => a.hypothesis === h.id),
  }));

  return [{ type: "text", text: JSON.stringify(joined) }];
}

// --- get_documents ---------------------------------------------------------------

interface DocumentEntry {
  rel: string;
  name: string;
  suffix: string;
  media_type: string;
  published: boolean;
  available: boolean;
}

interface DocumentCollectionItem {
  slug: string;
  title: string;
  description: string;
  entries: DocumentEntry[];
}

interface GetDocumentsParams {
  collection?: unknown;
}

export async function handleGetDocuments(params: unknown, requestUrl: string): Promise<McpContent[]> {
  const p = (params ?? {}) as GetDocumentsParams;
  const collectionFilter = typeof p.collection === "string" && p.collection ? p.collection : null;

  let collections = await fetchFeed<DocumentCollectionItem[]>("documents", requestUrl);

  if (collectionFilter) {
    collections = collections.filter((c) => c.slug === collectionFilter);
  }

  // Strip full entry details for brevity; return metadata only.
  const result = collections.map((c) => ({
    slug: c.slug,
    title: c.title,
    description: c.description,
    entry_count: c.entries.length,
    entries: c.entries.map((e) => ({
      rel: e.rel,
      name: e.name,
      media_type: e.media_type,
      published: e.published,
      available: e.available,
    })),
  }));

  return [{ type: "text", text: JSON.stringify(result) }];
}
