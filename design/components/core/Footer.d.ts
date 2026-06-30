import * as React from "react";

export interface FooterNavLink {
  /** Display label. */
  label: string;
  /** Destination URL. Defaults to "#". */
  href?: string;
}

export interface FooterNavGroup {
  /** Column heading — rendered in mono uppercase. */
  heading: string;
  /** Links stacked vertically in this column. */
  links: FooterNavLink[];
}

export interface FooterProps {
  /**
   * Show the pre-launch notice band (Band 1).
   * Set false once the site is fully public.
   * @default true
   */
  prelaunch?: boolean;

  /**
   * Bold prefix in the notice — the alarming part.
   * @default "Pre-launch — this site isn't public yet."
   */
  noticePrefix?: string;

  /**
   * Body copy that follows the prefix.
   * @default "Every figure carries a source; inference is labeled; redactions are shown, not hidden. Nothing here is a verdict."
   */
  noticeBody?: string;

  /**
   * Nav link groups rendered as labeled columns in Band 2.
   * Defaults to three groups: The investigation · Resources · Site.
   */
  groups?: FooterNavGroup[];

  /**
   * Mono technical manifesto shown under the wordmark.
   * @default "static · no trackers · every page reads with JS off"
   */
  manifesto?: string;

  /** href for the "Submit a tip or correction" CTA button. */
  submitHref?: string;

  /** Click handler for the submit CTA (takes precedence over submitHref). */
  onSubmitTip?: (e: React.MouseEvent<HTMLAnchorElement>) => void;

  style?: React.CSSProperties;
}

/**
 * Site-wide footer. Two bands:
 * 1. **Notice band** — pre-launch disclosure, provenance-first chip, submit CTA.
 * 2. **Nav band** — left: w. mark + wordmark + manifesto. Right: grouped nav columns.
 *
 * Default groups: *The investigation* (Overview → The record) ·
 * *Resources* (Directory, Research, Docs, Wiki) ·
 * *Site* (Connect, Methodology, About).
 *
 * Background: `--bone-sunk`. No radius. Flat by doctrine.
 *
 * @startingPoint section="Core" subtitle="Notice + columnar nav · site-wide footer" viewport="1100x280"
 */
export function Footer(props: FooterProps): JSX.Element;
