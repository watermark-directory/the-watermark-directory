/**
 * The Record Teardown — the guided walk's signature teaching component
 * (design handoff: "The Record Teardown"). A teardown is a *curated framing* of
 * one corpus record: pick a record, write three sentences. The structured
 * fields still come from the same feeds the library reads — the data never
 * forks. This module is the editorial shape the `<RecordTeardown>` component
 * renders; it mirrors the design's `RecordRow`.
 */

/** Maps onto the existing three evidence kinds (EvidenceTag). The design's
 *  `derived → inference` and `live → verified` collapse into these. */
export type TagKind = "verified" | "inference" | "open";

export type TeardownLayout = "split" | "scroll" | "annotated";

export interface TeardownSource {
  /** Source filename, shown in the document chrome. */
  file: string;
  /** Page / clause locator, e.g. "pp. 317–328" or "§5.5 · §9.13". */
  pages: string;
  /** Collection the source lives in. */
  collection: string;
  /** Character of the source, e.g. "Scanned PDF · degraded OCR". */
  kind: string;
  /** One line on why the binary isn't shown (the cloud deploy skips LFS). */
  note: string;
  /** Top-right marker on the source card (default "SCAN"). */
  badge?: string;
  /** Optional real link to the materialized exhibit/source. */
  href?: string;
}

export interface TeardownRow {
  label: string;
  value: string;
  /** Render the value as a scope-gap / approximate flag (red). */
  warn?: boolean;
}

export interface TeardownPin {
  n: number;
  label: string;
  value: string;
  /** Scope gap / redaction — renders red instead of indigo. */
  danger?: boolean;
  /** CSS offset over the artifact, e.g. "44px". */
  x: string;
  y: string;
}

export interface TeardownReveal {
  /** Prose before the load-bearing figure. */
  lead: string;
  /** The highlighted load-bearing figure. */
  key: string;
  /** Prose after the figure. */
  tail: string;
}

export interface TeardownCheck {
  tag: TagKind;
  /** Short qualifier on the tag, e.g. "totals" / "executed text". */
  sub: string;
  verify: string;
  verifyHref?: string;
  method: string;
  methodHref?: string;
}

export interface TeardownConnect {
  /** Library door type, e.g. "entity" / "timeline" / "concept" / "map". */
  kind: string;
  label: string;
  href?: string;
}

export interface TeardownRecord {
  title: string;
  docName: string;
  source: TeardownSource;
  extraction: TeardownRow[];
  /** Numbered annotations for the `annotated` layout. */
  pins?: TeardownPin[];
  reveal: TeardownReveal;
  check: TeardownCheck;
  connect: TeardownConnect[];
  /** Renders a redaction bar on the artifact (the `annotated` layout). */
  redactionLabel?: string;
  /**
   * `rel` of the backing row in the live `records` feed (e.g.
   * "recorder/202508130008300.deed.yaml"). When that row is present in the bundle
   * being built, the teardown's `verify` deep-links to the exact record and the
   * source card confirms the bundle's own citation — the data never forks. Absent
   * from the bundle (e.g. the minimal CI fixture) → graceful fallback to the
   * curated link. See `resolveTeardown`.
   */
  recordRel?: string;
  /**
   * Slug of the backing page in the legal-history collection (`lib/legal.ts`),
   * for teardowns whose anchor is an agreement/analysis rather than a `records`
   * row. Deep-links `verify` to `/site/legal/<slug>` when that page exists.
   */
  legalSlug?: string;
}
