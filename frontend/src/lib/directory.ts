/**
 * The directory's three-lens model (#308 "Directory" dictate) — one network, read three ways.
 *
 * The `/directory` index reorganizes the SAME 32 sites around one of three hypotheses:
 *   H1 water — where compute meets the watershed (the live reference thesis; Lima is worked).
 *   H2 defense — where the build-out meets federal land and the defense base (emerging).
 *   H3 surveillance — who owns it, who's watching, where the money moves (emerging).
 *
 * Discipline (the spine, mirrored from `defenseNexus.ts` and the evidentiary-method skills):
 * H2/H3 are hypotheses UNDER TEST, not findings. A site carries a defense/surveillance entry
 * only when there's a real, public, on-the-record fact behind it; inference is labeled as such;
 * everything else is "—" and lands in a "Not yet assessed under this thesis" chip group — never
 * a zero, which would read as a cleared verdict. We never fabricate a nexus, an operator, or a
 * count: the doc/record figures come from the live bundle (Lima only today) and are "—" elsewhere.
 *
 * Pure (no bundle import) so it unit-tests offline; the page passes Lima's real counts in.
 */
import {
  FACILITY_STATUS_META,
  facilityStatus,
  groupSites,
  type NetworkSite,
  SITES,
  siteBadge,
  type SiteStatus,
} from "./sites";

export type DirLens = "water" | "defense" | "surveillance";

/** Display order of the lens cards / panes (water is the default, live thesis). */
export const LENS_ORDER: readonly DirLens[] = ["water", "defense", "surveillance"];

/** The strength of a per-site signal under H2/H3 — inference until a nexus is documented. */
export type Signal = "anchor" | "strong" | "moderate" | "watch";

interface Swatch {
  label: string;
  color: string;
  bg: string;
  dot: string;
}

export const SIGNAL_META: Record<Signal, Swatch> = {
  anchor: { label: "Anchor case", color: "#3f51b5", bg: "#e8eaf6", dot: "#3f51b5" },
  strong: { label: "Strong signal", color: "#3f51b5", bg: "#f3f4fb", dot: "#5667c8" },
  moderate: { label: "Moderate", color: "#5b6172", bg: "#eceef2", dot: "#8a90a2" },
  watch: { label: "Under investigation", color: "#8a90a2", bg: "#f4f5f8", dot: "#c0c4cf" },
};

/** Build-phase pill swatches (the hex peer of `SITE_STATUS_META`'s CSS classes — the directory
 *  renders pills inline, like the facility pill, rather than through the switcher's class set). */
export const PHASE_PILL: Record<SiteStatus, Swatch> = {
  live: { label: "Live", color: "#2e7d32", bg: "#e9f3ea", dot: "#2e7d32" },
  building: { label: "Building", color: "#3f51b5", bg: "#f3f4fb", dot: "#3f51b5" },
  queued: { label: "Queued", color: "#b46e00", bg: "#fbf1dd", dot: "#b46e00" },
  tracking: { label: "Tracking", color: "#5b6172", bg: "#eceef2", dot: "#8a90a2" },
};

// --- The defense (H2) and surveillance (H3) reading of each site --------------------------------
// A site appears in a thesis group ONLY with a real, public, on-the-record fact; `group: "watch"`
// (the default) means "not yet assessed under this thesis" — it lands in the chip group, not a row.
export type DefGroup = "arsenal" | "federal" | "supply" | "watch";
export type SurvGroup = "onrecord" | "subsidy" | "watch";

export interface DefFact {
  /** The federal / defense nexus, or "—". */
  nexus: string;
  /** How the site relates to it (adjacency, supply chain, …), or "—". */
  linkage: string;
  signal: Signal;
  group: DefGroup;
}
export interface SurvFact {
  /** Operator behind the LLC (inferred), or "—". */
  operator: string;
  /** Capital & public-subsidy note, or "—". */
  capital: string;
  signal: Signal;
  group: SurvGroup;
}

const DEF0: DefFact = { nexus: "—", linkage: "—", signal: "watch", group: "watch" };
const SURV0: SurvFact = { operator: "—", capital: "—", signal: "watch", group: "watch" };

/**
 * Per-site H2/H3 facts. Keyed by slug; absent slugs inherit DEF0/SURV0 ("not yet assessed").
 * Every entry here is a real, public, on-the-record fact (federal facilities, the CHIPS megasite,
 * DLA Land & Maritime, Lima's JSMC + abatement) or an explicitly-labeled inference — never a
 * fabricated claim. Lima is the only fully-worked example under all three lenses.
 */
const LENS_DATA: Record<string, { def?: DefFact; surv?: SurvFact }> = {
  lima: {
    def: {
      nexus: "Lima Army Tank Plant (JSMC)",
      linkage: "Co-located · Allen Co.",
      signal: "anchor",
      group: "arsenal",
    },
    surv: {
      operator: "Shawnee Energy Campus",
      capital: "CRA #548-25 · 15 yr / 75%",
      signal: "anchor",
      group: "onrecord",
    },
  },
  springfield: {
    def: {
      nexus: "Springfield-Beckley ANGB",
      linkage: "Adjacent · NASIC nearby",
      signal: "moderate",
      group: "arsenal",
    },
  },
  wpafb: {
    def: {
      nexus: "Wright-Patterson AFB",
      linkage: "Adjacent · Mad R. terminus",
      signal: "strong",
      group: "arsenal",
    },
  },
  "hamilton-middletown": {
    surv: { operator: "—", capital: "Municipal power + CRA (signal)", signal: "watch", group: "subsidy" },
  },
  "new-albany": {
    def: {
      nexus: "CHIPS semiconductor megasite",
      linkage: "Federal program",
      signal: "moderate",
      group: "federal",
    },
    surv: {
      operator: "Hyperscaler cluster (inferred)",
      capital: "JobsOhio · TIF (inference)",
      signal: "moderate",
      group: "onrecord",
    },
  },
  columbus: {
    def: { nexus: "DLA Land & Maritime", linkage: "Supply chain", signal: "moderate", group: "federal" },
    surv: { operator: "—", capital: "Enterprise-zone abatement (signal)", signal: "watch", group: "subsidy" },
  },
  lordstown: {
    def: {
      nexus: "Defense-battery corridor",
      linkage: "Supply chain (signal)",
      signal: "watch",
      group: "supply",
    },
  },
};

/** A site's defense + surveillance reading, defaulting to "not yet assessed". */
export function lensDatum(slug: string): { def: DefFact; surv: SurvFact } {
  const d = LENS_DATA[slug];
  return { def: d?.def ?? DEF0, surv: d?.surv ?? SURV0 };
}

// --- The two continental divides (water lens grouping) ------------------------------------------
// Basins nest under the divide they drain to — the water thesis's organizing fact. Labels match
// `PLACEMENT`'s basin names so `groupSites("basin")` keys line up.
const DIVIDES: readonly { label: string; note: string; basins: readonly string[] }[] = [
  { label: "Lake Erie drainage", note: "north — into Lake Erie", basins: ["Maumee", "Sandusky", "Cuyahoga"] },
  {
    label: "Ohio River drainage",
    note: "south — into the Ohio & Mississippi",
    basins: ["Great Miami", "Little Miami", "Scioto", "Muskingum", "Mahoning", "Hocking"],
  },
];

// --- Lens configuration (cards, framing, columns) ----------------------------------------------
export interface LensConfig {
  key: DirLens;
  /** Hypothesis tag, H1/H2/H3. */
  n: string;
  name: string;
  accent: string;
  accentBg: string;
  accentBd: string;
  /** "Reference build" (live) or "Emerging hypothesis" (new). */
  status: string;
  statusKind: "live" | "new";
  claim: string;
  blurb: string;
  axisTitle: string;
  scoreTitle: string;
  scoreNote: string;
  footNote: string;
  cols: readonly { label: string; align?: "right" }[];
  fr: readonly string[];
}

export const LENSES: Record<DirLens, LensConfig> = {
  water: {
    key: "water",
    n: "H1",
    name: "Water & Power",
    accent: "#3f51b5",
    accentBg: "#f3f4fb",
    accentBd: "#c5cae9",
    status: "Reference build",
    statusKind: "live",
    claim: "Where compute meets the watershed.",
    blurb:
      "The original thesis: hyperscale compute lands where it can pull power and water, and a data center's intake, discharge, and downstream effects are basin facts. Sites nest by drainage — two divides, nine basins. Lima is the live, fully-assembled reference.",
    axisTitle: "Two divides · nine basins",
    scoreTitle: "Every point, by drainage",
    scoreNote: "Build phase and facility status are two clocks — kept distinct.",
    footNote: "A dash means the section isn't assembled yet — never a zero, which would read as a finding.",
    cols: [
      { label: "Site" },
      { label: "Watershed point" },
      { label: "Build phase" },
      { label: "Documents", align: "right" },
      { label: "Records", align: "right" },
      { label: "Facility status" },
    ],
    fr: ["1.5fr", "1.4fr", "0.95fr", "0.78fr", "0.78fr", "1.15fr"],
  },
  defense: {
    key: "defense",
    n: "H2",
    name: "Defense & Federal Enclave",
    accent: "#4a5a6b",
    accentBg: "#eef1f4",
    accentBd: "#cdd5dd",
    status: "Emerging hypothesis",
    statusKind: "new",
    claim: "Where the build-out meets federal land and the defense base.",
    blurb:
      "A second reading: the same map tracks arsenals, air bases, federal research and the CHIPS build — enclaves where federal jurisdiction, clearance, and defense supply chains concentrate. Newly opened; most sites are not yet assessed, and a federal nexus is a signal, not a verdict.",
    axisTitle: "Assessment so far",
    scoreTitle: "Every site, by federal nexus",
    scoreNote: "Signal is inference until a federal nexus is documented.",
    footNote:
      "Sites without an entry are not yet assessed under this thesis — that is not the same as cleared.",
    cols: [
      { label: "Site" },
      { label: "Federal / defense nexus" },
      { label: "Linkage" },
      { label: "Signal" },
      { label: "Facility status" },
    ],
    fr: ["1.4fr", "1.8fr", "1.0fr", "1.05fr", "1.15fr"],
  },
  surveillance: {
    key: "surveillance",
    n: "H3",
    name: "Corporate & Economic Surveillance",
    accent: "#715a78",
    accentBg: "#f2eef3",
    accentBd: "#d8cdda",
    status: "Emerging hypothesis",
    statusKind: "new",
    claim: "Who owns it, who's watching, and where the money moves.",
    blurb:
      "A third reading: the operators behind shell LLCs, the public-subsidy stack that pulls them in, and the capital and data flows the facilities sit on. The corporate-and-economic-surveillance thesis — opening now, mostly under investigation, with Lima's abatement on record.",
    axisTitle: "Assessment so far",
    scoreTitle: "Every site, by operator & capital",
    scoreNote: "Operators behind LLCs; public subsidy is on the public record.",
    footNote:
      "Sites without an entry are not yet assessed under this thesis — that is not the same as cleared.",
    cols: [
      { label: "Site" },
      { label: "Operator (inferred)" },
      { label: "Capital & public subsidy" },
      { label: "Signal" },
      { label: "Facility status" },
    ],
    fr: ["1.4fr", "1.5fr", "1.6fr", "1.05fr", "1.15fr"],
  },
};

/** The lens-card count line: the water lens counts the network; H2/H3 count assessment progress. */
export function lensCount(lens: DirLens): string {
  if (lens === "water") return `${SITES.length} sites · ${groupSites("basin").length} basins`;
  const assessed = SITES.filter((s) =>
    lens === "defense" ? lensDatum(s.slug).def.group !== "watch" : lensDatum(s.slug).surv.group !== "watch",
  ).length;
  return `${assessed} assessed · ${SITES.length - assessed} to review`;
}

// --- The rendered view model -------------------------------------------------------------------
export interface AxisGroup {
  label?: string;
  chips: { name: string; count: number }[];
}
export type CellKind = "site" | "text" | "num" | "pill";
export interface Cell {
  kind: CellKind;
  // site
  badge?: string;
  place?: string;
  badgeBg?: string;
  badgeColor?: string;
  // text / num
  text?: string;
  muted?: boolean;
  // pill
  pill?: Swatch;
}
export interface Row {
  slug: string;
  live: boolean;
  cells: Cell[];
}
export interface Group {
  kind: "rows" | "chips";
  abbr: string;
  label: string;
  count: number;
  /** Set on the first basin group of a divide (water lens) — the divide banner above it. */
  divide?: { label: string; note: string };
  rows: Row[];
  chips: { place: string; dot: string }[];
}
export interface LensView {
  key: DirLens;
  axisTitle: string;
  axisGroups: AxisGroup[];
  cols: { label: string; align: "left" | "right" }[];
  gridCols: string;
  groups: Group[];
}

const siteCell = (s: NetworkSite): Cell => {
  const live = s.status === "live";
  const codename = Boolean(s.codename);
  return {
    kind: "site",
    badge: siteBadge(s),
    place: s.place,
    badgeBg: live ? "#3f51b5" : codename ? "#eef0f4" : "#eceef2",
    badgeColor: live ? "#fff" : codename ? "#3f51b5" : "#5b6172",
  };
};
const textCell = (t: string, muted = false): Cell => {
  const empty = !t || t === "—";
  return { kind: "text", text: t || "—", muted: muted || empty };
};
const numCell = (t: string): Cell => ({ kind: "num", text: t, muted: t === "—" });
const pillCell = (s: Swatch): Cell => ({ kind: "pill", pill: s });

const facPill = (slug: string): Cell => pillCell(FACILITY_STATUS_META[facilityStatus(slug)]);

/**
 * Build a lens's full view model: the scorecard column spec, the grouped rows (or chip groups),
 * and the framing-panel axis chips. `limaCounts` carries Lima's real bundle figures; every other
 * site shows "—" (no assembled record yet).
 */
export function buildLens(lens: DirLens, limaCounts: { docs: string; records: string }): LensView {
  const cfg = LENSES[lens];
  const cols = cfg.cols.map((c) => ({ label: c.label, align: c.align ?? ("left" as const) }));
  const gridCols = cfg.fr.join(" ");

  const groups: Group[] = [];
  const axisGroups: AxisGroup[] = [];

  if (lens === "water") {
    const byBasin = new Map(groupSites("basin").map((g) => [g.label, g]));
    for (const d of DIVIDES) {
      d.basins.forEach((basinLabel, i) => {
        const grp = byBasin.get(basinLabel);
        if (!grp?.sites.length) return;
        const rows: Row[] = grp.sites.map((s) => ({
          slug: s.slug,
          live: s.status === "live",
          cells: [
            siteCell(s),
            textCell(s.basin),
            pillCell(PHASE_PILL[s.status]),
            numCell(s.slug === "lima" ? limaCounts.docs : "—"),
            numCell(s.slug === "lima" ? limaCounts.records : "—"),
            facPill(s.slug),
          ],
        }));
        const g: Group = {
          kind: "rows",
          abbr: grp.tag,
          label: grp.label,
          count: grp.sites.length,
          rows,
          chips: [],
        };
        if (i === 0) g.divide = { label: d.label, note: d.note };
        groups.push(g);
      });
    }
    axisGroups.push(
      ...DIVIDES.map((d) => ({
        label: d.label,
        chips: d.basins
          .map((b) => ({ name: b, count: byBasin.get(b)?.sites.length ?? 0 }))
          .filter((c) => c.count > 0),
      })),
    );
    return { key: lens, axisTitle: cfg.axisTitle, axisGroups, cols, gridCols, groups };
  }

  // Defense / surveillance: group by thesis category, with a "not yet assessed" chip tail.
  const isDef = lens === "defense";
  const grpKey = (s: NetworkSite): string =>
    isDef ? lensDatum(s.slug).def.group : lensDatum(s.slug).surv.group;
  const rowFor = (s: NetworkSite): Row => {
    const dat = lensDatum(s.slug);
    const cells = isDef
      ? [
          siteCell(s),
          textCell(dat.def.nexus),
          textCell(dat.def.linkage, true),
          pillCell(SIGNAL_META[dat.def.signal]),
          facPill(s.slug),
        ]
      : [
          siteCell(s),
          textCell(dat.surv.operator),
          textCell(dat.surv.capital),
          pillCell(SIGNAL_META[dat.surv.signal]),
          facPill(s.slug),
        ];
    return { slug: s.slug, live: s.status === "live", cells };
  };

  const cats: [string, string, string][] = isDef
    ? [
        ["arsenal", "MIL", "Arsenals & air bases"],
        ["federal", "FED", "Federal semiconductor & research"],
        ["supply", "SUP", "Defense supply corridors"],
      ]
    : [
        ["onrecord", "OPR", "Operator & subsidy on record"],
        ["subsidy", "SUB", "Public-subsidy signal only"],
      ];

  for (const [key, abbr, label] of cats) {
    const sites = SITES.filter((s) => grpKey(s) === key);
    if (!sites.length) continue;
    groups.push({ kind: "rows", abbr, label, count: sites.length, rows: sites.map(rowFor), chips: [] });
  }
  const watch = SITES.filter((s) => grpKey(s) === "watch");
  if (watch.length) {
    groups.push({
      kind: "chips",
      abbr: "—",
      label: "Not yet assessed under this thesis",
      count: watch.length,
      rows: [],
      chips: watch.map((s) => ({ place: s.place, dot: PHASE_PILL[s.status].dot })),
    });
  }
  axisGroups.push({
    chips: [
      ...cats.map(([key, , label]) => ({
        name: label.split(" &")[0],
        count: SITES.filter((s) => grpKey(s) === key).length,
      })),
      { name: "Not yet assessed", count: watch.length },
    ],
  });

  return { key: lens, axisTitle: cfg.axisTitle, axisGroups, cols, gridCols, groups };
}
