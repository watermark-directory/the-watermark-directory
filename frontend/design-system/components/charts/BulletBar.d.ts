import * as React from "react";

export interface BulletRow {
  label: string;
  /** Small evidence note under the label, e.g. "[verified] · USGS". */
  note?: string;
  /** Color of the note text (e.g. var(--ev-inference-fg)). */
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
