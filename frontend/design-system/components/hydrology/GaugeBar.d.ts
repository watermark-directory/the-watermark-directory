import * as React from "react";

export interface GaugeBarProps {
  /** The figure being gauged. */
  value: number;
  /** The permitted cap. */
  cap: number;
  /** Scale ceiling. Omit to derive from value + cap. */
  max?: number;
  /** Unit shown in the scale labels, e.g. "af". */
  unit?: string;
  /** Caption beside the big percentage. */
  label?: string;
  /** Fill color up to the cap. @default amber */
  fillColor?: string;
  /** Show the big percent-of-cap figure. @default true */
  showPercent?: boolean;
  style?: React.CSSProperties;
}

/**
 * GaugeBar — a single figure against a permitted cap, with the overage past the
 * cap mark in oxblood. The big percentage goes oxblood once the cap is exceeded.
 *
 * @startingPoint section="Hydrology" subtitle="% of cap" viewport="420x150"
 */
export function GaugeBar(props: GaugeBarProps): JSX.Element;
