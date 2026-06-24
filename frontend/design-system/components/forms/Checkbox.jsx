import React from "react";

/**
 * Checkbox — a flat square checkbox with an inline label. Checked is forest-filled
 * with a bone check. No radius.
 */
export function Checkbox({ checked = false, onChange, children, style, ...rest }) {
  return (
    <label className="wm-checkbox" style={{ display: "flex", alignItems: "center", gap: 9, fontSize: 12.5, color: "var(--ink-muted)", cursor: "pointer", ...style }} {...rest}>
      <span
        onClick={() => onChange && onChange(!checked)}
        style={{
          width: 18, height: 18, flex: "0 0 auto", display: "inline-flex", alignItems: "center", justifyContent: "center",
          border: `2px solid ${checked ? "var(--forest)" : "var(--line-2)"}`,
          background: checked ? "var(--forest)" : "var(--surface-card)",
          borderRadius: "var(--radius, 0)", transition: "background var(--dur) var(--ease), border-color var(--dur) var(--ease)",
        }}
      >
        {checked ? (
          <svg viewBox="0 0 24 24" width={12} height={12} fill="none" stroke="var(--bone-surface)" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round"><path d="M5 13 L10 18 L19 7" /></svg>
        ) : null}
      </span>
      {children}
    </label>
  );
}
