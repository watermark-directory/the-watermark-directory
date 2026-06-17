/**
 * Dilution-screen island (#222) — "the river is effluent." Scrub the campus
 * cooling draw and the season, and watch the net **consumptive** draw cross the
 * Ottawa's low flow: ~24× the annual 7Q10, ~3× the summer 30Q10 (the seasonal
 * pinch), and against the driest-week 1Q10 (0 cfs) there is no river left to
 * dilute into. Mounted `client:only` over the page's SSR seasonal table; the
 * numbers are the build-time `DilutionData` (the hydrology feed's own — no fork).
 *
 * Discipline: the draw-vs-low-flow ratio is a worst-case bound (Lima's supply is
 * reservoir-buffered), carried as [inference] — surfaced on the figure itself.
 */
import { useId, useState } from "react";
import type { DilutionData, DilutionFloor } from "../../lib/dilution";

function fmtMult(m: number): string {
  if (!Number.isFinite(m)) return "∞×";
  if (m >= 10) return `${Math.round(m)}×`;
  return `${m.toFixed(1)}×`;
}

export default function DilutionScreen({ data }: { data: DilutionData }): JSX.Element {
  const [coolingMgd, setCoolingMgd] = useState(data.maxCoolingMgd);
  const [seasonKey, setSeasonKey] = useState<DilutionFloor["key"]>("summer");
  const sliderId = useId();

  const floor = data.floors.find((f) => f.key === seasonKey) ?? data.floors[0];
  const draw = coolingMgd * data.cfsPerCoolingMgd;
  const multiple = floor.cfs > 0 ? draw / floor.cfs : Number.POSITIVE_INFINITY;
  const dry = floor.cfs <= 0;

  // Axis = the larger of river floor and draw, so the draw overflows the river
  // bar visibly; a small floor keeps a thread of river showing when it's ~0.
  const axisMax = Math.max(draw, floor.cfs, 0.01);
  const riverPct = Math.max((floor.cfs / axisMax) * 100, dry ? 0 : 1);
  const drawPct = Math.min((draw / axisMax) * 100, 100);

  return (
    <div
      className="dil"
      role="figure"
      aria-label="Interactive dilution screen: the campus consumptive cooling draw against the Ottawa River's low flow by season. The same figures are in the seasonal table on this page."
    >
      <div className="dil-head">
        <strong>The dilution screen</strong>
        <span
          className="dil-tag"
          title="A withdrawal-vs-low-flow comparison is a worst-case bound — Lima's supply is reservoir-buffered, not a direct low-flow river abstraction."
        >
          [inference] · worst-case bound
        </span>
      </div>

      <div className="dil-bars">
        <div className="dil-barrow">
          <div className="dil-barlabel">
            Ottawa · {floor.label}
            <span className="dil-barnum">{floor.cfs.toFixed(2)} cfs</span>
          </div>
          <div className="dil-track">
            <div className="dil-bar dil-bar--river" style={{ width: `${riverPct}%` }} />
            {dry && <div className="dil-dry">dry — 0 cfs</div>}
          </div>
        </div>
        <div className="dil-barrow">
          <div className="dil-barlabel">
            Campus consumptive draw
            <span className="dil-barnum">{draw.toFixed(2)} cfs</span>
          </div>
          <div className="dil-track">
            <div className="dil-bar dil-bar--draw" style={{ width: `${drawPct}%` }} />
          </div>
        </div>
      </div>

      <div className="dil-readout" role="status" aria-live="polite" aria-label="Dilution result">
        <span className="dil-mult">{dry ? "there is no river" : `${fmtMult(multiple)} the river`}</span>
        <span className="dil-readsub">
          {dry
            ? "the draw exceeds the entire driest-week flow — nothing to dilute into"
            : `the consumptive draw is ${fmtMult(multiple)} the Ottawa's ${floor.label.toLowerCase()}`}
        </span>
      </div>

      <div className="dil-controls">
        <label className="dil-slabel" htmlFor={sliderId}>
          Cooling draw
          <span className="dil-snum">
            {coolingMgd.toFixed(2)} MGD
            <span className="card-meta"> · {data.maxCoolingMgd.toFixed(2)} at full buildout</span>
          </span>
        </label>
        <input
          id={sliderId}
          className="dil-slider"
          type="range"
          min={0}
          max={data.maxCoolingMgd}
          step={data.maxCoolingMgd / 100}
          value={coolingMgd}
          aria-label="Campus cooling draw, million gallons per day"
          onChange={(e) => setCoolingMgd(Number(e.target.value))}
        />
        <div className="dil-seasons" role="group" aria-label="Receiving-stream low-flow season">
          {data.floors.map((f) => (
            <button
              key={f.key}
              type="button"
              className="dil-season"
              aria-pressed={f.key === seasonKey}
              onClick={() => setSeasonKey(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <p className="dil-cite">
        ⌖ {floor.cite}
        {floor.note ? ` · ${floor.note}` : ""}
      </p>
    </div>
  );
}
