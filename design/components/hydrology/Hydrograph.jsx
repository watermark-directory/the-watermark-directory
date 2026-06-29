import React from "react";

const FOREST = "var(--data-1)", AMBER = "var(--ev-inference-fg)", OX = "var(--ev-gap-fg)";
const AXIS = "var(--data-axis)", MONO = "var(--font-mono)", GHOST = "var(--ink-ghost)";
const INK = "var(--ink)", SURF = "var(--surface-card)";
const r = (n, p = 1) => { const f = 10 ** p; return Math.round(n * f) / f; };
const MLAB = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];

/**
 * Hydrograph — flow across the year. Three modes share one scale:
 *  · "area"     — a single seasonal series under the curve
 *  · "bars"     — monthly bars; any month below `drawLine` flags oxblood
 *  · "envelope" — typical vs dry band with both lines (hover for both)
 * √-scaled by default so a late-summer trough still reads against the freshet.
 */
export function Hydrograph({
  mode = "area", series = [], typical = [], dry = [], labels = MLAB,
  drawLine, max, sqrt = true, height = 196, style, ...rest
}) {
  const [hi, setHi] = React.useState(null);
  const L = 30, R = 354, base = 176, top = 14, plotW = R - L;
  const all = [...series, ...typical, ...dry, drawLine || 0];
  const vmax = max != null ? max : Math.max(...all) * 1.04;
  const sc = sqrt ? (v) => Math.sqrt(Math.max(v, 0)) : (v) => Math.max(v, 0);
  const scMax = sc(vmax);
  const sy = (v) => r(base - (sc(v) / scMax) * (base - top));
  const n = (mode === "envelope" ? typical.length : mode === "area" ? series.length : series.length) || 12;
  const hx = (i) => r(L + 18 + i * ((plotW - 36) / (n - 1)));
  const drawY = drawLine != null ? sy(drawLine) : null;

  const linePath = (arr) => "M" + arr.map((v, i) => hx(i) + " " + sy(v)).join(" L");

  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 360 ${height}`} style={{ width: "100%", height: "auto", display: "block" }} onMouseLeave={() => setHi(null)}>
        <line x1={L} y1={base} x2={R} y2={base} stroke={AXIS} strokeWidth="1" />
        {drawY != null ? <line x1={L} y1={drawY} x2={R} y2={drawY} stroke={AMBER} strokeWidth="1.3" strokeDasharray="4 3" /> : null}
        {drawY != null ? <text x={R - 2} y={drawY - 4} textAnchor="end" fontFamily={MONO} fontSize="8.5" fontWeight="600" fill={AMBER}>draw {drawLine}</text> : null}

        {mode === "area" ? (
          <>
            <path d={linePath(series) + ` L${hx(series.length - 1)} ${base} L${hx(0)} ${base} Z`} fill="rgba(31,111,74,0.13)" />
            <path d={linePath(series)} fill="none" stroke={FOREST} strokeWidth="2.2" strokeLinejoin="round" />
          </>
        ) : null}

        {mode === "bars" ? series.map((v, i) => {
          const y = sy(v), w = 16;
          return (
            <g key={i}>
              <rect x={r(hx(i) - w / 2)} y={y} width={w} height={r(base - y)} fill={drawLine != null && v < drawLine ? OX : FOREST} />
            </g>
          );
        }) : null}

        {mode === "envelope" ? (
          <>
            <path d={linePath(typical) + " L" + dry.map((v, i) => hx(n - 1 - i) + " " + sy(dry[n - 1 - i])).join(" L") + " Z"} fill="rgba(31,111,74,0.14)" />
            <path d={linePath(typical)} fill="none" stroke={FOREST} strokeWidth="2" strokeLinejoin="round" />
            <path d={linePath(dry)} fill="none" stroke={AMBER} strokeWidth="1.8" strokeDasharray="5 3" strokeLinejoin="round" />
          </>
        ) : null}

        {labels.map((m, i) => <text key={i} x={hx(i)} y={height - 6} textAnchor="middle" fontFamily={MONO} fontSize="8.5" fill={GHOST}>{m}</text>)}

        {mode === "envelope" ? typical.map((_, i) => (
          <rect key={i} x={r(hx(i) - ((plotW - 36) / (n - 1)) / 2)} y={top} width={r((plotW - 36) / (n - 1))} height={base - top} fill="#000" opacity="0" onMouseEnter={() => setHi(i)} />
        )) : null}
        {mode === "envelope" && hi != null ? (() => {
          const x = hx(hi), bw = 110, bh = 33; const yTop = sy(typical[hi]), yBot = sy(dry[hi]);
          let bx = Math.max(L, Math.min(x - bw / 2, R - bw)); let by = Math.min(yTop, yBot) - bh - 12; if (by < top) by = Math.max(yTop, yBot) + 12;
          return (
            <g>
              <line x1={x} y1={top} x2={x} y2={base} stroke={INK} strokeWidth="1" strokeDasharray="2 2" />
              <circle cx={x} cy={yTop} r="3" fill={FOREST} stroke={SURF} strokeWidth="1.5" />
              <circle cx={x} cy={yBot} r="3" fill={AMBER} stroke={SURF} strokeWidth="1.5" />
              <rect x={r(bx)} y={r(by)} width={bw} height={bh} fill={INK} />
              <text x={r(bx + 9)} y={r(by + 13)} fontFamily={MONO} fontSize="9.5" fill="var(--forest-on-ink)">{labels[hi]} typ {typical[hi]}</text>
              <text x={r(bx + 9)} y={r(by + 26)} fontFamily={MONO} fontSize="9.5" fill="#e0b552">dry {dry[hi]}</text>
            </g>
          );
        })() : null}
      </svg>
    </div>
  );
}
