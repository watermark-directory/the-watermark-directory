import React from "react";

/**
 * SectionCard — a browse "door" into a part of the record. Open doors show a
 * count and a Browse link; locked doors are dashed and explain what unlocks them.
 */
export function SectionCard({ badge, title, count, locked = false, lockNote, href = "#", style, ...rest }) {
  if (locked) {
    return (
      <div className="wm-section wm-section--locked" style={{ display: "flex", flexDirection: "column", background: "#f2efe6", border: "1px dashed var(--line-2)", padding: "14px 15px", opacity: 0.85, ...style }} {...rest}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 800, letterSpacing: "0.4px", color: "var(--ink-ghost)", background: "var(--bone-band)", border: "1px solid var(--border-card)", padding: "2px 7px" }}>{badge}</span>
          <span style={{ fontSize: 13 }}>🔒</span>
        </div>
        <div style={{ fontSize: 15, fontWeight: 700, margin: "9px 0 3px", color: "var(--ink-faint)" }}>{title}</div>
        <div style={{ fontSize: 11.5, color: "var(--ink-ghost)", lineHeight: 1.4 }}>{lockNote}</div>
      </div>
    );
  }
  return (
    <a href={href} className="wm-section wm-section--open" style={{ display: "flex", flexDirection: "column", textDecoration: "none", color: "var(--ink)", background: "var(--surface-card)", border: "1px solid var(--border-card)", padding: "14px 15px", transition: "border-color var(--dur) var(--ease), transform var(--dur) var(--ease)", ...style }} {...rest}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 800, letterSpacing: "0.4px", color: "var(--forest)", background: "var(--forest-tint)", border: "1px solid var(--forest-line)", padding: "2px 7px" }}>{badge}</span>
        {count != null ? <span style={{ fontFamily: "var(--font-mono)", fontSize: 16, fontWeight: 800, letterSpacing: "-0.5px" }}>{count}</span> : null}
      </div>
      <div style={{ fontSize: 15, fontWeight: 700, margin: "9px 0 3px" }}>{title}</div>
      <div style={{ fontSize: 12, color: "var(--forest)", fontWeight: 600 }}>Browse ›</div>
    </a>
  );
}
