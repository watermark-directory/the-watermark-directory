/**
 * The sequence-as-argument timeline spine (#225) — the walk's connective tissue.
 * Project BOSC's confidentiality went on *first*: the Mutual NDA was authorized
 * before the CRA abatement was voted, before the deeds were recorded — and the
 * public still could not name the customer from any of it. **The order is the
 * argument.**
 *
 * The three dated milestones are present-checked against the live `timeline` feed
 * (`inFeed`) so the spine and the library read the same events — no fork. The
 * fourth beat is the customer reveal, carried as an **annotation, not a node**
 * (discipline: Google stays an annotation): its name appears in none of these
 * records and surfaces only later, by accident.
 *
 * NOT client-safe (imports the node bundle loader); rendered SSR by
 * `WalkTimeline.astro`.
 */
import { hasFeed, loadFeed } from "./bundle";
import type { TimelineEntry } from "./feeds";

export type MilestoneKind = "confidential" | "approval" | "land" | "reveal";

export interface SpineMilestone {
  /** ISO date, or null for the undated reveal annotation. */
  date: string | null;
  label: string;
  detail: string;
  kind: MilestoneKind;
  cite: string;
  /** True when an event on this date is present in the live timeline feed. */
  inFeed: boolean;
}

export interface WalkSpine {
  milestones: SpineMilestone[];
  /** Total dated events in the feed the spine is drawn from (context). */
  totalEvents: number;
}

/** The curated confidentiality-first sequence (dates are the load-bearing facts). */
const SEQUENCE: Omit<SpineMilestone, "inFeed">[] = [
  {
    date: "2025-05-27",
    label: "Confidentiality goes on — Mutual NDA (Res #417-25)",
    detail:
      "The County authorizes a Mutual NDA with Bistrozzi (executed 2025-07-01) — a notify-and-minimize protocol agreed before any public-records request could be answered.",
    kind: "confidential",
    cite: "timeline · Res #417-25 (2025-05-27) · NDA executed 2025-07-01",
  },
  {
    date: "2025-07-10",
    label: "The public benefit is voted — CRA approved (Res #548-25)",
    detail:
      "The 75% / 15-year tax abatement is approved — first deliberated in a closed (G)(8) session on 2025-05-27, behind the NDA.",
    kind: "approval",
    cite: "timeline · Res #548-25 (2025-07-10)",
  },
  {
    date: "2025-08-13",
    label: "The land moves — deeds recorded → BISTROZZI LLC",
    detail:
      "Three Limited Warranty Deeds convey the assembled farms to a Delaware LLC — for “valuable consideration,” the price left blank on the DTE-100s.",
    kind: "land",
    cite: "timeline · deeds 202508130008300 / …312 / …316 (2025-08-13)",
  },
  {
    date: "2026-03-16",
    label: "Only now is the customer named — and only by the proponent",
    detail:
      "AEDG's own release names Google (and a Google official, Molly Kocour Boyle) as the entity behind Project BOSC — the first public confirmation, ~10 months after the NDA. The name appears in none of the deal records themselves; it had already slipped out by accident in a sibling Delaware filing. Held here as an annotation, not a node.",
    kind: "reveal",
    cite: "AEDG “Data Center Updates” release · 2026-03-16 · held as annotation, not a corpus node",
  },
];

export function buildWalkSpine(): WalkSpine {
  const events = hasFeed("timeline") ? loadFeed<TimelineEntry[]>("timeline") : [];
  const dates = new Set(events.map((e) => e.date));
  return {
    milestones: SEQUENCE.map((m) => ({ ...m, inFeed: m.date != null && dates.has(m.date) })),
    totalEvents: events.length,
  };
}
