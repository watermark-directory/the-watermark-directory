import * as React from "react";

export interface FigureStatProps {
  /** lg = standalone tile (dashboard/hub) · sm = inline profile stat. @default "lg" */
  size?: "lg" | "sm";
  /** Uppercase label above the value. */
  label?: string;
  /** The figure itself — rendered in mono. e.g. "$14,223,081" or "24.3×". */
  value?: React.ReactNode;
  /** Unit / qualifier shown after the value (lg only). */
  unit?: string;
  /** Evidence standing of the figure. @default "verified" */
  evidence?: "verified" | "inference" | "open";
  /** Optional second qualifier: how the figure was arrived at. */
  basis?: "grounded" | "modeled";
  /** Mono sub-line (the formula / breakdown). */
  sub?: string;
  /** Provenance source line (lg only). */
  source?: string;
  /** Turn the value oxblood — a figure the record was made thin to hide. @default false */
  warn?: boolean;
  style?: React.CSSProperties;
}

/**
 * A load-bearing number with its evidence standing — the unit of the record's figures.
 *
 * @startingPoint section="Record" subtitle="Figure tile with evidence + provenance" viewport="320x180"
 */
export function FigureStat(props: FigureStatProps): JSX.Element;
