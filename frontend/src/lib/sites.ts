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

/** Site lifecycle. `live` = built + selectable; `onboarding` = real facility, build queued;
 *  `open` = a tracked basin site, not yet started. Only `live` is selectable. */
export type SiteStatus = "live" | "onboarding" | "open";

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
    status: "onboarding",
    selectable: false,
    issue: "235",
    href: "/network/fort-wayne",
  },
  {
    slug: "defiance",
    codename: null,
    mono: "DEF",
    place: "Defiance",
    basin: "Maumee mainstem",
    status: "open",
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
    status: "open",
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
    status: "open",
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
    status: "open",
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
    status: "open",
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
    status: "open",
    selectable: false,
    issue: "381",
    href: "/network/ottawa",
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
 * `/network/<slug>[/…]` → that site (incl. the not-yet-built ones). The network hub
 * (`/network`) and the cross-cutting globals (`/about`, `/wiki`, `/ask`) belong to no
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
 * The build `status` (live/onboarding/open) tracks our progress assembling the *website*; this
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
