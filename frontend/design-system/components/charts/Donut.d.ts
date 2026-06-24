import * as React from "react";

export interface DonutDatum {
  label: string;
  value: number;
  /** Override the auto-assigned forest tint. */
  color?: string;
}

export interface DonutProps {
  data: DonutDatum[];
  /** Whole to divide by. Omit to sum the data. */
  total?: number;
  /** Diameter in px. @default 128 */
  size?: number;
  /** Big mono figure in the hole. Omit to show the total. */
  center?: React.ReactNode;
  /** Small caption under the center figure. @default "records" */
  centerSub?: string;
  /** Show the slice legend beside the ring. @default true */
  legend?: boolean;
  style?: React.CSSProperties;
}

/**
 * Donut — composition of a whole in forest tints, with the total set mono in
 * the center and an optional legend.
 *
 * @startingPoint section="Charts" subtitle="composition" viewport="360x180"
 */
export function Donut(props: DonutProps): JSX.Element;
