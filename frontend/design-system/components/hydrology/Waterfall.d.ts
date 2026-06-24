import * as React from "react";

export interface WaterfallStep {
  label: string;
  value: number;
  /** "base" = full bar from zero · "down" / "up" = a delta from the running
   *  total · "result" = the net remainder from zero. */
  kind: "base" | "down" | "up" | "result";
  /** Override the tone (base=ink, down=forest, up/result=amber). */
  color?: string;
}

export interface WaterfallProps {
  steps: WaterfallStep[];
  /** Scale ceiling. Omit to derive from the steps. */
  max?: number;
  /** Unit appended in surrounding copy (not drawn on bars). */
  unit?: string;
  /** @default 200 */
  height?: number;
  style?: React.CSSProperties;
}

/**
 * Waterfall — a value drawn down step by step; reads as an equation
 * (intake − returned = consumed). Floating bars with dashed connectors.
 *
 * @startingPoint section="Hydrology" subtitle="net consumptive" viewport="420x260"
 */
export function Waterfall(props: WaterfallProps): JSX.Element;
