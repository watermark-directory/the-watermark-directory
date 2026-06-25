import * as React from "react";

export interface RecordField {
  label: string;
  value: React.ReactNode;
  /** Tag this field's value with an evidence pill. */
  tag?: "verified" | "inference" | "open";
  /** Render the value oxblood (a blank / withheld figure). */
  warn?: boolean;
}

export interface LibraryRecord {
  kind?: string;            // "Record · deed"
  title?: string;
  recordId?: string;        // "instr. 202508130008300"
  evidence?: "verified" | "inference" | "open";
  seenIn?: RecordSeenIn;    // "↩ seen in the story" backlink (full) / "↩ story Ch.N" badge (compact)
  headlineValue?: string;   // compact density only
  headlineWarn?: boolean;
  fields?: RecordField[];
  nested?: NestedField[];   // structured fields rendered as a recursive key/value tree
  warnings?: string[];
  source?: { file: string; pages: string; collection: string };
  verify?: { href: string; label: string };  // structured verify link (was a bare label)
  correctHref?: string;     // when set, renders "✎ Suggest a correction"
  connect?: { kind: string; label: string; href?: string }[];
  href?: string;            // compact density only
}

export interface RecordSeenIn {
  href: string;             // link into the story chapter
  ch: number | string;      // chapter number / label
  label: string;            // the chapter title
}
/** A structured (object/array) field — rendered as a key/value tree; `~` leaves render oxblood. */
export interface NestedField {
  label: string;
  value: unknown;           // object | array | scalar
}

export interface RecordBlockProps {
  /** full = reference density · compact = list row. @default "full" */
  density?: "full" | "compact";
  record?: LibraryRecord;
  style?: React.CSSProperties;
}

/**
 * The canonical record card — a documented fact with its fields, gaps, provenance, and connections.
 *
 * @startingPoint section="Record" subtitle="Full record card with provenance & connections" viewport="700x520"
 */
export function RecordBlock(props: RecordBlockProps): JSX.Element;
