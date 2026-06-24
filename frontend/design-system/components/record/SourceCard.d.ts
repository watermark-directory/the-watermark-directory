import * as React from "react";

export interface SourceCardProps {
  /** Source filename shown in the header. */
  file?: string;
  /** Header badge — typically "SCAN" or "PDF". Pass empty to hide. */
  badge?: string;
  /** Page range, e.g. "pp. 317–328". */
  pages?: string;
  /** Holding body, e.g. "Public Records Request 01". */
  collection?: string;
  /** Call-to-action over the scan body. @default "View source on request" */
  action?: string;
  style?: React.CSSProperties;
}

/** The source-excerpt fallback card — stands in for a document scan with provenance, shown not hidden. */
export function SourceCard(props: SourceCardProps): JSX.Element;
