import React from "react";

const MAP = {
  verified:  { label: "verified",  fg: "var(--ev-verified-fg)",  bg: "var(--ev-verified-bg)",  bd: "var(--ev-verified-border)" },
  inference: { label: "inference", fg: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)", bd: "var(--ev-inference-border)" },
  open:      { label: "open",      fg: "var(--ev-open-fg)",      bg: "var(--ev-open-bg)",      bd: "var(--ev-open-border)" },
  gap:       { label: "scope gap", fg: "var(--ev-gap-fg)",       bg: "var(--ev-gap-bg)",       bd: "var(--ev-gap-border)" },
  key:       { label: "key figure",fg: "var(--ev-key-fg)",       bg: "var(--ev-key-bg)",       bd: "var(--ev-key-border)" },
};

/**
 * EvidenceTag — the load-bearing grammar of Watermark.
 * Every figure wears one of these so the reader always knows its standing.
 */
export function EvidenceTag({ kind = "verified", label, brackets = false, dot = true, size = "md", style, ...rest }) {
  const t = MAP[kind] || MAP.open;
  const text = label || t.label;
  const dim = size === "sm" ? { fontSize: 10, padding: "2px 7px", dot: 5 } : { fontSize: 11.5, padding: "3px 11px", dot: 6 };
  return (
    <span
      className={`wm-evidence wm-evidence--${kind}`}
      style={{
        display: "inline-flex", alignItems: "center", gap: 6,
        fontFamily: "var(--font-sans)", fontWeight: 700, fontSize: dim.fontSize,
        letterSpacing: "0.3px", lineHeight: 1.1,
        color: t.fg, background: t.bg, border: `1px solid ${t.bd}`,
        borderRadius: "var(--radius, 0)", padding: dim.padding, ...style,
      }}
      {...rest}
    >
      {dot ? <span style={{ width: dim.dot, height: dim.dot, background: t.fg, flex: "0 0 auto" }} aria-hidden="true" /> : null}
      {brackets ? `[${text}]` : text}
    </span>
  );
}
