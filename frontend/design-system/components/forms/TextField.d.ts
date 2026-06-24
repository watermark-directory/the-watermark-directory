import * as React from "react";

export interface TextFieldProps {
  /** Mono uppercase micro-label above the field. */
  label?: string;
  /** Helper text below the field. */
  hint?: React.ReactNode;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  /** Render a textarea instead of an input. @default false */
  multiline?: boolean;
  /** Textarea rows. @default 4 */
  rows?: number;
  /** Appends a muted "— optional" qualifier to the label. */
  optional?: string;
  /** Leading icon node. */
  icon?: React.ReactNode;
  style?: React.CSSProperties;
}

/** A flat, square text input / textarea — hairline border, bone fill, forest focus ring. */
export function TextField(props: TextFieldProps): JSX.Element;
