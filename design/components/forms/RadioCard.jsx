import React from "react";

/**
 * RadioCard — a selectable option card (the lead-type picker). A square radio dot,
 * a title, and a one-line description. Selected goes forest-tinted with a forest border.
 */
export function RadioCard({ title, desc, selected = false, onSelect, style, ...rest }) {
  return (
    <div
      onClick={onSelect}
      className={`wm-radiocard${selected ? " is-selected" : ""}`}
      style={{
        display: "flex", gap: 10, alignItems: "flex-start",
        border: `1.5px solid ${selected ? "var(--forest)" : "var(--line-hair)"}`,
        background: selected ? "var(--forest-tint)" : "var(--surface-card)",
        borderRadius: "var(--radius, 0)", padding: "12px 13px", cursor: "pointer",
        transition: "border-color var(--dur) var(--ease), background var(--dur) var(--ease)", ...style,
      }}
      {...rest}
    >
      <span style={{ flex: "0 0 auto", width: 18, height: 18, border: `2px solid ${selected ? "var(--forest)" : "var(--line-2)"}`, background: selected ? "var(--forest)" : "var(--surface-card)", marginTop: 1, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "var(--radius, 0)" }}>
        {selected ? <span style={{ width: 7, height: 7, background: "var(--bone-surface)" }} /> : null}
      </span>
      <div>
        <div style={{ fontSize: 14, fontWeight: 700, color: selected ? "var(--forest)" : "var(--ink)" }}>{title}</div>
        {desc ? <div style={{ fontSize: 12, color: "var(--ink-faint)", lineHeight: 1.4, marginTop: 1 }}>{desc}</div> : null}
      </div>
    </div>
  );
}
