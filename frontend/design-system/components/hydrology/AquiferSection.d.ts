import * as React from "react";

export interface AquiferWell {
  /** Horizontal position across the section, 0 (left) – 1 (right). */
  x: number;
  /** Casing depth as a fraction of the aquifer thickness. @default 0.4 */
  depthFrac?: number;
  label?: string;
}

export interface AquiferSectionProps {
  /** Drawdown at the pumping well, in feet — drives the cone depth. @default 42 */
  drawdownFt?: number;
  /** Override the drawdown dimension label. @default `${drawdownFt} ft` */
  drawdownLabel?: string;
  /** @default "pumping well" */
  wellLabel?: string;
  /** @default "static water level" */
  staticLabel?: string;
  /** @default "ground surface" */
  surfaceLabel?: string;
  /** Domestic wells sitting inside the cone. */
  wells?: AquiferWell[];
  /** @default 200 */
  height?: number;
  style?: React.CSSProperties;
}

/**
 * AquiferSection — the cone of depression in cross-section: forest dashed rest
 * level, amber drawn-down surface, an ink pumping-well casing, and the drawdown
 * dimension. The signature groundwater schematic.
 *
 * @startingPoint section="Hydrology" subtitle="cone of depression" viewport="420x240"
 */
export function AquiferSection(props: AquiferSectionProps): JSX.Element;
