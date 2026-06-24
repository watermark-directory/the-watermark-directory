import React from "react";

const AMBER = "var(--ev-inference-fg)", OX = "var(--ev-gap-fg)", INK = "var(--ink)";
const MONO = "var(--font-mono)", FAINT = "var(--ink-faint)", MUTED = "var(--ink-muted)";
const r = (n, p = 1) => { const f = 10 ** p; return Math.round(n * f) / f; };

/**
 * GaugeBar — a single figure against a permitted cap. The fill runs amber to
 * the cap; anything past it is the oxblood overage, with an ink cap mark. The
 * big percentage turns oxblood once the cap is exceeded.
 */
export function GaugeBar({
  value, cap, max, unit = "", label, fillColor = AMBER, showPercent = true, style, ...rest
}) {
  const ceiling = max != null ? max : Math.max(value, cap) * 1.04;
  const pct = (v) => Math.max(0, Math.min(100, (v / ceiling) * 100));
  const over = value > cap;
  const capPct = pct(cap);
  const fillPct = pct(Math.min(value, cap));
  const overPct = over ? pct(value) - capPct : 0;
  const percent = Math.round((value / cap) * 100);
  const fmt = (v) => (v >= 1000 ? v.toLocaleString() : r(v));

  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      {showPercent ? (
        <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginBottom: 14 }}>
          <span style={{ fontFamily: MONO, fontSize: 40, fontWeight: 700, letterSpacing: "-1.5px", color: over ? OX : "var(--data-1)" }}>{percent}%</span>
          {label ? <span style={{ fontFamily: "var(--font-sans)", fontSize: 13, color: MUTED }}>{label}</span> : null}
        </div>
      ) : null}
      <div style={{ position: "relative", height: 26, background: "var(--bone-band)", border: "1px solid var(--data-axis)" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: fillPct + "%", background: fillColor }} />
        {over ? <div style={{ position: "absolute", left: capPct + "%", top: 0, bottom: 0, width: overPct + "%", background: OX }} /> : null}
        <div style={{ position: "absolute", top: -4, bottom: -4, left: capPct + "%", width: 2, background: INK }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 7, fontFamily: MONO, fontSize: 10, color: FAINT }}>
        <span>0</span>
        <span style={{ color: INK, fontWeight: 600 }}>cap · {fmt(cap)}{unit ? " " + unit : ""}</span>
        <span>{fmt(Math.round(ceiling))}</span>
      </div>
    </div>
  );
}
