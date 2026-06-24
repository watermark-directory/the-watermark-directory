import React from "react";

const EV = {
  verified:  { text: "verified",  color: "var(--ev-verified-fg)",  bg: "var(--ev-verified-bg)" },
  inference: { text: "inference", color: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)" },
  open:      { text: "open",      color: "var(--ev-open-fg)",      bg: "var(--ev-open-bg)" },
};

/**
 * ProfileHeader — the wiki identity card for an entity, person, or place. Forest
 * rail + name + variants, evidence standing, a stat strip, an attributes grid, and
 * a graph-neighborhood relationship row.
 */
export function ProfileHeader({ profile = {}, style, ...rest }) {
  const p = profile;
  const t = EV[p.evidence] || EV.open;
  const stats = p.stats || [];
  const attrs = p.attrs || [];
  const rels = p.relationships || [];
  return (
    <div className="wm-profile" style={{ color: "var(--ink)", background: "#fff", border: "1px solid var(--ink)", overflow: "hidden", ...style }} {...rest}>
      {/* identity */}
      <div style={{ padding: "18px 22px 16px", display: "flex", alignItems: "flex-start", gap: 14 }}>
        <div style={{ flex: "0 0 4px", alignSelf: "stretch", background: "var(--forest)", minHeight: 54 }} />
        <div style={{ flex: "1 1 auto", minWidth: 0 }}>
          <div style={{ fontSize: 11, letterSpacing: "1.3px", textTransform: "uppercase", color: "var(--forest)", fontWeight: 700 }}>{p.kindLabel}</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap", marginTop: 3 }}>
            <div style={{ fontSize: 27, fontWeight: 800, letterSpacing: "-0.5px" }}>{p.name}</div>
            {(p.variants || []).map((v, i) => (
              <span key={i} style={{ fontSize: 12, fontFamily: "var(--font-mono)", color: "var(--ink-muted)", background: "var(--bone-sunk)", border: "1px solid var(--line-hair)", padding: "2px 8px" }}>{v}</span>
            ))}
          </div>
          {p.descriptor ? <div style={{ fontSize: 14.5, color: "var(--ink-prose)", lineHeight: 1.5, marginTop: 8, maxWidth: 640 }}>{p.descriptor}</div> : null}
        </div>
        <div style={{ flex: "0 0 auto", display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 9 }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 700, color: t.color, background: t.bg, padding: "3px 11px" }}><span style={{ width: 6, height: 6, background: t.color }} />[{t.text}]</span>
          {p.graph ? <a href="#" style={{ fontSize: 13, color: "var(--forest)", textDecoration: "none", fontWeight: 600, whiteSpace: "nowrap" }}>◉ View in graph</a> : null}
        </div>
      </div>

      {/* stat strip */}
      {stats.length ? (
        <div style={{ padding: "16px 22px", borderTop: "1px solid var(--line-faint)", display: "grid", gridTemplateColumns: `repeat(${stats.length}, 1fr)`, gap: 22 }}>
          {stats.map((s, i) => {
            const sc = EV[s.evidence] || EV.open;
            return (
              <div key={i} style={{ display: "flex", flexDirection: "column", gap: 3, minWidth: 0 }}>
                <div style={{ fontSize: 10.5, letterSpacing: "0.8px", textTransform: "uppercase", color: "var(--ink-faint)", fontWeight: 700 }}>{s.label}</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 7 }}>
                  <span style={{ fontSize: 20, fontWeight: 700, fontFamily: "var(--font-mono)", letterSpacing: "-0.4px", color: s.warn ? "var(--ev-gap-fg)" : "var(--ink)" }}>{s.value}</span>
                  <span style={{ width: 7, height: 7, background: sc.color }} />
                </div>
                {s.sub ? <div style={{ fontSize: 11, color: "var(--ink-faint)", fontFamily: "var(--font-mono)" }}>{s.sub}</div> : null}
              </div>
            );
          })}
        </div>
      ) : null}

      {/* attributes */}
      {attrs.length ? (
        <div style={{ padding: "14px 22px", borderTop: "1px solid var(--line-faint)", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 30px" }}>
          {attrs.map((a, i) => {
            const ft = a.tag ? (EV[a.tag] || EV.open) : null;
            return (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12, padding: "7px 0", borderBottom: "1px solid var(--line-faint)" }}>
                <div style={{ fontSize: 13, color: "var(--ink-muted)" }}>{a.label}</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 7 }}>
                  {ft ? <span style={{ fontSize: 10, fontWeight: 700, color: ft.color, background: ft.bg, padding: "1px 6px" }}>[{ft.text}]</span> : null}
                  <div style={{ fontSize: 13, fontWeight: 600, fontFamily: "var(--font-mono)", textAlign: "right", color: "var(--ink)" }}>{a.value}</div>
                </div>
              </div>
            );
          })}
        </div>
      ) : null}

      {/* relationships */}
      {rels.length ? (
        <div style={{ padding: "13px 22px", background: "var(--surface-card)", borderTop: "1px solid var(--line-faint)", display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", minWidth: 0 }}>
            <span style={{ fontSize: 11, letterSpacing: "0.8px", textTransform: "uppercase", color: "var(--ink-faint)", fontWeight: 700 }}>{p.relLabel || "Related"}</span>
            {rels.map((r, i) => (
              <a key={i} href="#" style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--ink)", textDecoration: "none", border: "1px solid var(--line-2)", background: "#fff", padding: "4px 11px" }}>
                <span style={{ fontSize: 10, letterSpacing: "0.5px", textTransform: "uppercase", color: "var(--forest)", fontWeight: 700 }}>{r.kind}</span>{r.label}
              </a>
            ))}
          </div>
          <a href="#" style={{ marginLeft: "auto", fontSize: 12.5, color: "var(--ink-muted)", textDecoration: "none", whiteSpace: "nowrap" }}>✎ Suggest a correction</a>
        </div>
      ) : null}
    </div>
  );
}
