import React from "react";

const FOREST = "var(--data-1)", AMBER = "var(--ev-inference-fg)";
const GRID = "var(--data-grid)", AXIS = "var(--data-axis)", MONO = "var(--font-mono)";
const INK = "var(--ink)", GHOST = "var(--ink-ghost)", FAINT = "var(--ink-faint)";
const r = (n, p = 1) => { const f = 10 ** p; return Math.round(n * f) / f; };

const TONE = {
  base: INK,        // a starting total (e.g. intake)
  down: FOREST,     // a subtraction that returns / recovers
  up: AMBER,        // an addition
  result: AMBER,    // the net remainder
};

/**
 * Waterfall — a value built or drawn down step by step; reads as an equation.
 * Each step floats from the running total. Use `kind`: "base" (full bar from
 * zero), "down" / "up" (a delta), "result" (the net remainder from zero).
 * Classic use: intake − returned = consumed.
 */
export function Waterfall({ steps = [], max, unit = "", height = 200, style, ...rest }) {
  const L = 40, R = 344, top = 32, base = 172, plotH = base - top;
  const running = [];
  let cur = 0;
  // compute the top of the running total before/after each step
  const peak = max != null ? max : Math.max(...steps.map((s) => s.value), 0) * 1.05;
  const sy = (v) => r(base - (v / peak) * plotH);
  const n = steps.length, slotW = (R - L) / n, barW = Math.min(58, slotW * 0.6);

  const bars = steps.map((s, i) => {
    const cx = L + slotW * i + slotW / 2;
    const x = r(cx - barW / 2);
    let yTop, yBot, color = s.color || TONE[s.kind] || INK, label;
    if (s.kind === "base" || s.kind === "result") {
      yTop = sy(s.value); yBot = base; cur = s.value; label = (s.kind === "base" ? "" : "") + s.value;
    } else if (s.kind === "down") {
      yBot = sy(cur); cur -= s.value; yTop = sy(cur); label = "−" + s.value;
    } else { // up
      yBot = sy(cur); cur += s.value; yTop = sy(cur); label = "+" + s.value;
    }
    running.push(cur);
    return { x, w: barW, y: r(yTop), h: r(yBot - yTop), color, label, cx: r(cx), topY: r(yTop), name: s.label };
  });

  const gridVals = [0, 0.33, 0.66, 1].map((f) => r(f * peak));

  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 360 ${height}`} style={{ width: "100%", height: "auto", display: "block" }}>
        {gridVals.map((v, i) => (
          <g key={i}>
            <line x1={L} y1={sy(v)} x2={R} y2={sy(v)} stroke={GRID} strokeWidth="1" />
            <text x={L - 4} y={sy(v) + 3} textAnchor="end" fontFamily={MONO} fontSize="8.5" fill={GHOST}>{v}</text>
          </g>
        ))}
        <line x1={L} y1={base} x2={R} y2={base} stroke={AXIS} strokeWidth="1" />
        {bars.map((b, i) => {
          const next = bars[i + 1];
          return (
            <g key={i}>
              <rect x={b.x} y={b.y} width={b.w} height={Math.max(b.h, 1)} fill={b.color} />
              <text x={b.cx} y={b.topY - 6} textAnchor="middle" fontFamily={MONO} fontSize="10" fontWeight="700" fill={b.color}>{b.label}</text>
              <text x={b.cx} y={base + 14} textAnchor="middle" fontFamily={MONO} fontSize="8.5" fill={FAINT}>{b.name}</text>
              {next ? <line x1={b.x + b.w} y1={b.topY} x2={next.x} y2={b.topY} stroke={FAINT} strokeWidth="1" strokeDasharray="3 2" /> : null}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
