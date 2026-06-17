/**
 * Build-time data for the Cost chapter's follow-the-money flow (#222 → #223).
 * The public's roadwork money, traced: $14.5M "Company Contribution" collected up
 * front → the Tetra Tech OPC estimate (6 corridor line items) → the first actual
 * award (Eagle Bridge, far under) → the §5.5 grant-refund arrow back to the
 * developer. Plus the parallel abatement strand.
 *
 * The OPC line items + total are read from the `records` feed (the same numbers
 * the library renders — no fork). The contribution, the actual award, and the
 * abatement terms are cited constants from the committed extractions (the RDA, the
 * PAAC minutes, the CRA, ECONOMICS.md) — those records aren't in the `records`
 * feed. NOT client-safe (imports the node bundle loader); the island consumes the
 * plain `MoneyFlowData` object this returns, passed as a prop.
 *
 * Discipline: the §5.5 refund consequence is flagged `[inference]` (it turns on
 * grant awards not in the document). The **abatement value per job is NOT
 * fabricated** — the School District Compensation terms that would pin it are
 * non-public (`cra-agreement.cra.yaml` `amounts_public: false`), so it is carried
 * as withheld, not invented.
 */
import { hasFeed, loadFeed } from "./bundle";
import type { RecordItem } from "./feeds";

export { fmtUsd, fmtUsdFull } from "./money";

export interface MoneyNode {
  name: string;
  usd: number;
}

export interface MoneyFlowData {
  /** "Company Contribution" collected up front (RDA §3.2(a)). */
  collectedUsd: number;
  collectedCite: string;
  /** Tetra Tech OPC construction total (feed). */
  opcTotalUsd: number;
  /** The 6 OPC corridor line items (feed). */
  opcItems: MoneyNode[];
  /** True when the OPC resolved from the records feed (else curated fallback). */
  opcFromFeed: boolean;
  /** The first actual construction award — Eagle Bridge, N. Cole (PAAC minutes). */
  firstAward: { label: string; usd: number; cite: string };
  /** The §5.5 grant-refund consequence, flagged [inference]. */
  refund: { note: string; cite: string };
  /** The parallel abatement strand — verified components; per-job $ withheld. */
  abatement: {
    pct: number;
    years: number;
    buildUsd: number;
    jobs: number;
    payrollUsd: number;
    taxBase: string;
    /** False — the School District Compensation $ are non-public. */
    schoolTermsPublic: boolean;
    cite: string;
  };
}

const OPC_REL = "aedg/roundabouts.summary.opc.yaml";

/** Curated OPC fallback (the 6 line items), for the minimal CI fixture only. */
const FALLBACK_OPC: MoneyNode[] = [
  { name: "Cole Street / Diller Road Roundabout", usd: 1535218 },
  { name: "Cole Street / Bluelick Road Roundabout", usd: 1704502 },
  { name: "Primary Access Entrance to Project Site (Roundabout)", usd: 2663045 },
  { name: "Cole Street / West Street (SR 115) Roundabout", usd: 2249609 },
  { name: "Cole Street Corridor", usd: 3899800 },
  { name: "Bluelick Road Corridor", usd: 2180907 },
];

interface OpcSubEstimate {
  name?: string | null;
  total?: number | null;
}

export function buildMoneyFlow(): MoneyFlowData {
  const records = hasFeed("records") ? loadFeed<RecordItem[]>("records") : [];
  const opc = records.find((r) => r.rel === OPC_REL);

  const meta = (opc?.fields.meta ?? null) as { summary_construction_total?: number } | null;
  const subs = (opc?.fields.sub_estimates ?? null) as OpcSubEstimate[] | null;
  const opcItems: MoneyNode[] =
    subs && subs.length > 0 ? subs.map((s) => ({ name: s.name ?? "—", usd: s.total ?? 0 })) : FALLBACK_OPC;
  const opcTotalUsd = meta?.summary_construction_total ?? opcItems.reduce((a, b) => a + b.usd, 0);

  return {
    collectedUsd: 14_500_000,
    collectedCite: "RDA §3.2(a) — one-time Company Contribution, due within 30 business days",
    opcTotalUsd,
    opcItems,
    opcFromFeed: !!opc,
    firstAward: {
      label: "Eagle Bridge · N. Cole design-build (first award)",
      usd: 3_520_000,
      cite: "PAAC board minutes 2026-04-23 (p.78) — ~$3.52M; the rest of the program is still being awarded",
    },
    refund: {
      note: "§5.5 — if certified Total Cost is less than the Contribution + public grants, the surplus is refunded to the Company; grants received later are likewise refunded.",
      cite: "RDA §5.5 Overpayment Amount · turns on grant awards not in the document",
    },
    abatement: {
      pct: 75,
      years: 15,
      buildUsd: 500_000_000,
      jobs: 50,
      payrollUsd: 4_000_000,
      taxBase: "Elida Local School District",
      schoolTermsPublic: false,
      cite: "CRA No. 1 (Res #548-25) · docs/ECONOMICS.md — ~$500M build, 15-yr/75%, ~50 jobs / ~$4M payroll",
    },
  };
}
