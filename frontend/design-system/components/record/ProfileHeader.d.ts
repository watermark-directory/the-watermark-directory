import * as React from "react";

export interface ProfileStat {
  label: string;
  value: React.ReactNode;
  evidence?: "verified" | "inference" | "open";
  sub?: string;
  warn?: boolean;
}
export interface ProfileAttr {
  label: string;
  value: React.ReactNode;
  tag?: "verified" | "inference" | "open";
}
export interface ProfileSeenIn {
  href: string;                // link into the story chapter
  ch: number | string;         // chapter number / label
  label: string;               // the chapter title
}
export interface Profile {
  kindLabel?: string;          // "Entity · shell company"
  name?: string;
  variants?: string[];         // aliases / registration codes
  descriptor?: string;
  evidence?: "verified" | "inference" | "open";
  graphHref?: string;          // when set, renders "◉ View in graph" → the entity graph
  seenIn?: ProfileSeenIn;      // "↩ seen in the story" backlink to the teardown chapter
  stats?: ProfileStat[];
  attrs?: ProfileAttr[];
  relLabel?: string;
  relationships?: { kind: string; label: string; href?: string }[];
  correctHref?: string;        // when set, renders "✎ Suggest a correction"
}

export interface ProfileHeaderProps {
  profile?: Profile;
  style?: React.CSSProperties;
}

/**
 * The wiki identity card for an entity, person, or place — rail, name, evidence, stat strip, attributes, graph row.
 *
 * @startingPoint section="Record" subtitle="Wiki profile header for an entity / person / place" viewport="700x420"
 */
export function ProfileHeader(props: ProfileHeaderProps): JSX.Element;
