import React from "react";

const FOREST = "var(--data-1)", AMBER = "var(--ev-inference-fg)", OX = "var(--ev-gap-fg)";
const GRID = "var(--data-grid)", AXIS = "var(--data-axis)", MONO = "var(--font-mono)";
const INK = "var(--ink)", GHOST = "var(--ink-ghost)", SURF = "var(--surface-card)";
const r = (n, p = 1) => { const f = 10 ** p; return Math.round(n * f) / f; };

/**
 * FlowDurationCurve — streamflow against the share of the year it is equalled
 * or exceeded (log Y). Threshold lines mark a draw / design low flow; an
 * optional shaded tail highlights the exceedance band below a value. Hover a
 * point for the readout.
 */
export function FlowDurationCurve({
  data = [], yMin, yMax, thresholds = [], shadeBelow, area = true, height = 192, style, ...rest
}) {
  const [hi, setHi] = React.useState(null);
  const L = 40, R = 348, T = 14, B = 168, plotW = R - L, plotH = B - T;
  const flows = data.map((d) => d.flow);
  const lo = yMin != null ? yMin : Math.max(0.1, Math.min(...flows) * 0.6);
  const hg = yMax != null ? yMax : Math.max(...flows) * 1.05;
  const lloL = Math.log10(lo), lhiL = Math.log10(hg);
  const fy = (v) => r(T + (1 - (Math.log10(v) - lloL) / (lhiL - lloL)) * plotH);
  const fx = (e) => r(L + (e / 100) * plotW);
  const pts = data.map((d) => ({ ...d, x: fx(d.exceedance), y: fy(d.flow) }));
  const line = pts.length ? "M" + pts.map((p) => p.x + " " + p.y).join(" L") : "";
  const areaD = pts.length ? line + ` L${pts[pts.length - 1].x} ${B} L${pts[0].x} ${B} Z` : "";

  // decade gridlines spanning the range
  const decades = [];
  for (let e = Math.floor(lloL); e <= Math.ceil(lhiL); e++) { const v = 10 ** e; if (v >= lo * 0.99 && v <= hg * 1.01) decades.push(v); }

  // exceedance where flow crosses shadeBelow
  let bandX = null;
  if (shadeBelow != null) {
    for (let i = 1; i < data.length; i++) {
      const a = data[i - 1], b = data[i];
      if ((a.flow - shadeBelow) * (b.flow - shadeBelow) <= 0 && a.flow !== b.flow) {
        const t = (a.flow - shadeBelow) / (a.flow - b.flow);
        bandX = fx(a.exceedance + t * (b.exceedance - a.exceedance)); break;
      }
    }
  }
  const fmt = (v) => (v >= 1000 ? r(v / 1000, 1) + "k" : v >= 1 ? r(v) : r(v, 2));

  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 360 ${height}`} style={{ width: "100%", height: "auto", display: "block" }} onMouseLeave={() => setHi(null)}>
        {bandX != null ? <rect x={bandX} y={T} width={r(R - bandX)} height={plotH} fill="rgba(122,34,48,0.10)" /> : null}
        {decades.map((v, i) => (
          <g key={i}>
            <line x1={L} y1={fy(v)} x2={R} y2={fy(v)} stroke={GRID} strokeWidth="1" />
            <text x={L - 4} y={fy(v) + 3} textAnchor="end" fontFamily={MONO} fontSize="8.5" fill={GHOST}>{fmt(v)}</text>
          </g>
        ))}
        {[0, 25, 50, 75, 100].map((e) => <text key={e} x={fx(e)} y={height - 6} textAnchor="middle" fontFamily={MONO} fontSize="8.5" fill={GHOST}>{e}</text>)}
        {area ? <path d={areaD} fill="rgba(31,111,74,0.12)" /> : null}
        <path d={line} fill="none" stroke={FOREST} strokeWidth="2.2" strokeLinejoin="round" />
        {thresholds.map((t, i) => (
          <g key={i}>
            <line x1={L} y1={fy(t.value)} x2={R} y2={fy(t.value)} stroke={t.color || AMBER} strokeWidth="1.5" strokeDasharray="4 3" />
            {t.label ? <text x={R - 2} y={fy(t.value) - 4} textAnchor="end" fontFamily={MONO} fontSize="9" fontWeight="600" fill={t.color || AMBER}>{t.label}</text> : null}
          </g>
        ))}
        {bandX != null ? <line x1={bandX} y1={T} x2={bandX} y2={B} stroke={OX} strokeWidth="1.5" /> : null}
        {pts.map((p, i) => {
          const left = i === 0 ? L : (pts[i - 1].x + p.x) / 2;
          const right = i < pts.length - 1 ? (pts[i + 1].x + p.x) / 2 : R;
          return <rect key={i} x={r(left)} y={T} width={r(right - left)} height={plotH} fill="#000" opacity="0" onMouseEnter={() => setHi(i)} />;
        })}
        {hi != null ? (() => {
          const p = pts[hi]; const bw = 104, bh = 33;
          let bx = Math.max(L - 6, Math.min(p.x - bw / 2, R - bw)); let by = p.y - bh - 12; if (by < T - 8) by = p.y + 12;
          return (
            <g key="tip">
              <line x1={p.x} y1={T} x2={p.x} y2={B} stroke={INK} strokeWidth="1" strokeDasharray="2 2" />
              <circle cx={p.x} cy={p.y} r="3.5" fill={INK} stroke={SURF} strokeWidth="1.5" />
              <rect x={r(bx)} y={r(by)} width={bw} height={bh} fill={INK} />
              <text x={r(bx + 9)} y={r(by + 13)} fontFamily={MONO} fontSize="9.5" fill={SURF}>{p.exceedance}% of year ≥</text>
              <text x={r(bx + 9)} y={r(by + 26)} fontFamily={MONO} fontSize="9.5" fontWeight="600" fill="var(--forest-on-ink)">{fmt(p.flow)} {p.unit || "cfs"}</text>
            </g>
          );
        })() : null}
      </svg>
    </div>
  );
}
