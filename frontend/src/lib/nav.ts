/**
 * The site's information architecture. Two related models:
 *
 *  - `SECTIONS` — the **content areas**, each with a minimal table of contents
 *    (the per-section TOC rail, the search index, and the docs grouping read it).
 *  - `NAV_TABS` — the **header bar** presentation: ordered tabs, an About
 *    dropdown, and a vertical divider before the corpus/wiki cluster.
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
  | "ask";

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
    href: "/",
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
    href: "/start",
    blurb: "The guided walk — read the record one document at a time, no prior knowledge.",
    toc: [],
  },
  {
    id: "timeline",
    label: "Timeline",
    tab: "Timeline",
    href: "/timeline",
    blurb: "Every dated event in the record, ordered — confidentiality first, the public reveal last.",
    toc: [],
  },
  {
    id: "reports",
    label: "Reports",
    tab: "Reports",
    href: "/reports",
    blurb:
      "Long-form analysis over the corpus — the dossier, the water and economics reads, and the extension narratives.",
    toc: [],
  },
  {
    id: "site",
    label: "The corpus",
    tab: "Corpus",
    href: "/site/",
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
    href: "/watershed/",
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
    blurb: "What Project BOSC is, the method behind it, and who's assembling it.",
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
];

export function getSection(id: SectionId): Section {
  const section = SECTIONS.find((s) => s.id === id);
  if (!section) throw new Error(`Unknown section "${id}"`);
  return section;
}

// --- Header bar model ------------------------------------------------------

/** A link in the About dropdown, or a horizontal divider within it. */
export type NavChild = { label: string; href: string } | { divider: true };

export type NavItem =
  | { kind: "link"; label: string; section: SectionId; href: string; match?: SectionId[] }
  | { kind: "dropdown"; label: string; section: SectionId; children: NavChild[] }
  | { kind: "divider" };

/**
 * The header tabs, in order. The About dropdown groups the method + the personal
 * pages; the divider sets the narrative tabs (Home…Reports) apart from the
 * reference cluster (Corpus, Wiki). The Corpus tab also owns the Watershed
 * sub-area, which is reached from the corpus landing rather than its own tab.
 */
export const NAV_TABS: NavItem[] = [
  { kind: "link", label: "Home", section: "home", href: "/" },
  { kind: "link", label: "Story", section: "story", href: "/start" },
  { kind: "link", label: "Timeline", section: "timeline", href: "/timeline" },
  { kind: "link", label: "Reports", section: "reports", href: "/reports" },
  {
    kind: "dropdown",
    label: "About",
    section: "about",
    children: [
      { label: "Methodology", href: "/docs/methodology" },
      { divider: true },
      { label: "About me", href: "/about-me" },
      { label: "The project", href: "/about" },
    ],
  },
  { kind: "divider" },
  { kind: "link", label: "Corpus", section: "site", href: "/site/", match: ["watershed"] },
  { kind: "link", label: "Wiki", section: "wiki", href: "/wiki/" },
  { kind: "link", label: "Ask", section: "ask", href: "/ask" },
];

/** Whether `item` is the active header tab for the page's `active` section. */
export function navItemActive(item: NavItem, active: SectionId): boolean {
  if (item.kind === "divider") return false;
  if (item.section === active) return true;
  return item.kind === "link" && (item.match?.includes(active) ?? false);
}

/** The header link tabs (for the footer's primary-nav row). */
export const NAV_LINKS = NAV_TABS.filter((t): t is Extract<NavItem, { kind: "link" }> => t.kind === "link");
