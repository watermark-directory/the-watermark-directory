import * as React from "react";

export interface EvidenceTagProps {
  /** The standing of the figure this tag annotates.
   *  verified = cited source · inference = modeled/derived · open = unverified lead ·
   *  gap = scope gap / redaction (oxblood) · key = the highlighted load-bearing figure. */
  kind?: "verified" | "inference" | "open" | "gap" | "key";
  /** Override the default label text for this kind. */
  label?: string;
  /** Wrap the label in [square brackets] — the record-screen convention. @default false */
  brackets?: boolean;
  /** Show the leading status square. @default true */
  dot?: boolean;
  /** @default "md" */
  size?: "sm" | "md";
  style?: React.CSSProperties;
}

/**
 * The evidence pill — Watermark's core trust grammar. Sits beside any figure,
 * record, or lead to declare its standing.
 *
 * @startingPoint section="Core" subtitle="verified · inference · open · scope-gap · key" viewport="700x120"
 */
export function EvidenceTag(props: EvidenceTagProps): JSX.Element;
