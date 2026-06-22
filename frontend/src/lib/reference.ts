/**
 * The reference-data collection (Pages cutover Gap C, #104): the authoritative
 * external datasets' READMEs under `data/reference/`, surfaced in-site.
 *
 * Like `lib/narrative.ts`, this is the single source of truth for which reference
 * READMEs are published, their slugs/titles, and (via `PUBLISHED_REFERENCE`) the
 * link-rewrite map the rehype plugin consults so `../<set>/README.md` cross-links
 * between reference pages resolve to their new `/bosc/site/reference/<slug>` routes.
 *
 * The READMEs are read AS-IS — source is never moved or edited.
 */
export interface ReferenceDataset {
  /** Path under `data/reference/` (the README). */
  repo: string;
  /** Route slug under `/bosc/site/reference/`. */
  slug: string;
  title: string;
  blurb: string;
}

export const REFERENCE: ReferenceDataset[] = [
  {
    repo: "echo/README.md",
    slug: "echo",
    title: "Maumee NPDES inventory (EPA ECHO)",
    blurb: "The EPA ECHO wastewater-discharger inventory for the Maumee basin (NPDES permits).",
  },
  {
    repo: "allen-gis/README.md",
    slug: "allen-gis",
    title: "Allen County parcels (CAMA)",
    blurb: "Parcel ownership / situs / acreage from the Allen County GIS Current Parcels layer.",
  },
  {
    repo: "lima-gis/README.md",
    slug: "lima-gis",
    title: "Lima zoning districts",
    blurb: "City of Lima zoning districts (and the FEMA DFIRM floodzone) from the city GIS.",
  },
  {
    repo: "rsei/README.md",
    slug: "rsei",
    title: "RSEI toxic-release inventory (EPA)",
    blurb: "The EPA RSEI Public Data Set reduced to Allen County's toxic-release facilities.",
  },
  {
    repo: "gleif/README.md",
    slug: "gleif",
    title: "Entity LEIs (GLEIF)",
    blurb: "GLEIF Legal Entity Identifier resolution for corridor entity parents.",
  },
  {
    repo: "economics/README.md",
    slug: "economics",
    title: "Economic baseline (BLS QCEW / Census)",
    blurb: "Allen County employment (BLS QCEW) and population (Census ACS) — the localized baseline.",
  },
  {
    repo: "hydrology/wbd/README.md",
    slug: "wbd",
    title: "USGS watershed boundaries (WBD)",
    blurb: "The USGS Watershed Boundary Dataset HUC boundaries framing the campus AOI.",
  },
];

/** Repo paths (under data/reference/) of the published READMEs. */
export const PUBLISHED_REFERENCE: Set<string> = new Set(REFERENCE.map((d) => `data/reference/${d.repo}`));

/** slug for a published reference repo path, or "" if not published. */
export function refSlugForRepoPath(repoPath: string): string {
  const d = REFERENCE.find((r) => `data/reference/${r.repo}` === repoPath);
  return d ? d.slug : "";
}

export const refBySlug = new Map(REFERENCE.map((d) => [d.slug, d]));
