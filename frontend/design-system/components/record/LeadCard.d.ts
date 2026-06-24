import * as React from "react";

export interface LeadCardProps {
  /** Lead type — shown as a mono tag. e.g. "Signal", "Open question", "Redaction", "Claim". */
  kind?: string;
  /** Confidence / standing of the lead. */
  confidence?: "low" | "unanswered" | "withheld" | "rumored";
  title?: string;
  detail?: string;
  /** Provenance / where it came from. */
  source?: string;
  /** Action label. @default "Help confirm" */
  action?: string;
  /** Secondary count, e.g. "3 on this". */
  count?: string;
  onAction?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

/**
 * An open, unverified thread — published for the public to corroborate, answer, or fill in.
 *
 * @startingPoint section="Record" subtitle="Open lead with confidence + call to action" viewport="420x220"
 */
export function LeadCard(props: LeadCardProps): JSX.Element;
