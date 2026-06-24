import * as React from "react";

export interface AnnotationPinProps {
  /** The pin number (or short label). */
  n?: React.ReactNode;
  /** forest = a read / annotation step · oxblood = a scope gap or redaction · muted. */
  tone?: "forest" | "oxblood" | "muted";
  /** Pixel size of the square. @default 28 */
  size?: number;
  /** Show the active outline ring. @default false */
  active?: boolean;
  onClick?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

/** A numbered square pin for the guided walk and document-scan annotations. Forest reads; oxblood flags gaps. */
export function AnnotationPin(props: AnnotationPinProps): JSX.Element;
