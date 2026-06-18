/**
 * The economic-ledger simulator (epic #271 flagship, #269) — the cost-of-opacity made
 * manipulable. Default: profile tabs + sliders over the four withheld knobs, recomputing
 * the 15-year public ledger (a point). "Show the full distribution": the knobs become
 * `[assumption]`/`[open]` priors → a Monte-Carlo band over the net subsidy per job, a
 * tornado ranking the knobs, and a "produce this record" toggle per knob that collapses
 * the band — the mandamus grievance turned into a measured ±$ tighten.
 *
 * Discipline: the priors are industry reference, not this campus; GovCloud is a what-if,
 * not a defense finding; the output is a band, not a verdict. Reproducible (seeded) so the
 * island matches the SSR fallback in the page.
 */
import { useMemo, useState } from "react";
import {
  COUNTY_JOBS_2023,
  ECON_PRIORS,
  abatement,
  abatementPerJob,
  keptByPublic,
  ledgerProfiles,
  netSubsidyModel,
  netSubsidyPerJobModel,
  salesTaxExemption,
} from "../../lib/econLedger";
import { fmtUsdM } from "../../lib/money";
import {
  DEFAULT_SEED,
  type Prior,
  central,
  disclose,
  outcomeBand,
  sample,
  summarize,
  tornado,
} from "../../lib/uncertainty";
import { DistributionStrip, RegisterMark, TornadoChart } from "./uncertaintyGrammar";

const REFRESH_CENTRAL = 1.5;
const PROFILES = ledgerProfiles();
const PRIOR_BY_KEY = new Map(ECON_PRIORS.map((p) => [p.key, p]));

function priorCentral(key: string): number {
  const p = PRIOR_BY_KEY.get(key);
  return p ? central(p.dist) : 0;
}

export default function EconLedgerSimulator(): JSX.Element {
  const [mode, setMode] = useState<"discrete" | "distribution">("discrete");

  // Discrete-mode point inputs (default = the "stated" profile).
  const [share, setShare] = useState(0.35);
  const [jobs, setJobs] = useState(50);
  const [schoolComp, setSchoolComp] = useState(0);
  const [dcte, setDcte] = useState(true);
  const [activeProfile, setActiveProfile] = useState<string>("stated");

  // Distribution-mode disclosures (which knobs have been "produced").
  const [disclosed, setDisclosed] = useState<Record<string, boolean>>({});

  function pickProfile(key: string): void {
    const p = PROFILES.find((x) => x.key === key);
    if (!p) return;
    setActiveProfile(key);
    setShare(p.buildingShare);
    setJobs(p.jobs);
  }

  // --- discrete point ledger ---
  const point = useMemo(() => {
    const ab = abatement(share);
    const ex = dcte ? salesTaxExemption(share, REFRESH_CENTRAL) : 0;
    return {
      abatement: ab,
      kept: keptByPublic(share),
      exemption: ex,
      net: ab + ex - schoolComp,
      perJob: abatementPerJob(share, jobs),
      jobsPct: (jobs / COUNTY_JOBS_2023) * 100,
    };
  }, [share, jobs, schoolComp, dcte]);

  // --- distribution: priors with disclosed knobs collapsed to their central ---
  const effectivePriors: Prior[] = useMemo(() => {
    let priors = ECON_PRIORS;
    for (const key of Object.keys(disclosed)) {
      if (disclosed[key]) priors = disclose(priors, key, priorCentral(key));
    }
    return priors;
  }, [disclosed]);

  const sim = useMemo(() => {
    const perJobModel = netSubsidyPerJobModel(dcte);
    const netModel = netSubsidyModel(dcte);
    const outcomes = sample(effectivePriors, perJobModel, 6000, DEFAULT_SEED);
    const summary = summarize(outcomes, 28);
    const perJobBand = outcomeBand(effectivePriors, perJobModel);
    const netBand = outcomeBand(effectivePriors, netModel);
    const bars = tornado(effectivePriors, perJobModel).map((b) => ({ ...b }));
    return { summary, perJobBand, netBand, bars };
  }, [effectivePriors, dcte]);

  // Fixed axes from the fully-undisclosed band, so the collapse is visible against them.
  const baseline = useMemo(() => {
    const perJobModel = netSubsidyPerJobModel(true);
    return {
      perJob: outcomeBand(ECON_PRIORS, perJobModel),
      net: outcomeBand(ECON_PRIORS, netSubsidyModel(true)),
    };
  }, []);

  const allDisclosed = ECON_PRIORS.every((p) => disclosed[p.key]);
  const halfWidthM = (sim.perJobBand.high - sim.perJobBand.low) / 2;

  return (
    <div className="unc unc-econ">
      <div className="unc-modebar" role="tablist" aria-label="View">
        <button
          type="button"
          role="tab"
          aria-selected={mode === "discrete"}
          className={`unc-modebtn${mode === "discrete" ? " is-active" : ""}`}
          onClick={() => setMode("discrete")}
        >
          Scenario
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "distribution"}
          className={`unc-modebtn${mode === "distribution" ? " is-active" : ""}`}
          onClick={() => setMode("distribution")}
        >
          Show the full distribution
        </button>
      </div>

      {mode === "discrete" ? (
        <div className="unc-discrete">
          <div className="unc-tabs" role="group" aria-label="Facility profile">
            {PROFILES.map((p) => (
              <button
                key={p.key}
                type="button"
                className={`unc-tab${activeProfile === p.key ? " is-active" : ""}`}
                onClick={() => pickProfile(p.key)}
              >
                {p.label}
              </button>
            ))}
          </div>

          <div className="unc-sliders">
            <Slider
              label="Building (abated) share of the $500M"
              value={share}
              min={0.2}
              max={0.45}
              step={0.01}
              onChange={(v) => {
                setShare(v);
                setActiveProfile("custom");
              }}
              fmt={(v) => `${Math.round(v * 100)}%`}
              register="assumption"
            />
            <Slider
              label="Steady-state jobs"
              value={jobs}
              min={30}
              max={50}
              step={1}
              onChange={(v) => {
                setJobs(v);
                setActiveProfile("custom");
              }}
              fmt={(v) => `${v}`}
              register="assumption"
            />
            <Slider
              label="School District Compensation (offset)"
              value={schoolComp}
              min={0}
              max={30_000_000}
              step={1_000_000}
              onChange={setSchoolComp}
              fmt={(v) => fmtUsdM(v)}
              register="open"
            />
            <label className="unc-toggle">
              <input type="checkbox" checked={dcte} onChange={(e) => setDcte(e.target.checked)} />
              Campus takes the sales-tax exemption (DCTE) <RegisterMark register="open" />
            </label>
          </div>

          <dl className="unc-readout">
            <Line label="Property-tax abatement" value={fmtUsdM(point.abatement)} register="inference" />
            <Line
              label="Sales-tax exemption"
              value={dcte ? fmtUsdM(point.exemption) : "not taken"}
              register="open"
            />
            <Line label="Un-abated tax (public keeps)" value={fmtUsdM(point.kept)} register="inference" />
            <Line label="Net public subsidy" value={fmtUsdM(point.net)} register="inference" strong />
            <Line label="Per job (abatement)" value={fmtUsdM(point.perJob)} register="open" />
            <Line
              label="Jobs vs. the county"
              value={`${jobs} ≈ ${point.jobsPct.toFixed(2)}% of ${COUNTY_JOBS_2023.toLocaleString("en-US")}`}
              register="verified"
            />
          </dl>
          <p className="unc-note">
            A single scenario — the record pins none of these. Switch to the full distribution to see the
            band, and what disclosing each record would do.
          </p>
        </div>
      ) : (
        <div className="unc-distribution">
          <div className="unc-band-head">
            <div className="unc-band-figure">
              {fmtUsdM(sim.perJobBand.low)} – {fmtUsdM(sim.perJobBand.high)}
            </div>
            <div className="unc-band-sub">
              net public subsidy <strong>per job</strong> · ±{fmtUsdM(halfWidthM)}{" "}
              {allDisclosed ? "(fully disclosed → a point)" : "(the band the record withholds)"}
            </div>
          </div>
          <DistributionStrip
            low={sim.perJobBand.low}
            central={sim.perJobBand.central}
            high={sim.perJobBand.high}
            p10={sim.summary.p10}
            p90={sim.summary.p90}
            bins={sim.summary.bins}
            domain={[baseline.perJob.low, baseline.perJob.high]}
            ghost={{ low: baseline.perJob.low, high: baseline.perJob.high }}
            register={allDisclosed ? "verified" : "open"}
            format={fmtUsdM}
          />
          <div className="unc-band-sub unc-band-net">
            15-year net subsidy (total):{" "}
            <strong>
              {fmtUsdM(sim.netBand.low)} – {fmtUsdM(sim.netBand.high)}
            </strong>{" "}
            for ~{jobs} jobs
          </div>

          <h4 className="unc-h4">Which withheld record moves it most</h4>
          <TornadoChart
            bars={sim.bars}
            domain={[baseline.perJob.low, baseline.perJob.high]}
            format={fmtUsdM}
          />

          <h4 className="unc-h4">Produce a record → collapse the band</h4>
          <div className="unc-disclose">
            {ECON_PRIORS.map((p) => (
              <label key={p.key} className={`unc-disclose-row${disclosed[p.key] ? " is-disclosed" : ""}`}>
                <input
                  type="checkbox"
                  checked={!!disclosed[p.key]}
                  onChange={(e) => setDisclosed((d) => ({ ...d, [p.key]: e.target.checked }))}
                />
                <span className="unc-disclose-label">
                  <RegisterMark register={p.register} /> {p.label}
                </span>
                <span className="unc-disclose-rec">{disclosed[p.key] ? "disclosed" : p.resolvingRecord}</span>
              </label>
            ))}
          </div>
          <p className="unc-note">
            Each toggle pins one withheld figure to its reference value and re-prices the opacity. The record
            pins none of these today — that is the finding, in dollars.
          </p>
        </div>
      )}
    </div>
  );
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  onChange,
  fmt,
  register,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  fmt: (v: number) => string;
  register: "verified" | "assumption" | "open";
}): JSX.Element {
  return (
    <label className="unc-slider">
      <span className="unc-slider-label">
        <RegisterMark register={register} /> {label}
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <span className="unc-slider-val">{fmt(value)}</span>
    </label>
  );
}

function Line({
  label,
  value,
  register,
  strong,
}: {
  label: string;
  value: string;
  register: "verified" | "assumption" | "inference" | "open";
  strong?: boolean;
}): JSX.Element {
  return (
    <div className={`unc-line${strong ? " is-strong" : ""}`}>
      <dt>
        <RegisterMark register={register} /> {label}
      </dt>
      <dd>{value}</dd>
    </div>
  );
}
