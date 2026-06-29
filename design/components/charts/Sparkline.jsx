import React from "react";

const MONO = "var(--font-mono)";

/**
 * Sparkline — a trend small enough to sit in a record row. No axes, no labels,
 * just the shape of a series next to its current figure. Defaults to forest.
 */
export function Sparkline({
  data = [], color = "var(--data-1)", width = 120, height = 32, strokeWidth = 2, dot = true, style, ...rest
}) {
  const r = (n) => Math.round(n * 10) / 10;
  const max = Math.max(...data), min = Math.min(...data), span = max - min || 1;
  const x0 = 3, w = width - 6, y0 = 5, h = height - 10;
  const step = w / Math.max(1, data.length - 1);
  const pts = data.map((v, i) => ({ x: r(x0 + step * i), y: r(y0 + (1 - (v - min) / span) * h) }));
  const path = pts.length ? "M" + pts.map((p) => p.x + " " + p.y).join(" L") : "";
  const end = pts[pts.length - 1];
  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width, height, flex: "0 0 auto", display: "block", ...style }} {...rest}>
      <path d={path} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinejoin="round" strokeLinecap="round" />
      {dot && end ? <circle cx={end.x} cy={end.y} r="3" fill={color} stroke="var(--surface-card)" strokeWidth="1.5" /> : null}
    </svg>
  );
}
