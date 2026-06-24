import * as React from "react";

export interface BulletRow {
  label: string;
  /** Typed evidence register — declares the row's standing and colors the note
   *  from the matching evidence palette (preferred over the raw note/noteColor). */
  evidence?: "verified" | "inference" | "open" | "gap" | "key";
  /** Note shown beside the evidence kind, e.g. "USGS" → "[verified] · USGS". */
  evidenceNote?: string;
  /** Raw evidence note under the label (fallback when `evidence` is unset), e.g. "[verified] · USGS". */
  note?: string;
  /** Color of the raw note text (e.g. var(--ev-inference-fg)). */
  noteColor?: string;
  value: number;
  /** Bar fill. @default forest (var(--data-1)) */
  color?: string;
  /** Optional oxblood limit marker, in the same units as `value`. */
  marker?: number;
}

export interface BulletBarProps {
  rows: BulletRow[];
  /** Shared scale ceiling across all rows. @default 100 */
  max?: number;
  /** Unit appended to each value, e.g. "cfs". */
  unit?: string;
  style?: React.CSSProperties;
}

/**
 * BulletBar — a measure against a limit; the oxblood marker is the available
 * threshold and the comparison is the whole story.
 *
 * @startingPoint section="Charts" subtitle="measure vs limit" viewport="520x140"
 */
export function BulletBar(props: BulletBarProps): JSX.Element;
