import * as React from "react";

export interface FlowDurationPoint {
  /** % of the year flow is equalled or exceeded (0–100). */
  exceedance: number;
  flow: number;
  unit?: string;
}
export interface FlowThreshold {
  value: number;
  label?: string;
  /** Defaults to amber (inference). Pass var(--ev-gap-fg) for a limit. */
  color?: string;
}

export interface FlowDurationCurveProps {
  /** Points sorted by ascending exceedance. */
  data: FlowDurationPoint[];
  /** Log-Y floor / ceiling. Omit to derive from the data. */
  yMin?: number;
  yMax?: number;
  /** Horizontal reference lines (draw, 7Q10, …). */
  thresholds?: FlowThreshold[];
  /** Shade the exceedance tail where flow drops below this value (oxblood). */
  shadeBelow?: number;
  /** Fill the forest tint under the curve. @default true */
  area?: boolean;
  /** @default 192 */
  height?: number;
  style?: React.CSSProperties;
}

/**
 * FlowDurationCurve — streamflow vs the share of the year it is equalled or
 * exceeded, on a log scale, with threshold lines and an optional shaded
 * low-flow tail. Hover a point for the readout.
 *
 * @startingPoint section="Hydrology" subtitle="exceedance · log" viewport="420x300"
 */
export function FlowDurationCurve(props: FlowDurationCurveProps): JSX.Element;
