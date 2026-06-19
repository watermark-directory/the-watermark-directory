/**
 * The BOSC network — the registry of watershed-point sites (the multi-site pivot, #304).
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
