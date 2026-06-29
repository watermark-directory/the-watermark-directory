import React from "react";

const CONF = {
  low:        { label: "Low confidence", fg: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)", rail: "var(--ev-inference-fg)" },
  unanswered: { label: "Unanswered",     fg: "var(--forest)",          bg: "var(--forest-tint)",     rail: "var(--forest)" },
  withheld:   { label: "Withheld",       fg: "var(--ev-open-fg)",      bg: "var(--ev-open-bg)",      rail: "var(--ink-faint)" },
  review:     { label: "Under review",   fg: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)", rail: "var(--ev-inference-fg)" },
};

/**
 * LeadCard — an open, unverified thread published for the public to close.
 * Left rail + confidence chip declare its standing; the action is forest.
 */
export function LeadCard({ kind = "Signal", confidence = "low", title, detail, source, action = "Help confirm", count, onAction, style, ...rest }) {
  const c = CONF[confidence] || CONF.low;
  return (
    <div className="wm-lead" style={{ display: "flex", flexDirection: "column", background: "var(--surface-card)", border: "1px solid var(--border-card)", borderLeft: `4px solid ${c.rail}`, padding: "15px 16px", ...style }} {...rest}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 9.5, fontWeight: 800, letterSpacing: "0.6px", textTransform: "uppercase", color: "var(--ink-muted)", background: "var(--bone-sunk)", border: "1px solid var(--border-card)", padding: "2px 7px" }}>{kind}</span>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10, fontWeight: 700, color: c.fg, background: c.bg, padding: "2px 8px" }}>
          <span style={{ width: 5, height: 5, background: c.fg }} />{c.label}
        </span>
        {source ? <span style={{ marginLeft: "auto", fontSize: 10.5, color: "var(--ink-ghost)", fontFamily: "var(--font-mono)", whiteSpace: "nowrap" }}>{source}</span> : null}
      </div>
      <div style={{ fontSize: 15, fontWeight: 700, margin: "10px 0 4px", lineHeight: 1.3 }}>{title}</div>
      {detail ? <div style={{ fontSize: 12.5, color: "var(--ink-muted)", lineHeight: 1.45 }}>{detail}</div> : null}
      <div style={{ display: "flex", alignItems: "center", gap: 11, marginTop: 13 }}>
        <span onClick={onAction} style={{ display: "inline-flex", alignItems: "center", gap: 7, fontSize: 12.5, fontWeight: 700, color: "var(--bone-surface)", background: "var(--forest)", padding: "7px 13px", cursor: "pointer" }}>{action} →</span>
        {count ? <span style={{ fontSize: 11.5, color: "var(--ink-faint)" }}>{count}</span> : null}
      </div>
    </div>
  );
}
