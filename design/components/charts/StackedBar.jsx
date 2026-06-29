import React from "react";

const MONO = "var(--font-mono)";
// Status proportions usually carry the evidence palette, not the forest series.
const EV = {
  verified: "var(--ev-verified-fg)", inference: "var(--ev-inference-fg)",
  open: "var(--ev-open-fg)", gap: "var(--ev-gap-fg)", key: "var(--ev-key-fg)",
};
const SERIES = ["var(--data-1)", "var(--data-2)", "var(--data-3)", "var(--data-4)", "var(--data-5)"];

/**
 * StackedBar — a single proportion bar with an optional legend. Pass each
 * segment a `kind` (evidence palette) or an explicit `color`; falls back to
 * the forest series. Good for "evidence status across N records".
 */
export function StackedBar({ segments = [], total, height = 30, legend = true, showPct = true, style, ...rest }) {
  const sum = total != null ? total : segments.reduce((a, s) => a + s.value, 0);
  const colorOf = (s, i) => s.color || (s.kind && EV[s.kind]) || SERIES[i % SERIES.length];
  const W = 360, pad = 3, inner = W - pad * 2;
  let acc = pad;
  const r = (n) => Math.round(n * 10) / 10;
  const segs = segments.map((s, i) => {
    const w = sum ? (s.value / sum) * inner : 0;
    const seg = { x: r(acc), w: r(w), fill: colorOf(s, i) };
    acc += w; return seg;
  });
  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 ${W} ${height}`} style={{ width: "100%", height, display: "block" }}>
        <defs><clipPath id="wm-stk-clip"><rect x={pad} y="3" width={inner} height={height - 6} /></clipPath></defs>
        <g clipPath="url(#wm-stk-clip)">
          {segs.map((s, i) => <rect key={i} x={s.x} y="3" width={s.w} height={height - 6} fill={s.fill} />)}
        </g>
      </svg>
      {legend ? (
        <div style={{ display: "flex", gap: 22, marginTop: 14, flexWrap: "wrap" }}>
          {segments.map((s, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, fontFamily: "var(--font-sans)", color: "var(--ink)" }}>
              <span style={{ width: 11, height: 11, background: colorOf(s, i), flex: "0 0 auto" }} />
              <b style={{ fontFamily: MONO }}>{s.value}</b>
              <span style={{ color: "var(--ink-faint)" }}>{s.label}{showPct && sum ? ` · ${Math.round((s.value / sum) * 100)}%` : ""}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
