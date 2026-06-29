import * as React from "react";

export interface CheckboxProps {
  checked?: boolean;
  onChange?: (next: boolean) => void;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

/** A flat square checkbox with inline label — checked is forest-filled with a bone check. */
export function Checkbox(props: CheckboxProps): JSX.Element;
