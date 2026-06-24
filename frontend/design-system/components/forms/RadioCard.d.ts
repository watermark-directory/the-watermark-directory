import * as React from "react";

export interface RadioCardProps {
  title?: string;
  desc?: string;
  selected?: boolean;
  onSelect?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

/** A selectable option card (the lead-type picker) — square radio dot, title, one-line description; selected goes forest. */
export function RadioCard(props: RadioCardProps): JSX.Element;
