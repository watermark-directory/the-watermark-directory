import * as React from "react";

export interface LinePoint {
  label?: string;
  value: number;
}

export interface LineChartProps {
  data: LinePoint[];
  /** Scale ceiling. Omit to derive from the data. */
  max?: number;
  /** Fill the forest-tint area under the line. @default true */
  area?: boolean;
  /** SVG height in px. @default 200 */
  height?: number;
  /** Emphasized inline figure drawn at the last point, e.g. "340.2 ac". */
  lastLabel?: string;
  style?: React.CSSProperties;
}

/**
 * LineChart — a time series with optional forest-tint area and an emphasized
 * last point. Mono axis ticks, light grid, no chrome.
 *
 * @startingPoint section="Charts" subtitle="time series · area" viewport="420x240"
 */
export function LineChart(props: LineChartProps): JSX.Element;
