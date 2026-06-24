import * as React from "react";

export interface StackSegment {
  value: number;
  label: string;
  /** Evidence palette kind — the usual choice for a status proportion. */
  kind?: "verified" | "inference" | "open" | "gap" | "key";
  /** Explicit color, overriding `kind` / the forest series. */
  color?: string;
}

export interface StackedBarProps {
  segments: StackSegment[];
  /** Whole to divide by. Omit to sum the segments. */
  total?: number;
  /** Bar height in px. @default 30 */
  height?: number;
  /** Show the legend row. @default true */
  legend?: boolean;
  /** Append "· NN%" to each legend entry. @default true */
  showPct?: boolean;
  style?: React.CSSProperties;
}

/**
 * StackedBar — a single proportion bar (e.g. evidence status across N records)
 * with an optional legend. Defaults segments to the evidence palette by `kind`.
 *
 * @startingPoint section="Charts" subtitle="proportion" viewport="460x110"
 */
export function StackedBar(props: StackedBarProps): JSX.Element;
