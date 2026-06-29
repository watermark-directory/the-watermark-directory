import * as React from "react";

export interface ThresholdPoint {
  label: string;
  value: number;
}

export interface ThresholdLineProps {
  data: ThresholdPoint[];
  /** The horizontal limit (permit cap, draw). */
  limit: number;
  /** Label drawn at the limit line. @default "cap" */
  limitLabel?: string;
  /** Scale ceiling. Omit to derive from the data + limit. */
  max?: number;
  /** Unit shown in the hover readout. */
  unit?: string;
  /** Fill the forest tint under the line. @default false */
  area?: boolean;
  /** Custom Y-tick formatter. */
  yTickFormat?: (v: number) => string;
  /** @default 196 */
  height?: number;
  style?: React.CSSProperties;
}

/**
 * ThresholdLine — a cumulative / time series against a horizontal limit. Marks
 * the crossing point and shades the overage above the limit in oxblood. Hover
 * a point for the value and its share of the limit.
 *
 * @startingPoint section="Hydrology" subtitle="cumulative vs cap" viewport="420x260"
 */
export function ThresholdLine(props: ThresholdLineProps): JSX.Element;
