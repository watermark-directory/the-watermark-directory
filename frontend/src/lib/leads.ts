/**
 * Open leads (design "Site Leads") — every gap we're chasing on the Lima site, in the open.
 *
 * PROVENANCE DISCIPLINE. Unlike the design comp's illustrative leads, every entry here
 * traces to a real, committed source: the corpus-completeness audit's owed/withheld/`[open]`
 * items (`data/extracted/legal/corpus-completeness-audit.md`) and the boom-origin hypotheses'
 * open threads (`bosc.hypotheses`). A lead is *unverified inference until a source corroborates
 * it* — so each carries an evidence `tag` (`open` = a documented gap; `inference` = a labeled
 * reading), and the `source` names where the gap is recorded. We deliberately DROP the comp's
 * fabricated contributor avatars and "updated 2h ago" timestamps — there is no real feed for
 * those, and inventing them is exactly the fabrication this repo forbids.
 *
 * This is a curated TS data module in the same spirit as `narrative.ts` / `walk.ts` /
 * `teardowns.ts`; when a structured leads feed lands in the bundle, the board reads that instead.
 */

/** The four lead kinds — the rail colour + the call-to-action verb come from `KIND_META`. */
export type LeadKind = "signal" | "question" | "redaction" | "claim";
/** Lead status — drives the chip; maps onto the repo's evidence palette. */
export type LeadStatus = "low" | "unanswered" | "withheld" | "review";
/** Evidence tag — the repo's tag vocabulary (`[open]` gap vs. `[inference]` reading). */
export type LeadTag = "open" | "inference";

export interface Lead {
  /** Stable local id; mirrors the PRR item / source where apt (shown mono, like the comp). */
  id: string;
  kind: LeadKind;
  status: LeadStatus;
  tag: LeadTag;
  title: string;
  detail: string;
  /** The real citation — where this gap is recorded. */
  source: string;
  /** A linked GitHub tracking issue (goedelsoup/network/american-sugar-creek-allen-co), when one exists. */
  issue?: number;
  /** A short standing note (the comp's "3 working on this" slot), used sparingly + truthfully. */
  note?: string;
}

/** Presentation vocab per kind: the board label, the CTA verb, a CSS modifier key. */
export const KIND_META: Record<LeadKind, { label: string; action: string; mod: string }> = {
  signal: { label: "Signal", action: "Help confirm", mod: "signal" },
  question: { label: "Open question", action: "Answer this", mod: "question" },
  redaction: { label: "Redaction", action: "Fill the gap", mod: "redaction" },
  claim: { label: "Claim", action: "Corroborate", mod: "claim" },
};

/** Presentation vocab per status: the chip label + a CSS modifier key. */
export const STATUS_META: Record<LeadStatus, { label: string; mod: string }> = {
  low: { label: "Low confidence", mod: "low" },
  unanswered: { label: "Unanswered", mod: "unanswered" },
  withheld: { label: "Withheld", mod: "withheld" },
  review: { label: "Under review", mod: "review" },
};

/** The board filters, in order (All first). */
export const LEAD_FILTERS: { key: "all" | LeadKind; label: string }[] = [
  { key: "all", label: "All" },
  { key: "signal", label: "Signals" },
  { key: "question", label: "Questions" },
  { key: "redaction", label: "Redactions" },
  { key: "claim", label: "Claims" },
];

export const LEADS: Lead[] = [
  {
    id: "PRR-04",
    kind: "redaction",
    status: "withheld",
    tag: "open",
    title: "The project's cost-benefit analysis is withheld",
    detail:
      "Item 4 of the BOSC public-records request — the projected tax-revenue impact and public-ROI inputs and assumptions — is held by county legal counsel under R.C. 149.43 and the §9.66(D) data-center exemption. Not produced.",
    source: "Allen County PRR · item 4",
    note: "the one to watch",
  },
  {
    id: "PTI-313MW",
    kind: "redaction",
    status: "withheld",
    tag: "open",
    title: "The per-engine output behind the 313 MW figure is trade-secret-redacted",
    detail:
      "The final air permit-to-install (eDoc 4132514, 2026-05-28) confirms the generator count and three-hall emission-unit grouping on a primary footing, but the per-engine ekW behind the disclosed 313 MW is redacted as trade secret.",
    source: "OEPA PTI · eDoc 4132514",
  },
  {
    id: "ASWCD-PLANS",
    kind: "redaction",
    status: "withheld",
    tag: "open",
    title: "The site plan sets are withheld twice over",
    detail:
      "The County withholds the BOSC-1A plan sets; the Soil & Water district shields the same documents again under R.C. 149.433 (infrastructure records) and R.C. 1333.61 (trade secret — “water and wastewater usage for a data center”), a ground that reaches even the plan-share links inside produced emails.",
    source: "Allen SWCD · §149.433 / §1333.61",
  },
  {
    id: "PRR-16",
    kind: "redaction",
    status: "withheld",
    tag: "open",
    title: "The county website's edit history is disclaimed, not absent",
    detail:
      "Item 16 (the CMS audit trail for the Sanitary Engineering pages) was answered “no records — we don't manage the website,” yet the WordPress /revisions endpoint returns HTTP 401 (gated, not 404). The version history exists; custody sits with the host.",
    source: "Allen County PRR · item 16 · contested",
  },
  {
    id: "ASWCD-03",
    kind: "question",
    status: "review",
    tag: "open",
    title: "Wetland determination: “no records” — but a produced inspection says otherwise",
    detail:
      "The SWCD answered “no records” for the 0.7-acre forested wetland (DSW401251760W), yet a produced site inspection records that “the existing wetland was mitigated.” A produced record contradicts the answer.",
    source: "Allen SWCD · item 3",
  },
  {
    id: "ASWCD-04",
    kind: "question",
    status: "review",
    tag: "open",
    title: "Farm-tile drainage impact: “no records” — yet a failure is photographed",
    detail:
      "The SWCD answered “no records” on tile / agricultural-drainage impact, but the 2026-06-05 inspection documents an east farm-tile diversion-swale failure (photo captioned “East farm tile bypass”).",
    source: "Allen SWCD · item 4",
  },
  {
    id: "FORCEMAIN-MGD",
    kind: "question",
    status: "unanswered",
    tag: "open",
    title: "Nobody owns the forcemain's MGD design capacity",
    detail:
      "The Hume / Shawnee forcemain's design capacity (item 9) is disclaimed by every county body — each points to Ohio EPA or the townships. Batch 2 produced the financing and the engineering contract, not the MGD figure.",
    source: "Cross-production referral · item 9",
  },
  {
    id: "CORRIDOR-NPDES",
    kind: "signal",
    status: "low",
    tag: "open",
    title: "The corridor environmental permits are owned by no county body",
    detail:
      "The NPDES construction-stormwater / SWPPP / ESC records for the forcemain corridors and Shawnee II Phase 2 sit with no county custodian — each “no records” answer refers onward to Ohio EPA or the townships, who were not yet a requested custodian.",
    source: "Cross-production referral map",
    issue: 151,
  },
  {
    id: "PRR-02",
    kind: "question",
    status: "unanswered",
    tag: "open",
    title: "County ⇄ DoD / federal-contractor comms — narrowed to nothing",
    detail:
      "Item 2 sought County communications with DoD or federal contractors (GDIT, GDLS) about the American Township facility and corridor. The county narrowed the ask and returned “no records.”",
    source: "Allen County PRR · item 2 · narrowed",
  },
  {
    id: "PRR-19",
    kind: "question",
    status: "unanswered",
    tag: "open",
    title: "County ⇄ engineer-of-record (EMH&T) comms not produced",
    detail:
      "Item 19 sought County communications with EMH&T. None produced as to the Commissioners; the SWCD produced its own EMH&T emails, but the County's are still owed (it may supplement from Sanitary Engineering).",
    source: "Allen County PRR · item 19 · owed",
  },
  {
    id: "GLRI-INSTRUMENT",
    kind: "question",
    status: "unanswered",
    tag: "open",
    title: "The grant instrument behind the $650k Lost Creek project",
    detail:
      "The funding source is verified — a GLRI subaward through Ohio EPA, OSU portion $327,450, term 2023–2025 — but the signed award instrument (deliverables, match, reporting) on the Maumee-headwater ag-runoff project is still owed.",
    source: "Ohio EPA GLRI subaward files · owed",
  },
  {
    id: "OSU-MONITORING",
    kind: "signal",
    status: "low",
    tag: "open",
    title: "The OSU monitoring data quantifying the Maumee-headwater load",
    detail:
      "Continuous flow and water-quality from three ISCO6712 sites would quantify the actual nutrient / flow reduction on Lost Creek (HUC12 041000070305). The load-reduction table is referenced on the captured SWCD page but not transcribed.",
    source: "Allen SWCD capture · untranscribed",
  },
  {
    id: "H2-AUTH",
    kind: "question",
    status: "unanswered",
    tag: "inference",
    title: "The campus's federal authorization posture is undisclosed",
    detail:
      "The Joint Systems Manufacturing Center (Lima Army Tank Plant) is co-located with the campus — documented geography under hypothesis H2 — but the campus's authorization posture (FedRAMP / DoD impact level) is undisclosed, so the causal link to the boom remains an inference.",
    source: "Hypothesis H2 · defense nexus",
  },
  {
    id: "H1-DRAW",
    kind: "claim",
    status: "low",
    tag: "inference",
    title: "The consumptive cooling draw against the river's cited 7Q10",
    detail:
      "The Ottawa's design low flow is about 0.2 cfs (cited); the campus's consumptive cooling loss is the keystone of hypothesis H1. The measured draw against that 7Q10 is predicted evidence the record still needs to close end to end.",
    source: "Hypothesis H1 · water & power",
  },
];

/** Recently closed — real corpus closures (the comp's "Recently closed" rail). */
export interface ClosedLead {
  title: string;
  meta: string;
}

export const RECENTLY_CLOSED: ClosedLead[] = [
  {
    title: "NPDES construction-stormwater coverage located — 2GC08468*AG, effective 2025-11-10",
    meta: "closes #143 + #154 · sourced 2026-06-16",
  },
  {
    title: "County wastewater universe (PRR items 5–15) produced",
    meta: "PRR batch 2 · sourced 2026-06-12",
  },
  {
    title: "GLRI funding source resolved — OSU $327,450, 2023–2025",
    meta: "Shedekar CV · sourced 2026-06-06",
  },
];

/** How a lead closes — the real lead lifecycle (mirrors the submissions seam, not a verdict). */
export const LEAD_LIFECYCLE: { num: string; title: string; desc: string }[] = [
  {
    num: "1",
    title: "Logged as open",
    desc: "It joins this queue immediately, labeled as unverified inference.",
  },
  { num: "2", title: "Picked up", desc: "Contributors gather sources; the record team reviews them." },
  {
    num: "3",
    title: "Corroborated",
    desc: "If a source checks out, the lead enters the record with its citation.",
  },
  { num: "✓", title: "The bar moves", desc: "A closed lead nudges the site up the completeness curve." },
];

/** Board summary stats — all derived from the real leads, not invented. */
export function leadStats(): { n: number; label: string; mod: string }[] {
  const withheld = LEADS.filter((l) => l.status === "withheld").length;
  const review = LEADS.filter((l) => l.status === "review").length;
  return [
    { n: LEADS.length, label: "open leads", mod: "inference" },
    { n: withheld, label: "withheld / sealed", mod: "open" },
    { n: review, label: "under review", mod: "inference" },
    { n: RECENTLY_CLOSED.length, label: "closed recently", mod: "verified" },
  ];
}

/** Count of leads in a filter bucket (`all` = every lead). */
export function leadCount(key: "all" | LeadKind): number {
  return key === "all" ? LEADS.length : LEADS.filter((l) => l.kind === key).length;
}
