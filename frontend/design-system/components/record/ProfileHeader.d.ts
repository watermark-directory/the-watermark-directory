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
export interface Profile {
  kindLabel?: string;          // "Entity · shell company"
  name?: string;
  variants?: string[];         // aliases / registration codes
  descriptor?: string;
  evidence?: "verified" | "inference" | "open";
  graph?: boolean;             // show "View in graph"
  stats?: ProfileStat[];
  attrs?: ProfileAttr[];
  relLabel?: string;
  relationships?: { kind: string; label: string }[];
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
