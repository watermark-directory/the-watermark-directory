import React from "react";

/**
 * AnnotationPin — a numbered square pin used on the guided walk and on document
 * scans. Forest = a read / annotation; oxblood = a scope gap or redaction.
 */
export function AnnotationPin({ n = 1, tone = "forest", size = 28, active = false, onClick, style, ...rest }) {
  const tones = {
    forest:  "var(--forest)",
    oxblood: "var(--ev-gap-fg)",
    muted:   "var(--ink-muted)",
  };
  const bg = tones[tone] || tones.forest;
  return (
    <span
      onClick={onClick}
      className={`wm-pin wm-pin--${tone}`}
      style={{
        display: "inline-flex", alignItems: "center", justifyContent: "center",
        width: size, height: size, flex: "0 0 auto",
        background: bg, color: "var(--bone-surface)",
        fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: Math.round(size * 0.46),
        borderRadius: "var(--radius, 0)",
        outline: active ? "2px solid var(--forest-line)" : "none", outlineOffset: 1,
        cursor: onClick ? "pointer" : "default", ...style,
      }}
      {...rest}
    >
      {n}
    </span>
  );
}
