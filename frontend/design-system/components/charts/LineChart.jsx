import React from "react";

const MONO = "var(--font-mono)";

/**
 * LineChart — a time series in the record grammar. Forest line, optional
 * forest-tint area, mono axis ticks, and an emphasized last point with an
 * inline figure. Light grid, no chrome.
 */
export function LineChart({
  data = [], max, area = true, height = 200, lastLabel, style, ...rest
}) {
  const r = (n, p = 1) => { const f = 10 ** p; return Math.round(n * f) / f; };
  const W = 360, l = 34, rpad = 14, top = 16, base = height - 26;
  const plotH = base - top, plotW = W - l - rpad;
  const vmax = max || Math.max(1, ...data.map((d) => d.value)) * 1.04;
  const step = plotW / Math.max(1, data.length - 1);
  const pts = data.map((d, i) => ({ label: d.label, x: r(l + step * i), y: r(base - (d.value / vmax) * plotH) }));
  const line = pts.length ? "M" + pts.map((p) => p.x + " " + p.y).join(" L") : "";
  const areaD = pts.length ? line + ` L${pts[pts.length - 1].x} ${base} L${pts[0].x} ${base} Z` : "";
  const last = pts[pts.length - 1];
  const gridVals = [0, 0.33, 0.66, 1].map((f) => r(f * vmax));

  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 ${W} ${height}`} style={{ width: "100%", height: "auto", display: "block" }}>
        {gridVals.map((v, i) => {
          const y = r(base - (v / vmax) * plotH);
          return (
            <g key={i}>
              <line x1={l} y1={y} x2={W - rpad} y2={y} stroke="var(--data-grid)" strokeWidth="1" />
              <text x={l - 6} y={y + 3} textAnchor="end" fontFamily={MONO} fontSize="9" fill="var(--ink-ghost)">{v}</text>
            </g>
          );
        })}
        <line x1={l} y1={base} x2={W - rpad} y2={base} stroke="var(--data-axis)" strokeWidth="1" />
        {area ? <path d={areaD} fill="var(--data-1)" fillOpacity="0.10" /> : null}
        <path d={line} fill="none" stroke="var(--data-1)" strokeWidth="2.2" strokeLinejoin="round" strokeLinecap="round" />
        {pts.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="3" fill="var(--surface-card)" stroke="var(--data-1)" strokeWidth="2" />
            {p.label ? <text x={p.x} y={base + 14} textAnchor="middle" fontFamily={MONO} fontSize="9.5" fill="var(--ink-faint)">{p.label}</text> : null}
          </g>
        ))}
        {last ? <circle cx={last.x} cy={last.y} r="4.5" fill="var(--data-1)" stroke="var(--surface-card)" strokeWidth="2" /> : null}
        {last && lastLabel ? <text x={r(last.x - 6)} y={r(last.y - 8)} textAnchor="end" fontFamily={MONO} fontSize="11" fontWeight="700" fill="var(--ink)">{lastLabel}</text> : null}
      </svg>
    </div>
  );
}
