/**
 * Build-time data for the Water chapter's dilution screen (#222) — "the river is
 * effluent." The campus's net **consumptive** cooling draw, set against the
 * Ottawa River's low-flow floors, season by season.
 *
 * The draw model is read from the `hydrology-scenarios` feed (the same numbers the
 * hydrology dashboard renders — no fork): the cited `buildout` scenario's cooling
 * demand, consumptive fraction, and resulting consumptive loss. The annual 7Q10
 * floor is the feed's `ottawa_7q10`; the seasonal floors (summer 30Q10, driest
 * 1Q10) are the cited values from `data/reference/hydrology/low-flow-7q10.yaml`.
 *
 * NOT client-safe (imports the node bundle loader); the island consumes the plain
 * `DilutionData` object this returns, passed as a prop.
 *
 * Discipline: comparing a withdrawal to a stream's low flow is a **worst-case
 * bound** — Lima's supply is reservoir-buffered, not a direct low-flow river
 * abstraction — so the chapter carries the ratio as `[inference]`, not a record
 * read. The numbers here are real; the framing stays flagged.
 */
import { hasFeed, loadFeed } from "./bundle";
import type { ScenarioResult } from "./feeds";

export interface DilutionFloor {
  key: "annual" | "summer" | "driest";
  label: string;
  /** The river's low-flow floor, cfs. */
  cfs: number;
  cite: string;
  note?: string;
}

export interface DilutionData {
  /** Max cooling draw of the cited buildout scenario, MGD. */
  maxCoolingMgd: number;
  /** Consumptive fraction (buildout assumption). */
  consumptiveFraction: number;
  /** Net consumptive draw per MGD of cooling, cfs (bakes in cfrac × MGD→cfs). */
  cfsPerCoolingMgd: number;
  /** Net consumptive draw at full buildout, cfs (feed-sourced). */
  drawAtBuildoutCfs: number;
  /** The Ottawa's live USGS flow, cfs (context — the dashboard re-runs on it). */
  ottawaLiveCfs: number | null;
  /** Receiving-stream low-flow floors: annual + the seasonal pinch (cited). */
  floors: DilutionFloor[];
  /** True when the buildout scenario resolved from the feed (else curated fallback). */
  fromFeed: boolean;
}

// MGD → cfs (1 million gallons/day = 1.547 cubic feet/second). A standard unit
// conversion, used only as the fallback slope when the feed is absent.
const CFS_PER_MGD = 1.547;

const OTTAWA_SEASONAL_CITE =
  "data/reference/hydrology/low-flow-7q10.yaml · Ottawa River context (Ohio EPA NPDES 2IG00001, USGS 04187100)";

export function buildDilution(): DilutionData {
  const scenarios = hasFeed("hydrology-scenarios") ? loadFeed<ScenarioResult[]>("hydrology-scenarios") : [];
  const buildout = scenarios.find((s) => s.scenario.name === "buildout");

  // Feed-sourced (no fork); curated fallbacks only for the minimal CI fixture.
  const maxCoolingMgd = buildout?.scenario.cooling_demand.value ?? 3.92;
  const consumptiveFraction = buildout?.scenario.consumptive_fraction.value ?? 0.8;
  const drawAtBuildoutCfs =
    buildout?.consumptive_loss.value ?? maxCoolingMgd * consumptiveFraction * CFS_PER_MGD;
  const annual7q10 = buildout?.ottawa_7q10.value ?? 0.2;
  const ottawaLiveCfs = buildout?.ottawa_live.value ?? null;
  const cfsPerCoolingMgd =
    maxCoolingMgd > 0 ? drawAtBuildoutCfs / maxCoolingMgd : consumptiveFraction * CFS_PER_MGD;

  const floors: DilutionFloor[] = [
    {
      key: "annual",
      label: "Annual 7Q10",
      cfs: annual7q10,
      cite: "Ohio EPA NPDES fact sheet 2IG00001 (Ottawa at Lima, USGS 04187100)",
    },
    {
      key: "summer",
      label: "Summer 30Q10",
      cfs: 1.6,
      cite: OTTAWA_SEASONAL_CITE,
      note: "the May–Oct pinch — when the cooling draw also peaks",
    },
    {
      key: "driest",
      label: "Driest week 1Q10",
      cfs: 0.0,
      cite: OTTAWA_SEASONAL_CITE,
      note: "the Ottawa mainstem nearly dries — 1Q10 = 0 cfs",
    },
  ];

  return {
    maxCoolingMgd,
    consumptiveFraction,
    cfsPerCoolingMgd,
    drawAtBuildoutCfs,
    ottawaLiveCfs,
    floors,
    fromFeed: !!buildout,
  };
}

/** Net consumptive draw (cfs) at a given cooling demand (MGD), per the model. */
export function drawCfs(data: DilutionData, coolingMgd: number): number {
  return coolingMgd * data.cfsPerCoolingMgd;
}

/** Draw ÷ floor — how many times the river's low flow the draw is.
 *  `Infinity` when the floor is zero (the river is gone). */
export function dilutionMultiple(drawCfsValue: number, floorCfs: number): number {
  return floorCfs > 0 ? drawCfsValue / floorCfs : Number.POSITIVE_INFINITY;
}
