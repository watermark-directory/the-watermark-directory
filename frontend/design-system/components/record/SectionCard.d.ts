import * as React from "react";

export interface SectionCardProps {
  /** Mono badge code, e.g. "DOC", "REC", "TML", "ENT". */
  badge?: string;
  title?: string;
  /** Item count (open doors only). */
  count?: React.ReactNode;
  /** Locked doors are dashed and show lockNote instead of a count. @default false */
  locked?: boolean;
  /** Why it's locked / what unlocks it. */
  lockNote?: string;
  href?: string;
  style?: React.CSSProperties;
}

/** A browse "door" into a part of the record — open (count + Browse) or locked (dashed, with an unlock note). */
export function SectionCard(props: SectionCardProps): JSX.Element;
