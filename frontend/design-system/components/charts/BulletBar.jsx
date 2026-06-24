import React from "react";

const MONO = "var(--font-mono)";

// Typed evidence register — a row's note can declare its standing and take the
// matching evidence color (mirrors EvidenceTag), instead of a raw noteColor.
const EV = {
  verified: "var(--ev-verified-fg)", inference: "var(--ev-inference-fg)",
  open: "var(--ev-open-fg)", gap: "var(--ev-gap-fg)", key: "var(--ev-key-fg)",
};

/**
 * BulletBar — a measure against a limit (the comparison that is the whole
 * story). Each row carries its own label, evidence note, fill color, value,
 * and an optional `marker` (a red rule, e.g. a design low-flow limit).
 * `max` sets the shared scale across rows.
 */
export function BulletBar({ rows = [], max = 100, unit = "", style, ...rest }) {
  const pct = (v) => Math.max(0, Math.min(100, (v / max) * 100)) + "%";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, ...style }} {...rest}>
      {rows.map((row, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ flex: "0 0 150px" }}>
            <div style={{ fontFamily: "var(--font-sans)", fontSize: 13, fontWeight: 600, color: "var(--ink)" }}>{row.label}</div>
            {row.evidence ? (
              <div style={{ fontFamily: "var(--font-sans)", fontSize: 11, fontWeight: 700, color: EV[row.evidence] || "var(--ink-faint)" }}>
                [{row.evidence}]{row.evidenceNote ? ` · ${row.evidenceNote}` : ""}
              </div>
            ) : row.note ? <div style={{ fontFamily: "var(--font-sans)", fontSize: 11, fontWeight: 700, color: row.noteColor || "var(--ink-faint)" }}>{row.note}</div> : null}
          </div>
          <div style={{ flex: "1 1 auto", position: "relative", height: 22, background: "var(--forest-tint)", border: "1px solid var(--data-axis)", overflow: "hidden" }}>
            <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: pct(row.value), background: row.color || "var(--data-1)" }} />
            {row.marker != null ? <div style={{ position: "absolute", top: -3, bottom: -3, left: pct(row.marker), width: 2, background: "var(--ev-gap-fg)" }} /> : null}
          </div>
          <div style={{ flex: "0 0 84px", textAlign: "right", fontFamily: MONO, fontSize: 15, fontWeight: 700, color: "var(--ink)" }}>
            {row.value}{unit ? <span style={{ fontSize: 11, color: "var(--ink-faint)", marginLeft: 4 }}>{unit}</span> : null}
          </div>
        </div>
      ))}
    </div>
  );
}
