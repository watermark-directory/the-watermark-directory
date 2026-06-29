import * as React from "react";

export interface LinePoint {
  label?: string;
  value: number;
}

/** A dashed horizontal threshold line (a draw / limit / level) drawn across the plot. */
export interface RefLine {
  /** Where to draw it, in the data's units; clamped to the scale ceiling. */
  value: number;
  /** Right-aligned label above the line. */
  label?: string;
  /** Line color. @default oxblood (var(--ev-gap-fg)) — the limit/threshold red. */
  color?: string;
  /** SVG dash pattern. @default "5 3" */
  dash?: string;
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
  /** Dashed horizontal threshold lines — a disclosed cap, a design low flow, a target. */
  refs?: RefLine[];
  style?: React.CSSProperties;
}

/**
 * LineChart — a time series with optional forest-tint area and an emphasized
 * last point. Mono axis ticks, light grid, no chrome.
 *
 * @startingPoint section="Charts" subtitle="time series · area" viewport="420x240"
 */
export function LineChart(props: LineChartProps): JSX.Element;
