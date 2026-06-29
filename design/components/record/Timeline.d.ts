import * as React from "react";

export interface TimelineEvent {
  /** Year — used to auto-insert a year divider when it changes. */
  year: string;
  /** Display date, e.g. "2025-08-13" or "2026 · pending". */
  date: string;
  /** Event kind label, e.g. "deed", "air permit", "records request". */
  kind?: string;
  title: string;
  summary?: string;
  evidence?: "verified" | "inference" | "open";
  connect?: { kind: string; label: string; href?: string }[];
  /** Story chapter that tears this event down — renders an "↩ story Ch.N" badge. */
  seenInCh?: number | string;
  seenInHref?: string;
}

export interface TimelineProps {
  /** Chronological events. Year markers are inserted automatically on year change. */
  events?: TimelineEvent[];
  style?: React.CSSProperties;
}

/**
 * The record's chronology — an ink spine with square evidence-colored nodes and forest year diamonds.
 *
 * @startingPoint section="Record" subtitle="Provenance timeline with evidence nodes" viewport="640x560"
 */
export function Timeline(props: TimelineProps): JSX.Element;
