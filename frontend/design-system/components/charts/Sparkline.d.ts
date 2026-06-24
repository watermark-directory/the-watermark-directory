import * as React from "react";

export interface SparklineProps {
  /** The series values. */
  data: number[];
  /** Stroke color. @default forest (var(--data-1)) */
  color?: string;
  /** @default 120 */
  width?: number;
  /** @default 32 */
  height?: number;
  /** @default 2 */
  strokeWidth?: number;
  /** Draw the end dot. @default true */
  dot?: boolean;
  style?: React.CSSProperties;
}

/**
 * Sparkline — an axis-less trend sized to sit in a record row or stat strip,
 * next to its current figure.
 *
 * @startingPoint section="Charts" subtitle="inline trend" viewport="200x60"
 */
export function Sparkline(props: SparklineProps): JSX.Element;
