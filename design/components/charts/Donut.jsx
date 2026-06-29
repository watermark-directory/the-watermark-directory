import React from "react";

const SERIES = ["var(--data-1)", "var(--data-2)", "var(--data-3)", "var(--data-4)", "var(--data-5)"];
const MONO = "var(--font-mono)";

/**
 * Donut — composition of a whole. One forest hue in tints; the center holds
 * the total as a mono figure. Optional legend lists each slice with its value.
 */
export function Donut({
  data = [], total, size = 128, center, centerSub = "records", legend = true, style, ...rest
}) {
  const sum = total != null ? total : data.reduce((a, d) => a + d.value, 0);
  const cx = 100, cy = 100, ro = 80, ri = 50;
  const r = (n, p = 2) => { const f = 10 ** p; return Math.round(n * f) / f; };
  const pol = (rad, a) => [r(cx + rad * Math.cos(a)), r(cy + rad * Math.sin(a))];
  let a = -Math.PI / 2;
  const segs = data.map((d, i) => {
    const a0 = a, a1 = a + (sum ? d.value / sum : 0) * Math.PI * 2; a = a1;
    const large = a1 - a0 > Math.PI ? 1 : 0;
    const [x0, y0] = pol(ro, a0), [x1, y1] = pol(ro, a1), [x2, y2] = pol(ri, a1), [x3, y3] = pol(ri, a0);
    return { fill: d.color || SERIES[i % SERIES.length], d: `M${x0} ${y0} A${ro} ${ro} 0 ${large} 1 ${x1} ${y1} L${x2} ${y2} A${ri} ${ri} 0 ${large} 0 ${x3} ${y3} Z` };
  });

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16, ...style }} {...rest}>
      <svg viewBox="0 0 200 200" style={{ width: size, height: size, flex: "0 0 auto" }}>
        {segs.map((s, i) => <path key={i} d={s.d} fill={s.fill} stroke="var(--surface-card)" strokeWidth="2" />)}
        <text x="100" y="96" textAnchor="middle" fontFamily={MONO} fontSize="30" fontWeight="700" fill="var(--ink)">{center != null ? center : sum}</text>
        {centerSub ? <text x="100" y="116" textAnchor="middle" fontFamily={MONO} fontSize="10" fill="var(--ink-faint)">{centerSub}</text> : null}
      </svg>
      {legend ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 7, minWidth: 0 }}>
          {data.map((d, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5, fontFamily: "var(--font-sans)", color: "var(--ink)" }}>
              <span style={{ width: 10, height: 10, background: d.color || SERIES[i % SERIES.length], flex: "0 0 auto" }} />
              {d.label}
              <span style={{ marginLeft: "auto", fontFamily: MONO, color: "var(--ink-faint)", paddingLeft: 12 }}>{d.value}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
