import * as React from "react";

export interface SourceCrop {
  src: string;                 // committed scan-crop image
  alt?: string;
  caption?: string;
  /** A precise redaction overlay drawn over the crop (CSS lengths). */
  redaction?: { label: string; x: string; y: string; w: string; h: string };
}
export interface SourceFacsimileField {
  label: string;
  value: React.ReactNode;
  warn?: boolean;              // oxblood — a blank / withheld figure
}

export interface SourceCardProps {
  /** Source filename shown in the header. */
  file?: string;
  /** Header badge — the source's render class ("SCAN" / "PDF" / "HTML"). Pass empty to hide. */
  badge?: string;
  /** Page range, e.g. "pp. 317–328". */
  pages?: string;
  /** Holding body, e.g. "Public Records Request 01". */
  collection?: string;
  /** A trailing note line under the card. */
  note?: string;
  /** Tier 1 — a committed scan crop of the real region (preferred preview). */
  crop?: SourceCrop;
  /** Tier 2 — embed the live source document (only when published). */
  embed?: boolean;
  /** Tier 3 — the real extraction rendered as a key/value facsimile. */
  fields?: SourceFacsimileField[];
  /** A catalogued source's full viewer page; linked when not embedded inline. */
  docHref?: string;
  /** A generic redaction bar drawn over a non-crop tier that still marks a gap. */
  redactionLabel?: string;
  /** Tier 4 fallback — call-to-action over the striped scan body. @default "View source on request" */
  action?: string;
  style?: React.CSSProperties;
}

/**
 * The record's source viewer — a four-tier preview (scan crop → live embed → extraction
 * facsimile → on-request fallback), with provenance shown, never hidden.
 *
 * @startingPoint section="Record" subtitle="Source viewer — scan crop / embed / facsimile / fallback" viewport="380x420"
 */
export function SourceCard(props: SourceCardProps): JSX.Element;
