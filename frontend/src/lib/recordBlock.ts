/**
 * The Record Block (design "Record Block") — the library's per-record unit, one
 * family with the Record Teardown at reference density. This module is the data
 * shape the `RecordBlock.astro` component renders, plus a mapper from a live
 * `records`-feed row so the library and the walk read the same feed.
 */
import type { TagKind } from "./teardown";
import { evidenceKind, slugify, type RecordItem } from "./feeds";
import { fieldToString, groupLabel, isApproximate } from "./records";
import { walkAnchorFor } from "./walk";
import { withBase } from "./site";

export interface BlockField {
  label: string;
  value: string;
  warn?: boolean;
  tag?: TagKind;
}

export interface BlockSeenIn {
  ch: string;
  label: string;
  href: string;
}

export interface LibraryRecord {
  /** Anchor id (slug of the record `rel`) for deep links from the walk. */
  id: string;
  kind: string;
  title: string;
  recordId: string;
  evidence: TagKind;
  seenIn?: BlockSeenIn;
  /** Headline figure shown in compact density. */
  headlineValue?: string;
  headlineWarn?: boolean;
  fields: BlockField[];
  warnings: string[];
  source: { file: string; pages: string; collection: string };
  verify?: { label: string; href: string };
  correctHref?: string;
  /** Compact-density row link target. */
  href?: string;
}

/** The top-level collection of a `rel` (e.g. "permits/4132514.epa.yaml" → "permits"). */
function relCollection(rel: string): string {
  const i = rel.indexOf("/");
  return i > 0 ? rel.slice(0, i) : rel;
}

/** A short, human record id from the `rel` basename (without extensions). */
function relRecordId(rel: string): string {
  const base = rel.slice(rel.lastIndexOf("/") + 1);
  return base.replace(/\.[a-z0-9]+(\.[a-z0-9]+)?$/i, "");
}

/** Map a live `records`-feed row onto the Record Block shape. */
export function recordToBlock(r: RecordItem): LibraryRecord {
  const fields: BlockField[] = Object.entries(r.fields).map(([k, v]) => ({
    label: k,
    value: fieldToString(v),
    warn: isApproximate(r, k),
  }));
  const anchor = walkAnchorFor(r.rel);
  const c = r.citation;
  return {
    id: slugify(r.rel),
    kind: `Record · ${groupLabel(r.group).replace(/ —.*$/, "")}`,
    title: r.title,
    recordId: relRecordId(r.rel),
    evidence: evidenceKind(c),
    seenIn: anchor
      ? { ch: anchor.ch, label: anchor.label, href: withBase(`/walk/${anchor.slug}`) }
      : undefined,
    fields,
    warnings: r.warnings,
    source: {
      file: c.source ?? r.rel,
      pages: c.page ? `p.${c.page}` : "—",
      collection: relCollection(r.rel),
    },
    // The record's own screen (/site/records/<group>/<id>) — the compact row links
    // here; the full block ignores it (it IS the screen).
    href: withBase(`/site/records/${r.group}/${slugify(r.rel)}`),
    correctHref: withBase(
      `/submit?ref_kind=record&ref_id=${encodeURIComponent(r.rel)}&ref_label=${encodeURIComponent(r.title)}`,
    ),
  };
}
