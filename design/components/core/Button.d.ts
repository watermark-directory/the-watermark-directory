import * as React from "react";

export interface ButtonProps {
  /** Visual weight. `solid` = ink fill (primary), `forest` = the signal-green fill,
   *  `ghost` = ink outline, `link` = inline forest text link. @default "solid" */
  variant?: "solid" | "forest" | "ghost" | "link";
  /** @default "md" */
  size?: "sm" | "md" | "lg";
  /** Render as an anchor instead of a button. */
  href?: string;
  /** Leading icon node (a 24px-grid stroke SVG, inherits currentColor). */
  icon?: React.ReactNode;
  /** Trailing icon node — commonly an arrow → or verify ↗. */
  iconRight?: React.ReactNode;
  disabled?: boolean;
  onClick?: (e: React.MouseEvent) => void;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * The flat, square-cornered Watermark action button.
 *
 * @startingPoint section="Core" subtitle="Solid · forest · ghost · link actions" viewport="700x180"
 */
export function Button(props: ButtonProps): JSX.Element;
