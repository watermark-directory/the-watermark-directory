import * as React from "react";

/** Every glyph in the Watermark icon family. */
export type IconName =
  // navigation & chrome
  | "search" | "menu" | "home" | "chevron" | "dropdown" | "arrow"
  | "verify-link" | "close" | "email" | "notify" | "locked" | "secure" | "ask"
  // records & sources
  | "document" | "scan" | "corpus" | "archive" | "citation" | "link" | "pages" | "repo"
  // entities & places
  | "entity" | "person" | "place" | "watershed" | "timeline" | "concept" | "map"
  // actions
  | "download" | "attach" | "send" | "correction" | "filter" | "copy" | "submit"
  // data & figures
  | "chart" | "trend" | "measure" | "cost" | "power" | "discharge"
  // evidence & provenance (semantic)
  | "verified" | "inference" | "open" | "scope-gap" | "excerpt" | "key-figure" | "redaction";

export interface IconProps {
  /** Which glyph to draw. */
  name?: IconName;
  /** Pixel size of the 24px-grid artboard. @default 24 */
  size?: number;
  /** Stroke weight (ignored for the two filled glyphs: repo, redaction). @default 1.7 */
  stroke?: number;
  /** Force a color. Omit to inherit `currentColor` (and, for semantic icons,
   *  their fixed evidence color). */
  color?: string;
  /** Force `currentColor` even for a semantic icon, ignoring its evidence color. @default false */
  inherit?: boolean;
  /** Accessible title; when set the icon is exposed as an image instead of decoration. */
  title?: string;
  style?: React.CSSProperties;
}

/** All available icon names, for pickers / iteration. */
export const ICON_NAMES: IconName[];

/**
 * Icon — the Watermark stroke family on a 24px grid (1.7 stroke, round cap/join,
 * currentColor). Semantic icons (verified, inference, open, scope-gap, key-figure)
 * carry the evidence palette by default; `repo` and `redaction` are filled.
 *
 * @startingPoint section="Core" subtitle="40+ glyphs · 24px grid · currentColor" viewport="760x200"
 */
export function Icon(props: IconProps): JSX.Element;
