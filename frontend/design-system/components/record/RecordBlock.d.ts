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
  headlineValue?: string;   // compact density only
  headlineWarn?: boolean;
  fields?: RecordField[];
  warnings?: string[];
  source?: { file: string; pages: string; collection: string };
  verify?: string;          // verify-link label
  connect?: { kind: string; label: string }[];
  href?: string;            // compact density only
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
