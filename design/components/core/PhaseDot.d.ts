import * as React from "react";

export interface PhaseDotProps {
  /** Build phase of a site. live = forest · building = ink · queued = muted · tracking = faint. */
  phase?: "live" | "building" | "queued" | "tracking";
  /** Override the default label. */
  label?: string;
  /** @default "md" */
  size?: "sm" | "md";
  style?: React.CSSProperties;
}

/** Build-phase marker — a square status dot + mono uppercase label, used in the directory table and chrome. */
export function PhaseDot(props: PhaseDotProps): JSX.Element;
