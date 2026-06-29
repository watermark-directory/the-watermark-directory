import React from "react";

/**
 * ConnectChip — a "library door": a typed link out to a connected entity,
 * concept, timeline event, place, or person. The kind prefix is a tiny mono
 * uppercase tag; the value is the link text. Forest-tinted, square.
 */
export function ConnectChip({ kind = "entity", children, href = "#", tone = "forest", onClick, style, ...rest }) {
  const tones = {
    forest:  { fg: "var(--forest)", bg: "var(--forest-tint)", bd: "var(--forest-line)", kindFg: "#3a4a3e" },
    neutral: { fg: "var(--ink)",    bg: "var(--bone-sunk)",   bd: "var(--line-2)",      kindFg: "var(--ink-muted)" },
  };
  const t = tones[tone] || tones.forest;
  return (
    <a
      href={href}
      onClick={onClick}
      className={`wm-connect wm-connect--${kind}`}
      style={{
        display: "inline-flex", alignItems: "center", gap: 7,
        fontFamily: "var(--font-sans)", fontSize: 13, color: t.fg,
        textDecoration: "none", border: `1px solid ${t.bd}`, background: t.bg,
        borderRadius: "var(--radius, 0)", padding: "5px 12px",
        transition: "background var(--dur) var(--ease)", ...style,
      }}
      {...rest}
    >
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 9.5, fontWeight: 600, letterSpacing: "0.6px", textTransform: "uppercase", color: t.kindFg }}>
        {kind}
      </span>
      {children}
    </a>
  );
}
