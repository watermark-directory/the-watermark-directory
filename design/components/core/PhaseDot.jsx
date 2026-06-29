import React from "react";

const PHASE = {
  live:     { label: "Live",     color: "var(--forest)" },
  building: { label: "Building", color: "var(--ink)" },
  queued:   { label: "Queued",   color: "var(--ink-muted)" },
  tracking: { label: "Tracking", color: "var(--ink-faint)" },
};

/**
 * PhaseDot — the build-phase marker used across the directory.
 * A mono uppercase label preceded by a square status dot in the phase color.
 */
export function PhaseDot({ phase = "live", label, size = "md", style, ...rest }) {
  const p = PHASE[phase] || PHASE.tracking;
  const dot = size === "sm" ? 6 : 7;
  const fs = size === "sm" ? 10 : 11;
  return (
    <span
      className={`wm-phase wm-phase--${phase}`}
      style={{
        display: "inline-flex", alignItems: "center", gap: 7,
        fontFamily: "var(--font-mono)", fontSize: fs, fontWeight: 600,
        letterSpacing: "0.5px", textTransform: "uppercase", color: p.color, ...style,
      }}
      {...rest}
    >
      <span style={{ width: dot, height: dot, background: p.color, flex: "0 0 auto" }} aria-hidden="true" />
      {label || p.label}
    </span>
  );
}
