import * as React from "react";

export interface HydrographProps {
  /** "area" = one seasonal series · "bars" = monthly bars with deficit flag ·
   *  "envelope" = typical vs dry band. @default "area" */
  mode?: "area" | "bars" | "envelope";
  /** The series for "area" / "bars". */
  series?: number[];
  /** Upper line for "envelope". */
  typical?: number[];
  /** Lower / dry-year line for "envelope". */
  dry?: number[];
  /** Month (or period) labels. @default J…D */
  labels?: string[];
  /** Dashed reference line (e.g. the plant's draw). In "bars" mode, months
   *  below this turn oxblood. */
  drawLine?: number;
  /** Scale ceiling. Omit to derive from the data. */
  max?: number;
  /** √-scale the Y axis so a low trough still reads. @default true */
  sqrt?: boolean;
  /** @default 196 */
  height?: number;
  style?: React.CSSProperties;
}

/**
 * Hydrograph — flow across the year in three modes (area · bars · envelope),
 * all √-scaled by default. Bars flag deficit months below the draw; envelope
 * is hoverable.
 *
 * @startingPoint section="Hydrology" subtitle="area · bars · envelope" viewport="420x280"
 */
export function Hydrograph(props: HydrographProps): JSX.Element;
