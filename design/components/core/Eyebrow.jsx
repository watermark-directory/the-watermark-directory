import React from "react";

/**
 * Eyebrow — the mono uppercase part-label that sits above headings and section
 * starts. Carries the documentary register. tone sets the ink.
 */
export function Eyebrow({ children, tone = "muted", as = "div", style, ...rest }) {
  const tones = {
    muted:  "var(--ink-muted)",
    faint:  "var(--ink-faint)",
    forest: "var(--forest)",
    ink:    "var(--ink)",
  };
  const Tag = as;
  return (
    <Tag
      className={`wm-eyebrow wm-eyebrow--${tone}`}
      style={{
        fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 600,
        letterSpacing: "1.6px", textTransform: "uppercase",
        color: tones[tone] || tones.muted, ...style,
      }}
      {...rest}
    >
      {children}
    </Tag>
  );
}
