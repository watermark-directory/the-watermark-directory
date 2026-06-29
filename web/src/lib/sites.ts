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
 *  sections coming online; `queued` = registered profile + coming-soon page, in the build queue;
 *  `tracking` = a GitHub-tracked candidate with an issue but no registered profile yet (the
 *  earliest phase — it routes to a lightweight "watch" page). Only `live` is selectable. */
import { runWithSite } from "./bundle";
import { DEFAULT_STORY_CODENAME, SITE_BASE, siteBase } from "./routes";

export type SiteStatus = "live" | "building" | "queued" | "tracking";

/**
 * A story a site hosts — the lightweight registry reference (#724/#729). It names the story
 * (codename + title) for the switcher / nav; the full reading path (chapters, anchors) lives
 * in the story store keyed by `(site.slug, codename)` — `storyFor` in `./walk` today, the MDX
 * `stories` collection later (#730).
 */
export interface StoryRef {
  /** Story codename — the URL segment under the site's `stories/` and the store key. */
  codename: string;
  /** Display title, e.g. "Project BOSC". */
  title: string;
  /** One-line description — the on-ramp dek / nav blurb (story-level, not per chapter). */
  dek: string;
}

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
  /**
   * Restricted by policy (design "Site Locked") — the record is sealed (source protection,
   * legal sensitivity, or an embargo). Orthogonal to `status`: a locked site can be at any
   * build phase. The switcher marks it with a lock and routes to its request-access page; the
   * directory route renders the locked screen. No real site is locked today (a capability).
   */
  locked?: boolean;
  /** Why a `locked` site is sealed — drives the request-access dek. */
  lockReason?: "sourcing" | "legal" | "embargo";
  /** The stories this site hosts, in display order. Absent until a site has one (#724). */
  stories?: readonly StoryRef[];
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
    href: SITE_BASE,
    stories: [
      {
        codename: DEFAULT_STORY_CODENAME,
        title: "Project BOSC",
        dek: "Project BOSC — read the record one document at a time, no prior knowledge.",
      },
    ],
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
    href: "/network/fort-wayne",
    stories: [
      {
        codename: "project-zodiac",
        title: "Project Zodiac",
        dek: "Project Zodiac — a $2B Google data center in Fort Wayne, read from the records.",
      },
    ],
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
    href: "/network/defiance",
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
    href: "/network/findlay",
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
    href: "/network/toledo",
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
    href: "/network/van-wert",
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
    href: "/network/bryan",
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
    href: "/network/ottawa",
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
    href: "/network/urbana",
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
    href: "/network/springfield",
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
    href: "/network/xenia",
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
    href: "/network/wpafb",
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
    href: "/network/hamilton-middletown",
  },
  {
    // The upper Great Miami mainstem node (Miami County), upstream of WPAFB — the I-75 corridor
    // between the Great Miami headwaters and Dayton. Mid-size manufacturing (Hobart food equipment,
    // auto parts) with a second muni-power story (Piqua). The upstream complement to
    // Hamilton/Middletown's lower-mainstem node. Tracking (#475).
    slug: "troy-piqua",
    codename: null,
    mono: "TRP",
    place: "Troy · Piqua",
    basin: "Great Miami (upper)",
    status: "queued",
    selectable: false,
    issue: "475",
    href: "/network/troy-piqua",
  },

  // The remaining Miami-basin sites, now onboarded (queued; #440) — registered SiteProfiles in
  // `bosc.sites`: the Great Miami headwaters + the basin-divide edge, and the Little Miami Air
  // Park node. They complete the Miami branch (great-miami + little-miami).
  {
    slug: "sidney",
    codename: null,
    mono: "SID",
    place: "Sidney",
    basin: "Great Miami · headwaters",
    status: "queued",
    selectable: false,
    issue: "481",
    href: "/network/sidney",
  },
  {
    slug: "greenville",
    codename: null,
    mono: "GRV",
    place: "Greenville · Darke Co",
    basin: "Stillwater · basin divide",
    status: "queued",
    selectable: false,
    issue: "482",
    href: "/network/greenville",
  },
  {
    slug: "wilmington",
    codename: null,
    mono: "WIL",
    place: "Wilmington",
    basin: "Todd Fork · Little Miami",
    status: "queued",
    selectable: false,
    issue: "492",
    href: "/network/wilmington",
  },

  // --- Tracking sites (#484 + basin epics): GitHub-tracked candidates with an issue but no
  // registered SiteProfile yet — the earliest phase, routed to a lightweight "watch" page. These
  // fill out the full network the grouped selector depicts (32 sites across 9 basins). ---
  // Scioto (the data-center epicenter)
  {
    slug: "new-albany",
    codename: null,
    mono: "NAL",
    place: "New Albany · Licking",
    basin: "Scioto ↔ Muskingum divide",
    status: "tracking",
    selectable: false,
    issue: "485",
    href: "/network/new-albany",
  },
  {
    slug: "columbus",
    codename: null,
    mono: "COL",
    place: "Columbus",
    basin: "Scioto · Olentangy",
    status: "tracking",
    selectable: false,
    issue: "486",
    href: "/network/columbus",
  },
  // Muskingum (Ohio's largest basin)
  {
    slug: "newark",
    codename: null,
    mono: "NWK",
    place: "Newark",
    basin: "Licking River",
    status: "tracking",
    selectable: false,
    issue: "493",
    href: "/network/newark",
  },
  {
    slug: "zanesville",
    codename: null,
    mono: "ZAN",
    place: "Zanesville",
    basin: "Muskingum mainstem",
    status: "tracking",
    selectable: false,
    issue: "494",
    href: "/network/zanesville",
  },
  {
    slug: "coshocton",
    codename: null,
    mono: "CSH",
    place: "Coshocton",
    basin: "Tuscarawas + Walhonding",
    status: "tracking",
    selectable: false,
    issue: "495",
    href: "/network/coshocton",
  },
  // Sandusky (the Maumee's Lake Erie nutrient sibling)
  {
    slug: "fremont",
    codename: null,
    mono: "FRE",
    place: "Fremont · Clyde",
    basin: "Lower Sandusky",
    status: "tracking",
    selectable: false,
    issue: "496",
    href: "/network/fremont",
  },
  {
    slug: "tiffin",
    codename: null,
    mono: "TIF",
    place: "Tiffin",
    basin: "Sandusky (mid)",
    status: "tracking",
    selectable: false,
    issue: "497",
    href: "/network/tiffin",
  },
  {
    slug: "bucyrus",
    codename: null,
    mono: "BUC",
    place: "Bucyrus",
    basin: "Sandusky headwaters",
    status: "tracking",
    selectable: false,
    issue: "498",
    href: "/network/bucyrus",
  },
  // Cuyahoga (the burning-river industrial legacy)
  {
    slug: "cleveland",
    codename: null,
    mono: "CLE",
    place: "Cleveland",
    basin: "Lower Cuyahoga",
    status: "tracking",
    selectable: false,
    issue: "499",
    href: "/network/cleveland",
  },
  {
    slug: "akron",
    codename: null,
    mono: "AKR",
    place: "Akron",
    basin: "Upper Cuyahoga · CVNP",
    status: "tracking",
    selectable: false,
    issue: "500",
    href: "/network/akron",
  },
  // Mahoning (Voltage Valley EV/battery load)
  {
    slug: "lordstown",
    codename: null,
    mono: "LRD",
    place: "Lordstown · Warren",
    basin: "Upper Mahoning",
    status: "tracking",
    selectable: false,
    issue: "501",
    href: "/network/lordstown",
  },
  {
    slug: "youngstown",
    codename: null,
    mono: "YNG",
    place: "Youngstown",
    basin: "Mahoning mainstem",
    status: "tracking",
    selectable: false,
    issue: "502",
    href: "/network/youngstown",
  },
  // Hocking (the unglaciated Appalachian contrast)
  {
    slug: "lancaster",
    codename: null,
    mono: "LAN",
    place: "Lancaster",
    basin: "Upper Hocking",
    status: "tracking",
    selectable: false,
    issue: "503",
    href: "/network/lancaster",
  },
  {
    slug: "athens",
    codename: null,
    mono: "ATH",
    place: "Athens",
    basin: "Lower Hocking",
    status: "tracking",
    selectable: false,
    issue: "504",
    href: "/network/athens",
  },
  {
    slug: "logan",
    codename: null,
    mono: "LOG",
    place: "Logan",
    basin: "Hocking Hills",
    status: "tracking",
    selectable: false,
    issue: "505",
    href: "/network/logan",
  },
] as const;

/** Build-phase display meta — the switcher row status, the phase pill, and the selector legend
 *  all read from here, so the four phases render identically everywhere. */
export const SITE_STATUS_META: Record<SiteStatus, { label: string; cls: string }> = {
  live: { label: "Live", cls: "is-live" },
  building: { label: "Building", cls: "is-building" },
  queued: { label: "Queued", cls: "is-queued" },
  tracking: { label: "Tracking", cls: "is-tracking" },
};

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
 * Resolve which network site a route belongs to — the switcher's *current* state (#316), and
 * the site-vs-network chrome tier. Only a **selectable** (built) site triggers the site tier:
 * `/network/american-sugar-creek-allen-co[/…]` → the live build. A coming-soon site lives at
 * `/network/<slug>` too, but it's not selectable, so it stays on neutral **network** chrome
 * (the directory `/`, the `/network/<slug>` watch pages, and the cross-cutting globals all →
 * `null`). `base` strips an Astro base prefix.
 */
export function siteForPath(pathname: string, base = ""): NetworkSite | null {
  return siteForPathIn(SITES, pathname, base);
}

/**
 * The seam of {@link siteForPath} (#746): resolve a route to its site over an explicit `sites`
 * list, so the multi-site chrome logic is testable against a two-selectable-site fixture.
 */
export function siteForPathIn(
  sites: readonly NetworkSite[],
  pathname: string,
  base = "",
): NetworkSite | null {
  return matchSiteByPath(sites, pathname, base, true);
}

/**
 * Resolve the network site a `/network/<…>` route belongs to **regardless of `selectable`** — so
 * the switcher reflects the *current* site even on a coming-soon / watch page (`/network/<slug>`),
 * where {@link siteForPath} returns `null` because the full site tier isn't built yet (#793). Use
 * this for the switcher chip + active row; the site-vs-network *tab tier* still keys off
 * {@link siteForPath} (a non-selectable site has no inner pages to tab into).
 */
export function currentSiteForPath(pathname: string, base = ""): NetworkSite | null {
  return matchSiteByPath(SITES, pathname, base, false);
}

/** Shared core: the first site whose `href` is a prefix of `pathname`. `requireSelectable`
 *  restricts to built sites (the tab-tier resolver) vs any site (the switcher's current state). */
function matchSiteByPath(
  sites: readonly NetworkSite[],
  pathname: string,
  base: string,
  requireSelectable: boolean,
): NetworkSite | null {
  let p = pathname;
  if (base && base !== "/" && p.startsWith(base)) p = p.slice(base.length);
  if (!p.startsWith("/")) p = `/${p}`;
  p = p.replace(/\/+$/, "") || "/";
  return (
    sites.find((s) => {
      if (requireSelectable && !s.selectable) return false;
      const h = s.href.replace(/\/+$/, "");
      return p === h || p.startsWith(`${h}/`);
    }) ?? null
  );
}

/** The sites that need a coming-soon page (everything not switchable). */
export function comingSoonSites(): NetworkSite[] {
  return comingSoonFrom(SITES);
}

/** The seam of {@link comingSoonSites} (#746) over an explicit `sites` list. */
export function comingSoonFrom(sites: readonly NetworkSite[]): NetworkSite[] {
  return sites.filter((s) => !s.selectable);
}

/**
 * `getStaticPaths` entries for the `network/[site]/…` routes (#724/#734): one per *selectable*
 * site, keyed by its URL id (`siteBase(slug)` minus `/network/`), with the registry `slug` passed
 * as a prop so a page can thread it into `siteHref(slug, …)` / `loadFeed(name, slug)` (#739).
 * Today that's Lima alone, so these routes reproduce the live build; a second selectable site
 * (#740) gets its own build with no new page files.
 */
export function selectableSitePaths(): Array<{ params: { site: string }; props: { slug: string } }> {
  return selectablePathsFrom(SITES);
}

/**
 * The seam of {@link selectableSitePaths} (#746) over an explicit `sites` list — the testable core
 * that a two-selectable-site fixture exercises (each site keyed by its own `siteBase`).
 */
export function selectablePathsFrom(
  sites: readonly NetworkSite[],
): Array<{ params: { site: string }; props: { slug: string } }> {
  return sites
    .filter((s) => s.selectable)
    .map((s) => ({
      params: { site: siteBase(s.slug).replace("/network/", "") },
      props: { slug: s.slug },
    }));
}

/**
 * Cross a `network/[site]/…/[item]` route's per-item paths with the selectable sites (#724/#735):
 * each item is emitted once per site, with the `site` param and the registry `slug` prop folded
 * in. Use it to wrap an existing item enumeration in a dynamic route's `getStaticPaths`. Today,
 * with Lima alone, the result is just the items; a second selectable site multiplies them.
 *
 * Two call forms (#744):
 * - **Array** — *shared* items (content collections: legal/reference/narrative MDX), the same set
 *   for every site, so they're crossed as-is.
 * - **Callback** `(slug) => items` — *per-site* items (feed-derived routes: records/people/places/
 *   documents). `getStaticPaths` runs **outside** the request-time active-site ALS, so a bare
 *   `loadFeed(...)` there resolves Lima's bundle for *every* site. The callback is invoked inside
 *   `runWithSite(slug)`, so its `hasFeed`/`loadFeed` reads bind to **that** site's bundle. With Lima
 *   alone the two forms are identical; a second selectable site is what makes the difference real.
 */
export function withSitePaths<P extends Record<string, unknown>, Q extends Record<string, unknown>>(
  itemPaths: Array<{ params: P; props?: Q }>,
): Array<{ params: P & { site: string }; props: Q & { slug: string } }>;
export function withSitePaths<P extends Record<string, unknown>, Q extends Record<string, unknown>>(
  itemPathsFor: (slug: string) => Array<{ params: P; props?: Q }>,
): Array<{ params: P & { site: string }; props: Q & { slug: string } }>;
export function withSitePaths(
  itemPaths:
    | Array<{ params: Record<string, unknown>; props?: Record<string, unknown> }>
    | ((slug: string) => Array<{ params: Record<string, unknown>; props?: Record<string, unknown> }>),
): Array<{ params: Record<string, unknown>; props: Record<string, unknown> }> {
  return selectableSitePaths().flatMap(({ params: siteParam, props: siteProps }) => {
    const items =
      typeof itemPaths === "function"
        ? runWithSite(siteProps.slug, () => itemPaths(siteProps.slug))
        : itemPaths;
    return items.map((it) => ({
      params: { ...it.params, ...siteParam },
      props: { ...(it.props ?? {}), ...siteProps },
    }));
  });
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
  "fort-wayne": "live", // GCP — a disclosed facility, not yet a construction record
};

/** A site's facility lifecycle stage; "investigation" when no facility is disclosed. */
export function facilityStatus(slug: string): FacilityStatus {
  return FACILITY_STATUS[slug] ?? "investigation";
}

export const FACILITY_STATUS_META: Record<
  FacilityStatus,
  { label: string; color: string; bg: string; dot: string }
> = {
  investigation: { label: "Investigating", color: "#566159", bg: "#e8e4d8", dot: "#8c9389" },
  confirmed: { label: "Confirmed", color: "#1f6f4a", bg: "#e4ece4", dot: "#1f6f4a" },
  construction: { label: "Under construction", color: "#9a6a14", bg: "#efe6d0", dot: "#9a6a14" },
  live: { label: "Live", color: "#1f6f4a", bg: "#e4ece4", dot: "#1f6f4a" },
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
  { status: "live", short: "Operational" },
];

/** The 0-based position of a facility status within `FACILITY_STAGES` — the rail's current step. */
export function facilityStageIndex(status: FacilityStatus): number {
  return FACILITY_STAGES.findIndex((s) => s.status === status);
}

// --- Grouped switcher (#307/#308 dictate C) --------------------------------------------------
// Canonical (state, basin) placement for every site. The selector pivots the SAME sites by
// either axis — `state` is the legal jurisdiction a record lives under; `basin` is the major
// river basin (one of nine) it documents. Both matter to a researcher, so either can be the
// outer grouping. The per-row `basin` subline carries the finer sub-watershed detail.
const PLACEMENT: Record<string, { state: string; basin: string }> = {
  lima: { state: "Ohio", basin: "Maumee" },
  "fort-wayne": { state: "Indiana", basin: "Maumee" },
  defiance: { state: "Ohio", basin: "Maumee" },
  findlay: { state: "Ohio", basin: "Maumee" },
  toledo: { state: "Ohio", basin: "Maumee" },
  "van-wert": { state: "Ohio", basin: "Maumee" },
  bryan: { state: "Ohio", basin: "Maumee" },
  ottawa: { state: "Ohio", basin: "Maumee" },
  // The Miami branches (Ohio River sink, not Lake Erie).
  urbana: { state: "Ohio", basin: "Great Miami" },
  springfield: { state: "Ohio", basin: "Great Miami" },
  xenia: { state: "Ohio", basin: "Little Miami" },
  wpafb: { state: "Ohio", basin: "Great Miami" },
  "hamilton-middletown": { state: "Ohio", basin: "Great Miami" },
  "troy-piqua": { state: "Ohio", basin: "Great Miami" },
  sidney: { state: "Ohio", basin: "Great Miami" },
  greenville: { state: "Ohio", basin: "Great Miami" },
  wilmington: { state: "Ohio", basin: "Little Miami" },
  // The Scioto branch (the data-center epicenter) and the remaining major basins.
  "new-albany": { state: "Ohio", basin: "Scioto" },
  columbus: { state: "Ohio", basin: "Scioto" },
  newark: { state: "Ohio", basin: "Muskingum" },
  zanesville: { state: "Ohio", basin: "Muskingum" },
  coshocton: { state: "Ohio", basin: "Muskingum" },
  fremont: { state: "Ohio", basin: "Sandusky" },
  tiffin: { state: "Ohio", basin: "Sandusky" },
  bucyrus: { state: "Ohio", basin: "Sandusky" },
  cleveland: { state: "Ohio", basin: "Cuyahoga" },
  akron: { state: "Ohio", basin: "Cuyahoga" },
  lordstown: { state: "Ohio", basin: "Mahoning" },
  youngstown: { state: "Ohio", basin: "Mahoning" },
  lancaster: { state: "Ohio", basin: "Hocking" },
  athens: { state: "Ohio", basin: "Hocking" },
  logan: { state: "Ohio", basin: "Hocking" },
};

/** The registry entry for a slug (the canonical {@link NetworkSite}), or `undefined`. */
export function siteForSlug(slug: string): NetworkSite | undefined {
  return SITES.find((s) => s.slug === slug);
}

/**
 * The legal jurisdiction (US state) a site's records live under — e.g. `"Ohio"`, `"Indiana"`.
 * The source for per-site datelines/kickers, so the site pages read it instead of hardcoding
 * "Lima, Ohio" (#741). Empty string for an unplaced slug.
 */
export function siteState(slug: string): string {
  return PLACEMENT[slug]?.state ?? "";
}

const STATE_ABBR: Record<string, string> = { Ohio: "OH", Indiana: "IN" };
const BASIN_ABBR: Record<string, string> = {
  Maumee: "MAU",
  "Great Miami": "GMI",
  "Little Miami": "LMI",
  Scioto: "SCI",
  Muskingum: "MUS",
  Sandusky: "SAN",
  Cuyahoga: "CUY",
  Mahoning: "MAH",
  Hocking: "HOC",
};

// Region super-groups (design "Site Selector") — the basin lens nests its nine basins under
// four regions so the panel reads geographically. Keyed by the display basin name.
const BASIN_REGION: Record<string, string> = {
  Maumee: "maumee",
  "Great Miami": "miamis",
  "Little Miami": "miamis",
  Scioto: "southeast",
  Muskingum: "southeast",
  Hocking: "southeast",
  Cuyahoga: "northeast",
  Mahoning: "northeast",
  Sandusky: "northeast",
};
const REGION_ORDER = ["maumee", "miamis", "southeast", "northeast"] as const;
const REGION_LABEL: Record<string, string> = {
  maumee: "Maumee Basin",
  miamis: "The Two Miamis",
  southeast: "Southeastern Basins",
  northeast: "Northeast Basins",
};
const REGION_ABBR: Record<string, string> = {
  maumee: "MAU",
  miamis: "2MI",
  southeast: "SE",
  northeast: "NE",
};
// Basin order within a region (the panel's row order); the basin lens walks REGION_ORDER then this.
const BASIN_ORDER = [
  "Maumee",
  "Great Miami",
  "Little Miami",
  "Scioto",
  "Muskingum",
  "Hocking",
  "Sandusky",
  "Cuyahoga",
  "Mahoning",
];

export type GroupBy = "state" | "basin";

export interface SiteGroup {
  /** Group heading (the state name, or the basin name). */
  label: string;
  /** Short tag shown beside the heading (the state abbr, or the 3-letter basin code). */
  tag: string;
  sites: NetworkSite[];
  /** Region super-group (basin lens only): set on the FIRST basin group of each region so the
   *  panel can render a region header bar before it. Absent in the state lens. */
  region?: string;
  regionLabel?: string;
  regionTag?: string;
  regionCount?: number;
  showRegion?: boolean;
}

/**
 * Group the registry by the State (jurisdiction) or Basin (the nine major river basins) axis —
 * the grouped selector's two lenses (#307/#308). The state lens groups by first appearance; the
 * basin lens nests basins under four regions (design "Site Selector"), walking REGION_ORDER then
 * the basin order within each region. Rows keep their registry order, so the same sites pivot
 * without reshuffling.
 */
export function groupSites(by: GroupBy): SiteGroup[] {
  if (by === "state") {
    const groups: SiteGroup[] = [];
    const index = new Map<string, SiteGroup>();
    for (const s of SITES) {
      const p = PLACEMENT[s.slug];
      if (!p) continue;
      let g = index.get(p.state);
      if (!g) {
        g = { label: p.state, tag: STATE_ABBR[p.state] ?? "", sites: [] };
        index.set(p.state, g);
        groups.push(g);
      }
      g.sites.push(s);
    }
    return groups;
  }

  // Basin lens — region super-groups, then basins within each region.
  const byBasin = new Map<string, NetworkSite[]>();
  for (const s of SITES) {
    const p = PLACEMENT[s.slug];
    if (!p) continue;
    const arr = byBasin.get(p.basin);
    if (arr) arr.push(s);
    else byBasin.set(p.basin, [s]);
  }
  const groups: SiteGroup[] = [];
  for (const region of REGION_ORDER) {
    const basins = BASIN_ORDER.filter((b) => BASIN_REGION[b] === region && byBasin.has(b));
    const regionCount = basins.reduce((n, b) => n + (byBasin.get(b)?.length ?? 0), 0);
    basins.forEach((b, i) => {
      groups.push({
        label: b,
        tag: BASIN_ABBR[b] ?? "",
        sites: byBasin.get(b) ?? [],
        region,
        regionLabel: REGION_LABEL[region],
        regionTag: REGION_ABBR[region],
        regionCount,
        showRegion: i === 0,
      });
    });
  }
  return groups;
}
