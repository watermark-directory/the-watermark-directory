import * as React from "react";

export interface BarDatum {
  label: string;
  value: number;
  /** Make this the load-bearing bar (filled forest, bold value). */
  highlight?: boolean;
  /** Draw as a withheld / secondary value (faint forest fill + border). */
  muted?: boolean;
}

export interface BarChartProps {
  data: BarDatum[];
  /** Scale ceiling. Omit to derive from the data. */
  max?: number;
  /** "vertical" = categorical columns · "horizontal" = ranked rows. @default "vertical" */
  orientation?: "vertical" | "horizontal";
  /** SVG height in px (vertical only really uses it). @default 200 */
  height?: number;
  /** Appended after each value label, e.g. "ac". */
  unit?: string;
  /** Show the per-bar value labels. @default true */
  valueLabels?: boolean;
  style?: React.CSSProperties;
}

/**
 * BarChart — categorical or ranked bars in the Watermark grammar: forest
 * series, mono figures, light grid, no chrome.
 *
 * @startingPoint section="Charts" subtitle="categorical · ranked" viewport="420x260"
 */
export function BarChart(props: BarChartProps): JSX.Element;
