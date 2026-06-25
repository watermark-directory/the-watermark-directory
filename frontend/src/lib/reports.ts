/**
 * The interactive-report registry (#584) — the single source for which narrative
 * essays have an interactive companion page under `/reports/<slug>` and what they're
 * called. Previously the slug→href map was hardcoded twice: the reports index
 * (`reports/index.astro`, deciding the companion link + "interactive" badge) and the
 * public balance sheet (`balanceSheet.ts`, linking each band back to its narrative).
 *
 * The slug is also the docs-essay slug (`docs/<slug>.md`); a report with no companion
 * falls back to that essay. URLs are built with `siteUrl` (site-base only, no deploy
 * base) so both call sites stay byte-identical — the index wraps the result in
 * `withBase`, the client-safe balance sheet consumes it raw.
 */
import { siteUrl } from "./routes";

export interface ReportEntry {
  /** `/reports/<slug>` and `docs/<slug>.md`. */
  slug: string;
  /** Display title — the narrative's name. */
  label: string;
}

/** Reports whose essay has an interactive companion page (the SSOT slug list). */
export const INTERACTIVE_REPORTS: ReportEntry[] = [
  { slug: "end-use-and-workloads", label: "End use & workloads" },
  { slug: "defense-nexus", label: "The defense nexus" },
  { slug: "the-economic-ledger", label: "The economic ledger" },
  { slug: "toxics-and-the-corridor", label: "Toxics and the corridor" },
  { slug: "the-load-and-the-grid", label: "The load and the grid" },
];

const BY_SLUG = new Map(INTERACTIVE_REPORTS.map((r) => [r.slug, r]));

/** The companion page URL for a report slug (site-base only; caller applies the deploy base). */
export function reportUrl(slug: string): string {
  return siteUrl(`/reports/${slug}`);
}

/** True when the report has an interactive companion (vs only the docs essay). */
export function hasInteractive(slug: string): boolean {
  return BY_SLUG.has(slug);
}
