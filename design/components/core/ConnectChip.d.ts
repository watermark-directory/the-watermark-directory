import * as React from "react";

export interface ConnectChipProps {
  /** The kind of thing linked — shown as a tiny mono prefix. */
  kind?: "entity" | "concept" | "timeline" | "place" | "person" | "map";
  /** Link text (the entity/concept name, e.g. "Tetra Tech" or "[[7Q10]]"). */
  children?: React.ReactNode;
  href?: string;
  /** forest (default) = on a record's "where it connects"; neutral = quieter contexts. */
  tone?: "forest" | "neutral";
  onClick?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

/** A "library door" chip — a typed link out to a connected entity, concept, timeline event, place, or map layer. */
export function ConnectChip(props: ConnectChipProps): JSX.Element;
