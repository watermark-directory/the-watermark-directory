import * as React from "react";

export interface EyebrowProps {
  children?: React.ReactNode;
  /** Ink color. @default "muted" */
  tone?: "muted" | "faint" | "forest" | "ink";
  /** Element to render. @default "div" */
  as?: keyof JSX.IntrinsicElements;
  style?: React.CSSProperties;
}

/** The mono uppercase part-label above headings and section starts — carries Watermark's documentary register. */
export function Eyebrow(props: EyebrowProps): JSX.Element;
