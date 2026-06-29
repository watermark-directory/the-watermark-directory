import React from "react";

const FOREST = "var(--data-1)", OX = "var(--ev-gap-fg)";
const GRID = "var(--data-grid)", AXIS = "var(--data-axis)", MONO = "var(--font-mono)";
const INK = "var(--ink)", GHOST = "var(--ink-ghost)", SURF = "var(--surface-card)";
const r = (n, p = 1) => { const f = 10 ** p; return Math.round(n * f) / f; };

/**
 * ThresholdLine — a cumulative / time-series line measured against a horizontal
 * limit (a permit cap, a draw). Auto-marks the crossing point and shades the
 * overage region above the limit in oxblood. Hover a month for the readout.
 */
export function ThresholdLine({
  data = [], limit, limitLabel = "cap", max, unit = "", area = false,
  yTickFormat, height = 196, style, ...rest
}) {
  const [hi, setHi] = React.useState(null);
  const L = 40, R = 348, top = 14, base = 172, plotW = R - L, plotH = base - top;
  const vmax = max != null ? max : Math.max(...data.map((d) => d.value), limit || 0) * 1.08;
  const cy = (v) => r(base - (v / vmax) * plotH);
  const cx = (i) => r(L + i * (plotW / (data.length - 1)));
  const pts = data.map((d, i) => ({ ...d, x: cx(i), y: cy(d.value) }));
  const line = pts.length ? "M" + pts.map((p) => p.x + " " + p.y).join(" L") : "";
  const areaD = pts.length ? line + ` L${pts[pts.length - 1].x} ${base} L${pts[0].x} ${base} Z` : "";
  const fmt = yTickFormat || ((v) => (v >= 1000 ? r(v / 1000, 1) + "k" : r(v)));

  // crossing
  let crossX = null, overD = "";
  if (limit != null) {
    for (let i = 1; i < data.length; i++) {
      if (data[i - 1].value <= limit && data[i].value > limit) {
        const t = (limit - data[i - 1].value) / (data[i].value - data[i - 1].value);
        crossX = r(cx(i - 1) + t * (cx(i) - cx(i - 1))); break;
      }
    }
    if (crossX != null) {
      const over = pts.filter((p) => p.value > limit);
      overD = `M${crossX} ${cy(limit)} ` + over.map((p) => `L${p.x} ${p.y}`).join(" ") + ` L${pts[pts.length - 1].x} ${cy(limit)} Z`;
    }
  }
  const gridVals = [0, 0.33, 0.66, 1].map((f) => r(f * vmax));

  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 360 ${height}`} style={{ width: "100%", height: "auto", display: "block" }} onMouseLeave={() => setHi(null)}>
        {gridVals.map((v, i) => (
          <g key={i}>
            <line x1={L} y1={cy(v)} x2={R} y2={cy(v)} stroke={GRID} strokeWidth="1" />
            <text x={L - 4} y={cy(v) + 3} textAnchor="end" fontFamily={MONO} fontSize="8.5" fill={GHOST}>{fmt(v)}</text>
          </g>
        ))}
        <line x1={L} y1={base} x2={R} y2={base} stroke={AXIS} strokeWidth="1" />
        {area ? <path d={areaD} fill="rgba(31,111,74,0.16)" /> : null}
        {overD ? <path d={overD} fill="rgba(122,34,48,0.22)" /> : null}
        {limit != null ? (
          <>
            <line x1={L} y1={cy(limit)} x2={R} y2={cy(limit)} stroke={OX} strokeWidth="1.5" strokeDasharray="5 3" />
            <text x={R - 2} y={cy(limit) - 4} textAnchor="end" fontFamily={MONO} fontSize="9" fontWeight="600" fill={OX}>{limitLabel} {fmt(limit)}</text>
          </>
        ) : null}
        <path d={line} fill="none" stroke={FOREST} strokeWidth="2.2" strokeLinejoin="round" />
        {crossX != null ? <circle cx={crossX} cy={cy(limit)} r="4" fill={OX} stroke={SURF} strokeWidth="1.5" /> : null}
        {pts.map((p, i) => <text key={"x" + i} x={p.x} y={height - 6} textAnchor="middle" fontFamily={MONO} fontSize="8.5" fill={GHOST}>{p.label}</text>)}
        {pts.map((p, i) => {
          const left = i === 0 ? L : (pts[i - 1].x + p.x) / 2;
          const right = i < pts.length - 1 ? (pts[i + 1].x + p.x) / 2 : R;
          return <rect key={i} x={r(left)} y={top} width={r(right - left)} height={plotH} fill="#000" opacity="0" onMouseEnter={() => setHi(i)} />;
        })}
        {hi != null ? (() => {
          const p = pts[hi], bw = 104, bh = 33;
          let bx = Math.max(L - 6, Math.min(p.x - bw / 2, R - bw)); let by = p.y - bh - 12; if (by < top - 8) by = p.y + 12;
          const pct = limit ? Math.round((p.value / limit) * 100) + "% of " + limitLabel : "";
          return (
            <g>
              <circle cx={p.x} cy={p.y} r="3.5" fill={INK} stroke={SURF} strokeWidth="1.5" />
              <rect x={r(bx)} y={r(by)} width={bw} height={bh} fill={INK} />
              <text x={r(bx + 9)} y={r(by + 13)} fontFamily={MONO} fontSize="9.5" fill={SURF}>{p.label} · {fmt(p.value)}{unit ? " " + unit : ""}</text>
              <text x={r(bx + 9)} y={r(by + 26)} fontFamily={MONO} fontSize="9.5" fontWeight="600" fill="var(--forest-on-ink)">{pct}</text>
            </g>
          );
        })() : null}
      </svg>
    </div>
  );
}
