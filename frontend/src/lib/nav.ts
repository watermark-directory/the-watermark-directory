/**
 * The site's information architecture. Two related models:
 *
 *  - `SECTIONS` — the **content areas**, each with a minimal table of contents
 *    (the per-section TOC rail, the search index, and the docs grouping read it).
 *  - `NETWORK_TABS` / `SITE_TABS` / `PLATFORM_LINKS` — the **header bar**
 *    presentation (design "Global Chrome"): a two-tier bar whose left tabs swap
 *    by tier, plus the constant platform cluster on the right.
 *
 * A page declares its `section`; the header resolves which tab is active via
 * `navItemActive` (so the Watershed sub-area lights the Corpus tab, etc.).
 *
 * Each TOC `anchor` is an `id` the section's landing page renders, so the rail
 * links, the on-page scroll-spy, and search deep-links all resolve to a real
 * heading.
 */

export type SectionId =
  | "home"
  | "story"
  | "timeline"
  | "reports"
  | "about"
  | "site"
  | "watershed"
  | "wiki"
  | "ask"
  | "search"
  | "directory"
  | "hypotheses"
  | "submit";

export interface TocEntry {
  /** Visible label in the per-section TOC. */
  label: string;
  /** The `id` of the heading on the section page this entry points to. */
  anchor: string;
}

export interface Section {
  id: SectionId;
  /** Full label (section H1, search). */
  label: string;
  /** Short label for the topbar tab. */
  tab: string;
  /** Root-absolute path to the section landing (pre-base). */
  href: string;
  /** One-line description (used on the landing and in search). */
  blurb: string;
  toc: TocEntry[];
}

export const SECTIONS: Section[] = [
  {
    id: "home",
    label: "Home",
    tab: "Home",
    href: "/bosc",
    blurb: "Landing, disclaimer, corpus at a glance, and the two doors in.",
    toc: [
      { label: "Disclaimer", anchor: "disclaimer" },
      { label: "Corpus at a glance", anchor: "corpus" },
      { label: "Methodology", anchor: "methodology" },
      { label: "The bigger picture", anchor: "bigger-picture" },
    ],
  },
  {
    id: "story",
    label: "The story",
    tab: "Story",
    href: "/bosc/start",
    blurb: "The guided walk — read the record one document at a time, no prior knowledge.",
    toc: [],
  },
  {
    id: "timeline",
    label: "Timeline",
    tab: "Timeline",
    href: "/bosc/timeline",
    blurb: "Every dated event in the record, ordered — confidentiality first, the public reveal last.",
    toc: [],
  },
  {
    id: "reports",
    label: "Reports",
    tab: "Reports",
    href: "/bosc/reports",
    blurb:
      "Long-form analysis over the corpus — the dossier, the water and economics reads, and the extension narratives.",
    toc: [],
  },
  {
    id: "site",
    label: "The corpus",
    tab: "Corpus",
    href: "/bosc/site/",
    blurb: "Documents, records, exhibits, people & places, legal history, and the watershed data.",
    toc: [
      { label: "Documents", anchor: "documents" },
      { label: "Records", anchor: "records" },
      { label: "Timeline", anchor: "timeline" },
      { label: "Exhibits", anchor: "exhibits" },
      { label: "People & places", anchor: "people" },
      { label: "Legal history", anchor: "legal" },
      { label: "Reference data", anchor: "reference" },
    ],
  },
  {
    id: "watershed",
    label: "The Maumee watershed",
    tab: "Watershed",
    href: "/bosc/watershed/",
    blurb: "Hydrology dashboards, the watershed map, imagery before/during/after, and RSEI toxics.",
    toc: [
      { label: "Hydrology", anchor: "hydrology" },
      { label: "Watershed map", anchor: "map" },
      { label: "Imagery", anchor: "imagery" },
      { label: "RSEI / toxics", anchor: "rsei" },
    ],
  },
  {
    id: "about",
    label: "About",
    tab: "About",
    href: "/about",
    blurb: "What Watermark is, the method behind it, and who's assembling it.",
    toc: [],
  },
  {
    id: "wiki",
    label: "Wiki",
    tab: "Wiki",
    href: "/wiki/",
    blurb: "Entity & concept pages with backlinks and a graph neighborhood.",
    toc: [
      { label: "Entities", anchor: "entities" },
      { label: "People", anchor: "people" },
      { label: "Concepts", anchor: "concepts" },
      { label: "Curated entities", anchor: "curated" },
    ],
  },
  {
    id: "ask",
    label: "Ask the corpus",
    tab: "Ask",
    href: "/ask",
    blurb: "Ask a question of the record and get a cited answer drawn only from the extracted corpus.",
    toc: [],
  },
  {
    // The network directory — the multi-site overview (#304/#307, route renamed /network → /directory
    // in #402). The root `/` redirects to the live site (/bosc); this directory lists every
    // watershed-point site. The switcher is the primary entry.
    id: "directory",
    label: "The network directory",
    tab: "Directory",
    href: "/directory/",
    blurb:
      "Data-center development across Ohio's Maumee watershed, point by point — Lima is the reference build.",
    toc: [],
  },
  {
    // The network's hypotheses layer (the (site × hypothesis) join) — read the network
    // through the boom-origin hypotheses. A network-tier tab beside Report.
    id: "hypotheses",
    label: "Hypotheses",
    tab: "Research",
    href: "/directory/hypotheses",
    blurb: "Read the network three ways — the boom-origin hypotheses, scored against each site.",
    toc: [],
  },
  {
    // Contribute a lead — a network-tier entry (no account; a document, a name, a correction).
    id: "submit",
    label: "Submit a lead",
    tab: "Submit",
    href: "/submit",
    blurb: "Contribute a document, a name, or a correction — every confirmed figure started as a lead.",
    toc: [],
  },
];

export function getSection(id: SectionId): Section {
  const section = SECTIONS.find((s) => s.id === id);
  if (!section) throw new Error(`Unknown section "${id}"`);
  return section;
}

// --- Header bar model (two-tier chrome, design "Global Chrome") -------------
//
// One bar, two tiers. The `Watermark.` wordmark always links home to the network;
// a chip (the breadcrumb / switcher) sits beside it. The LEFT tabs swap by tier:
//  - network level (the directory + cross-cutting globals) → Directory · Research · About▾
//  - inside a site → The site · The record · The watershed
// The PLATFORM cluster (Docs · Wiki · | · Submit · Ask · Search) sits right and never
// changes — Submit is a right-side affordance present on BOTH tiers (design "Chrome"),
// not a left network tab. The active tier is resolved from the route (`siteForPath` in
// the Header): inside a site → site tier.

/** A link in a dropdown menu (an optional second line), or a horizontal divider. */
export type NavChild = { label: string; href: string; blurb?: string } | { divider: true };

export type NavItem =
  | { kind: "link"; label: string; section: SectionId; href: string; match?: SectionId[] }
  | { kind: "dropdown"; label: string; section: SectionId; children: NavChild[] };

/** Network-tier left tabs — shown at the directory and on cross-cutting globals.
 *  Submit is NOT here — it's a right-cluster affordance (see SUBMIT_LINK / the Header). */
export const NETWORK_TABS: NavItem[] = [
  { kind: "link", label: "Directory", section: "directory", href: "/directory/" },
  { kind: "link", label: "Research", section: "hypotheses", href: "/directory/hypotheses" },
  {
    kind: "dropdown",
    label: "About",
    section: "about",
    children: [
      { label: "Methodology", href: "/bosc/docs/methodology", blurb: "How the record is built & labeled" },
      { label: "About the site", href: "/about", blurb: "What Watermark is, and why" },
      { label: "About the author", href: "/about-me", blurb: "Who keeps the record" },
    ],
  },
];

/** Site-tier left tabs — shown inside a site (e.g. Lima, under /bosc). */
export const SITE_TABS: NavItem[] = [
  { kind: "link", label: "The site", section: "home", href: "/bosc" },
  { kind: "link", label: "The record", section: "site", href: "/bosc/site/", match: ["timeline"] },
  { kind: "link", label: "The watershed", section: "watershed", href: "/bosc/watershed/" },
];

/** The platform cluster (right of the bar), constant across tiers. Ask + Search and
 *  Submit are rendered separately as affordances; these two are the plain links. */
export const PLATFORM_LINKS: { label: string; section: SectionId; href: string }[] = [
  { label: "Docs", section: "reports", href: "/bosc/docs/" },
  { label: "Wiki", section: "wiki", href: "/wiki/" },
];

/** Submit — a right-cluster affordance (a `+` pill), present on both tiers (design
 *  "Chrome"). It's the network-tier `/submit` route; the per-record correction
 *  deep-links target the site-tier `/bosc/submit` instead (both share <SubmitForm>). */
export const SUBMIT_LINK: { label: string; section: SectionId; href: string } = {
  label: "Submit",
  section: "submit",
  href: "/submit",
};

/** Whether `item` is the active header tab for the page's `active` section. */
export function navItemActive(item: NavItem, active: SectionId): boolean {
  if (item.section === active) return true;
  return item.kind === "link" && (item.match?.includes(active) ?? false);
}

/** Flat primary-nav links for the footer row — both tiers + platform. */
export const NAV_LINKS: { label: string; href: string }[] = [
  ...SITE_TABS.filter((t): t is Extract<NavItem, { kind: "link" }> => t.kind === "link").map((t) => ({
    label: t.label,
    href: t.href,
  })),
  { label: "Directory", href: "/directory/" },
  { label: "Research", href: "/directory/hypotheses" },
  ...PLATFORM_LINKS.map((t) => ({ label: t.label, href: t.href })),
];
