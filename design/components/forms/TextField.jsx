import React from "react";

/**
 * TextField — a flat, square text input or textarea. Hairline border, bone fill,
 * forest focus ring. The label is a mono uppercase micro-label.
 */
export function TextField({ label, hint, placeholder, value, onChange, multiline = false, rows = 4, optional, icon, style, ...rest }) {
  const [focus, setFocus] = React.useState(false);
  const fieldStyle = {
    width: "100%", boxSizing: "border-box", fontFamily: "var(--font-sans)", fontSize: 13.5,
    color: "var(--ink)", background: "var(--surface-card)",
    border: `1px solid ${focus ? "var(--forest)" : "var(--line-2)"}`,
    boxShadow: focus ? "var(--ring-focus)" : "none", borderRadius: "var(--radius, 0)",
    padding: "11px 13px", outline: "none", lineHeight: 1.5, resize: multiline ? "vertical" : "none",
    transition: "border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease)",
  };
  return (
    <div className="wm-field" style={{ display: "flex", flexDirection: "column", gap: 7, ...style }}>
      {label ? (
        <label style={{ fontSize: 11, letterSpacing: "0.6px", textTransform: "uppercase", color: "var(--ink-faint)", fontWeight: 800 }}>
          {label}{optional ? <span style={{ textTransform: "none", letterSpacing: 0, color: "var(--ink-ghost)", fontWeight: 600 }}> — {optional}</span> : null}
        </label>
      ) : null}
      <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
        {icon ? <span style={{ position: "absolute", left: 12, display: "inline-flex", color: "var(--ink-faint)", pointerEvents: "none" }} aria-hidden="true">{icon}</span> : null}
        {multiline ? (
          <textarea rows={rows} placeholder={placeholder} value={value} onChange={onChange} onFocus={() => setFocus(true)} onBlur={() => setFocus(false)} style={{ ...fieldStyle, minHeight: 88, paddingLeft: icon ? 36 : 13 }} {...rest} />
        ) : (
          <input type="text" placeholder={placeholder} value={value} onChange={onChange} onFocus={() => setFocus(true)} onBlur={() => setFocus(false)} style={{ ...fieldStyle, paddingLeft: icon ? 36 : 13 }} {...rest} />
        )}
      </div>
      {hint ? <div style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 11.5, color: "var(--ink-faint)" }}>{hint}</div> : null}
    </div>
  );
}
