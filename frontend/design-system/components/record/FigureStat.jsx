import React from "react";

const EV = {
  verified:  { label: "verified",  fg: "var(--ev-verified-fg)",  bg: "var(--ev-verified-bg)" },
  inference: { label: "inference", fg: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)" },
  open:      { label: "open",      fg: "var(--ev-open-fg)",      bg: "var(--ev-open-bg)" },
};
const BASIS = {
  grounded: { label: "grounded", fg: "var(--ev-verified-fg)", bg: "var(--ev-verified-bg)" },
  modeled:  { label: "modeled",  fg: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)" },
};

/**
 * FigureStat — a load-bearing number with its evidence standing.
 * `lg` is a standalone dashboard/hub tile; `sm` is an inline profile stat.
 * Value is ALWAYS mono. Warn turns the value oxblood.
 */
export function FigureStat({
  size = "lg", label, value, unit, evidence = "verified", basis, sub, source, warn = false, style, ...rest
}) {
  const t = EV[evidence] || EV.open;
  const b = basis ? BASIS[basis] : null;
  const valueColor = warn ? "var(--ev-gap-fg)" : "var(--ink)";

  if (size === "sm") {
    return (
      <div className="wm-figure wm-figure--sm" style={{ display: "flex", flexDirection: "column", gap: 3, padding: "2px 0", ...style }} {...rest}>
        <div style={{ fontFamily: "var(--font-sans)", fontSize: 10.5, fontWeight: 700, letterSpacing: "0.8px", textTransform: "uppercase", color: "var(--ink-faint)" }}>{label}</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 7 }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 20, fontWeight: 700, letterSpacing: "-0.4px", color: valueColor }}>{value}</span>
          <span title={t.label} style={{ width: 7, height: 7, background: t.fg }} />
        </div>
        {sub ? <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--ink-faint)" }}>{sub}</div> : null}
      </div>
    );
  }

  return (
    <div className="wm-figure wm-figure--lg" style={{ background: "var(--surface-card)", border: "1px solid var(--border-card)", padding: "17px 18px", display: "flex", flexDirection: "column", height: "100%", ...style }} {...rest}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 11 }}>
        <span style={{ fontFamily: "var(--font-sans)", fontSize: 11, fontWeight: 700, letterSpacing: "0.9px", textTransform: "uppercase", color: "var(--ink-faint)" }}>{label}</span>
        {b ? <span style={{ fontFamily: "var(--font-sans)", fontSize: 10, fontWeight: 700, letterSpacing: "0.4px", textTransform: "uppercase", color: b.fg, background: b.bg, padding: "2px 7px" }}>{b.label}</span> : null}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8, flexWrap: "wrap" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 34, fontWeight: 700, letterSpacing: "-1px", color: valueColor }}>{value}</span>
        {unit ? <span style={{ fontFamily: "var(--font-mono)", fontSize: 14, color: "var(--ink-faint)" }}>{unit}</span> : null}
      </div>
      {sub ? <div style={{ fontFamily: "var(--font-mono)", fontSize: 12.5, color: "var(--ink-muted)", lineHeight: 1.45, marginTop: 7 }}>{sub}</div> : null}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: "auto", paddingTop: 13 }}>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 700, color: t.fg, background: t.bg, padding: "3px 11px" }}>
          <span style={{ width: 6, height: 6, background: t.fg }} />[{t.label}]
        </span>
        {source ? <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--ink-faint)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{source}</span> : null}
      </div>
    </div>
  );
}
