/**
 * Grid load-band simulator (epic #271 Phase 2, #265). The headline "313 MW" is backup,
 * not load, and the per-engine rating behind it is redacted in the issued permit — so the
 * working load is an inference chain (313 backup → IT via N+1 → ×PUE → facility ~348 MW),
 * and that chain IS the uncertainty. Disclose the operating load and the band collapses;
 * the load-not-jobs bars hold the finding that survives both disciplines. Reuses the
 * uncertainty engine + grammar.
 */
import { useMemo, useState } from "react";
import {
  AEP_OHIO_RETAIL_GWH,
  BACKUP_MW,
  GRID_PRIORS,
  PROMISED_JOBS,
  annualGwh,
  equivalentHomes,
  facilityDrawModel,
  mwPerJob,
  pctOfAepRetail,
} from "../../lib/gridLoad";
import {
  DEFAULT_SEED,
  type Prior,
  central,
  disclose,
  outcomeBand,
  sample,
  summarize,
} from "../../lib/uncertainty";
import { fmtMw } from "../../lib/format";
import { DistributionStrip, RegisterMark } from "./uncertaintyGrammar";

const priorCentral = (key: string): number => {
  const p = GRID_PRIORS.find((x) => x.key === key);
  return p ? central(p.dist) : 0;
};

export default function GridLoadScreen(): JSX.Element {
  const [disclosed, setDisclosed] = useState<Record<string, boolean>>({});

  const effectivePriors: Prior[] = useMemo(() => {
    let priors = GRID_PRIORS;
    for (const key of Object.keys(disclosed)) {
      if (disclosed[key]) priors = disclose(priors, key, priorCentral(key));
    }
    return priors;
  }, [disclosed]);

  const band = useMemo(() => outcomeBand(effectivePriors, facilityDrawModel), [effectivePriors]);
  const summary = useMemo(
    () => summarize(sample(effectivePriors, facilityDrawModel, 6000, DEFAULT_SEED), 24),
    [effectivePriors],
  );
  const baseline = useMemo(() => outcomeBand(GRID_PRIORS, facilityDrawModel), []);

  // The load-not-jobs figures, read off the central inferred facility draw + IT load.
  const gwh = annualGwh(band.central);
  const itCentral = priorCentral("it_load");
  const halfWidth = (band.high - band.low) / 2;

  return (
    <div className="unc unc-grid">
      <div className="unc-band-head">
        <div className="unc-band-figure">
          {fmtMw(band.low)} – {fmtMw(band.high)}
        </div>
        <div className="unc-band-sub">
          inferred facility draw · ±{fmtMw(halfWidth)}{" "}
          {Object.values(disclosed).some(Boolean)
            ? "(narrowed by disclosure)"
            : "(the band the redaction leaves)"}
        </div>
      </div>

      <div className="unc-chain">
        <span className="unc-chain-step">
          <RegisterMark register="verified" /> {BACKUP_MW} MW backup <em>(draft)</em>
        </span>
        <span className="unc-chain-arrow">→</span>
        <span className="unc-chain-step">
          <RegisterMark register="assumption" /> IT load (N+1)
        </span>
        <span className="unc-chain-arrow">→</span>
        <span className="unc-chain-step">
          <RegisterMark register="assumption" /> × PUE = facility draw
        </span>
      </div>

      <DistributionStrip
        low={band.low}
        central={band.central}
        high={band.high}
        p10={summary.p10}
        p90={summary.p90}
        bins={summary.bins}
        domain={[Math.floor(baseline.low) - 3, Math.ceil(baseline.high) + 3]}
        ghost={{ low: baseline.low, high: baseline.high }}
        register="inference"
        format={fmtMw}
      />

      <h4 className="unc-h4">Produce a record → collapse the inference</h4>
      <div className="unc-disclose">
        {GRID_PRIORS.map((p) => (
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

      <h4 className="unc-h4">Load, not jobs</h4>
      <dl className="unc-readout">
        <Stat
          label="Annual energy"
          value={`${Math.round(gwh).toLocaleString("en-US")} GWh/yr`}
          reg="inference"
        />
        <Stat
          label="Share of AEP Ohio retail sales"
          value={`${pctOfAepRetail(gwh).toFixed(1)}% of ${AEP_OHIO_RETAIL_GWH.toLocaleString("en-US")} GWh`}
          reg="verified"
          strong
        />
        <Stat
          label="Equivalent Ohio homes"
          value={`~${Math.round(equivalentHomes(gwh) / 1000)}k homes`}
          reg="inference"
        />
        <Stat label="Promised jobs" value={`~${PROMISED_JOBS}`} reg="verified" />
        <Stat
          label="Load per job"
          value={`~${mwPerJob(itCentral).toFixed(1)} MW / job`}
          reg="inference"
          strong
        />
      </dl>

      <p className="unc-note">
        <strong>313 MW is backup, not load.</strong> The per-engine rating that pins it is redacted in the
        issued permit — the band above exists <em>because</em> the record is withheld. "Behind-the-meter" is a
        proponent claim <code>[open]</code>: the campus is a PUCO-regulated <strong>retail</strong> customer
        of AEP Ohio (the 114 gensets are emergency backup, not primary generation). PJM dollar figures are a
        <code>[reference]</code> screen, not a finding. What survives is the load: ~5–6% of a utility's entire
        retail electricity, ~260k homes of it, for ~50 jobs.
      </p>
    </div>
  );
}

function Stat({
  label,
  value,
  reg,
  strong,
}: {
  label: string;
  value: string;
  reg: "verified" | "assumption" | "inference" | "open";
  strong?: boolean;
}): JSX.Element {
  return (
    <div className={`unc-line${strong ? " is-strong" : ""}`}>
      <dt>
        <RegisterMark register={reg} /> {label}
      </dt>
      <dd>{value}</dd>
    </div>
  );
}
