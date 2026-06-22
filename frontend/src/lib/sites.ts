/**
 * The Watermark network — the registry of watershed-point sites (the multi-site pivot, #304).
 *
 * Decision (locked): **one build, one site.** This is an *in-build* navigation concept,
 * not separate deployments — every watershed point is a section of the single build, and
 * cross-references between them are real. Lima is the live reference build; the basin
 * sites come online incrementally.
 *
 * Only a `selectable` site can be switched into (today: Lima alone). Every other site —
 * including Fort Wayne, a live facility we can onboard fast but haven't built yet — routes
 * to its coming-soon page (#305) and is never rendered as a switchable destination.
 */

/** Site BUILD lifecycle — our progress assembling the *website* (a separate clock from the data
 *  center's real-world `facilityStatus`). `live` = built + selectable; `building` = scaffold up,
 *  sections coming online; `queued` = announced & in the build queue. Only `live` is selectable. */
export type SiteStatus = "live" | "building" | "queued";

export interface NetworkSite {
  /** Registry + URL key (kebab). */
  slug: string;
  /** Per-site codename — the switcher badge. `null` falls back to `mono`. */
  codename: string | null;
  /** Three-letter fallback badge when there's no codename. */
  mono: string;
  place: string;
  /** Receiving water / basin subline shown under the place. */
  basin: string;
  status: SiteStatus;
  /** Can a reader switch into this site's build? Only the live reference site today. */
  selectable: boolean;
  /** Tracking issue number (no `#`), when one exists. */
  issue?: string;
  /** Where the switcher row points: the live root, or the coming-soon page. */
  href: string;
}

/** The single source of truth for the switcher, the coming-soon pages, and the basin map.
 *  Order is the display order in the switcher (active first, then by basin position). */
export const SITES: readonly NetworkSite[] = [
  {
    slug: "lima",
    codename: "BOSC",
    mono: "LIM",
    place: "Lima",
    basin: "Ottawa River · Lima, OH",
    status: "live",
    selectable: true,
    href: "/bosc",
  },
  {
    // A live data-center facility; the site build is queued (onboard fast, not selectable yet).
    slug: "fort-wayne",
    codename: "GCP",
    mono: "FTW",
    place: "Fort Wayne",
    basin: "Maumee headwaters",
    status: "building",
    selectable: false,
    issue: "235",
    href: "/directory/fort-wayne",
  },
  {
    slug: "defiance",
    codename: null,
    mono: "DEF",
    place: "Defiance",
    basin: "Maumee mainstem",
    status: "queued",
    selectable: false,
    issue: "238",
    href: "/directory/defiance",
  },
  {
    slug: "findlay",
    codename: null,
    mono: "FIN",
    place: "Findlay",
    basin: "Blanchard River",
    status: "queued",
    selectable: false,
    issue: "237",
    href: "/directory/findlay",
  },
  {
    slug: "toledo",
    codename: null,
    mono: "TOL",
    place: "Toledo",
    basin: "Lucas Co WRRF",
    status: "queued",
    selectable: false,
    issue: "236",
    href: "/directory/toledo",
  },
  {
    // Small-stream headwaters comparator: a 4 MGD plant on a small tributary (the
    // effluent-dominance end of the basin spectrum). Onboarded, not yet built.
    slug: "van-wert",
    codename: null,
    mono: "VWT",
    place: "Van Wert",
    basin: "Town Creek · Little Auglaize",
    status: "queued",
    selectable: false,
    issue: "363",
    href: "/directory/van-wert",
  },
  {
    // Municipal-utility / Tiffin-subbasin headwaters comparator: the basin's first municipal
    // electric point (Bryan Municipal Utilities, AMP/PJM). Onboarded, not yet built.
    slug: "bryan",
    codename: null,
    mono: "BRY",
    place: "Bryan",
    basin: "Prairie Creek · Tiffin River",
    status: "queued",
    selectable: false,
    issue: "380",
    href: "/directory/bryan",
  },
  {
    // Intra-tributary (same-river) comparator: the downstream Blanchard sibling of Findlay —
    // same receiving river, two points ~40 river-mi apart. Onboarded, not yet built.
    slug: "ottawa",
    codename: null,
    mono: "OTW",
    place: "Ottawa",
    basin: "Blanchard River (lower)",
    status: "queued",
    selectable: false,
    issue: "381",
    href: "/directory/ottawa",
  },
  {
    // The network's FIRST Miami-basin site (second basin branch): the clean headwaters of the
    // Mad River buried-valley sole-source aquifer, upstream of the Wright-Patterson / Dayton
    // corridor — the geological inverse of the Maumee lake-plain sites. Onboarding (#441 / epic #440).
    slug: "urbana",
    codename: null,
    mono: "URB",
    place: "Urbana",
    basin: "Mad River · Great Miami",
    status: "queued",
    selectable: false,
    issue: "441",
    href: "/directory/urbana",
  },
  {
    // The network's SECOND Miami-basin site: the Mad River MID-CORRIDOR node between the Urbana
    // headwaters (#441) and Dayton / Wright-Patterson (#442), on the same buried-valley
    // sole-source aquifer — distinguished by a managed second supply water (Buck Creek / C.J.
    // Brown Reservoir). Onboarding (#452 / epic #451).
    slug: "springfield",
    codename: null,
    mono: "SPR",
    place: "Springfield",
    basin: "Mad River · Great Miami",
    status: "queued",
    selectable: false,
    issue: "452",
    href: "/directory/springfield",
  },
  {
    // The network's FIRST Little Miami-basin site (a third basin branch): the WPAFB-adjacent
    // Greene County node on the Little Miami — a National & State Scenic River, the heightened
    // regulatory-overlay receiving water the Maumee/Great-Miami sites lack. Tracking (#444).
    slug: "xenia",
    codename: null,
    mono: "XEN",
    place: "Xenia",
    basin: "Little Miami",
    status: "queued",
    selectable: false,
    issue: "444",
    href: "/directory/xenia",
  },
  {
    // The downstream terminus of the Mad River corridor and the richest Miami node: the SW-Ohio
    // analog to Lima's defense nexus. Wright-Patterson AFB — regulated/air-gapped DoD cloud (the
    // distinctive data-center variant), a sole-source buried-valley aquifer, and a documented
    // TCE/PFAS plume on it. Already in the corpus (defense-footprint testimony). Tracking (#442).
    slug: "wpafb",
    codename: null,
    mono: "WPA",
    place: "Dayton · WPAFB",
    basin: "Mad River · Great Miami",
    status: "queued",
    selectable: false,
    issue: "442",
    href: "/directory/wpafb",
  },
  {
    // The lower Great Miami heavy-industry node and the I-75 Cincinnati–Dayton corridor's southern
    // anchor: the established-industry comparator to the greenfield sites (Cleveland-Cliffs
    // Middletown Works / former AK Steel), on the Great Miami mainstem. Butler County (seat = City of
    // Hamilton, NOT Hamilton County/Cincinnati); a third PJM zone (DEOK). Tracking (#443).
    slug: "hamilton-middletown",
    codename: null,
    mono: "HAM",
    place: "Hamilton · Middletown",
    basin: "Great Miami (lower)",
    status: "queued",
    selectable: false,
    issue: "443",
    href: "/directory/hamilton-middletown",
  },
] as const;

/** This build is the Lima reference build. */
export const ACTIVE_SITE_SLUG = "lima";

export function activeSite(): NetworkSite {
  const site = SITES.find((s) => s.slug === ACTIVE_SITE_SLUG);
  if (!site) throw new Error(`Active site "${ACTIVE_SITE_SLUG}" missing from the registry`);
  return site;
}

/** The badge shown for a site — its codename, else its 3-letter mono. */
export function siteBadge(site: NetworkSite): string {
  return site.codename ?? site.mono;
}

/**
 * Resolve which network site a route belongs to — the switcher's *current* state (#316).
 * Prefix-matches the path against each site's `href`: `/bosc[/…]` → the live Lima build,
 * `/directory/<slug>[/…]` → that site (incl. the not-yet-built ones). The network directory
 * (`/directory`) and the cross-cutting globals (`/about`, `/wiki`, `/ask`) belong to no
 * single site → `null` (a neutral network state). `base` strips an Astro base prefix.
 */
export function siteForPath(pathname: string, base = ""): NetworkSite | null {
  let p = pathname;
  if (base && base !== "/" && p.startsWith(base)) p = p.slice(base.length);
  if (!p.startsWith("/")) p = `/${p}`;
  p = p.replace(/\/+$/, "") || "/";
  return (
    SITES.find((s) => {
      const h = s.href.replace(/\/+$/, "");
      return p === h || p.startsWith(`${h}/`);
    }) ?? null
  );
}

/** The sites that need a coming-soon page (everything not switchable). */
export function comingSoonSites(): NetworkSite[] {
  return SITES.filter((s) => !s.selectable);
}

/**
 * The data center's real-world lifecycle — a SEPARATE clock from the site build `status`.
 * The build `status` (live/building/queued) tracks our progress assembling the *website*; this
 * tracks the *facility in the ground* (investigation → confirmed → construction → live). The two
 * are deliberately distinct: a queued site can document a live facility, and a live site can
 * document one still under investigation. A site with no disclosed facility is "investigation"
 * (the data-center dimension is inferential until a project is on the record).
 */
export type FacilityStatus = "investigation" | "confirmed" | "construction" | "live";

const FACILITY_STATUS: Record<string, FacilityStatus> = {
  lima: "construction", // Shawnee Energy Campus — air-permit-grounded, ~313 MW (the disclosed build)
  "fort-wayne": "confirmed", // GCP — a disclosed facility, not yet a construction record
};

/** A site's facility lifecycle stage; "investigation" when no facility is disclosed. */
export function facilityStatus(slug: string): FacilityStatus {
  return FACILITY_STATUS[slug] ?? "investigation";
}

export const FACILITY_STATUS_META: Record<
  FacilityStatus,
  { label: string; color: string; bg: string; dot: string }
> = {
  investigation: { label: "Under investigation", color: "#5b6172", bg: "#eceef2", dot: "#8a90a2" },
  confirmed: { label: "Confirmed", color: "#3f51b5", bg: "#f3f4fb", dot: "#3f51b5" },
  construction: { label: "Under construction", color: "#b46e00", bg: "#fbf1dd", dot: "#b46e00" },
  live: { label: "Live", color: "#2e7d32", bg: "#e9f3ea", dot: "#2e7d32" },
};

/**
 * The facility lifecycle in order — the stepped progress rail (#401). The 4-stage indicator
 * on a facility/record header walks this sequence: completed stages are filled, the current
 * stage is highlighted in its status color, and future stages are muted. The short labels are
 * the rail's tick captions (the long forms live in `FACILITY_STATUS_META`).
 */
export const FACILITY_STAGES: readonly { status: FacilityStatus; short: string }[] = [
  { status: "investigation", short: "Investigation" },
  { status: "confirmed", short: "Confirmed" },
  { status: "construction", short: "Construction" },
  { status: "live", short: "Live" },
];

/** The 0-based position of a facility status within `FACILITY_STAGES` — the rail's current step. */
export function facilityStageIndex(status: FacilityStatus): number {
  return FACILITY_STAGES.findIndex((s) => s.status === status);
}

// --- Grouped switcher (#307 dictate C) ------------------------------------------------------
// Canonical (state, watershed) placement for every site. The switcher pivots the SAME sites by
// either axis — `state` is the legal jurisdiction a record lives under; `watershed` is the
// hydrological unit it documents. Both matter to a researcher, so either can be the outer grouping.
const PLACEMENT: Record<string, { state: string; watershed: string }> = {
  lima: { state: "Ohio", watershed: "Ottawa River" },
  "fort-wayne": { state: "Indiana", watershed: "Maumee headwaters" },
  defiance: { state: "Ohio", watershed: "Maumee mainstem" },
  findlay: { state: "Ohio", watershed: "Blanchard River" },
  toledo: { state: "Ohio", watershed: "Maumee mainstem" },
  "van-wert": { state: "Ohio", watershed: "Little Auglaize" },
  bryan: { state: "Ohio", watershed: "Tiffin River" },
  ottawa: { state: "Ohio", watershed: "Blanchard River" },
  // The first Miami-basin point — a distinct watershed group (Ohio River sink, not Lake Erie).
  urbana: { state: "Ohio", watershed: "Great Miami (Mad River)" },
  springfield: { state: "Ohio", watershed: "Great Miami (Mad River)" },
  xenia: { state: "Ohio", watershed: "Little Miami" },
  wpafb: { state: "Ohio", watershed: "Great Miami (Mad River)" },
  "hamilton-middletown": { state: "Ohio", watershed: "Great Miami (lower)" },
};
const STATE_ABBR: Record<string, string> = { Ohio: "OH", Indiana: "IN" };

export type GroupBy = "state" | "watershed";

export interface SiteGroup {
  /** Group heading (the state name, or the watershed name). */
  label: string;
  /** Short tag shown beside the heading (the state abbr; empty for watershed groups). */
  tag: string;
  sites: NetworkSite[];
}

/**
 * Group the registry by the State (jurisdiction) or Watershed (basin) axis — the grouped
 * switcher's two lenses (#307). Group order follows first appearance in `SITES`; rows keep
 * their registry order, so toggling the axis pivots the same sites without reshuffling them.
 */
export function groupSites(by: GroupBy): SiteGroup[] {
  const groups: SiteGroup[] = [];
  const index = new Map<string, SiteGroup>();
  for (const s of SITES) {
    const p = PLACEMENT[s.slug];
    if (!p) continue;
    const label = by === "state" ? p.state : p.watershed;
    let g = index.get(label);
    if (!g) {
      g = { label, tag: by === "state" ? (STATE_ABBR[p.state] ?? "") : "", sites: [] };
      index.set(label, g);
      groups.push(g);
    }
    g.sites.push(s);
  }
  return groups;
}
