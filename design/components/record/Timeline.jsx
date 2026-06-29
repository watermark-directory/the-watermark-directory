import React from "react";

const EV = {
  verified:  { text: "verified",  color: "var(--ev-verified-fg)",  bg: "var(--ev-verified-bg)",  ring: "var(--ev-verified-border)" },
  inference: { text: "inference", color: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)", ring: "var(--ev-inference-border)" },
  open:      { text: "open",      color: "var(--ev-open-fg)",      bg: "var(--ev-open-bg)",      ring: "var(--ev-open-border)" },
};

/**
 * Timeline — the record's chronology. A single ink spine with square evidence-colored
 * nodes; year markers are forest diamonds. Each event is a card with its standing,
 * kind, summary, optional connect chips, and an optional "↩ story Ch.N" badge linking
 * to the story chapter that tears the event down. Inserts year dividers automatically.
 */
export function Timeline({ events = [], style, ...rest }) {
  const items = [];
  let lastYear = null;
  for (const e of events) {
    if (e.year !== lastYear) { items.push({ isYear: true, year: e.year }); lastYear = e.year; }
    items.push({ isYear: false, ...e });
  }
  return (
    <div className="wm-timeline" style={{ color: "var(--ink)", ...style }} {...rest}>
      {items.map((it, i) => {
        if (it.isYear) {
          return (
            <div key={`y${i}`} style={{ display: "flex", gap: 18, alignItems: "center" }}>
              <div style={{ flex: "0 0 64px", position: "relative", alignSelf: "stretch", minHeight: 46 }}>
                <div style={{ position: "absolute", left: 31, top: 0, bottom: 0, width: 2, background: "var(--line-2)" }} />
                <div style={{ position: "absolute", left: 24, top: "50%", transform: "translateY(-50%) rotate(45deg)", width: 16, height: 16, background: "var(--forest)", border: "2px solid var(--surface-card)", boxShadow: "0 0 0 2px var(--forest-line)" }} />
              </div>
              <div style={{ flex: "1 1 auto", display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ fontSize: 23, fontWeight: 800, fontFamily: "var(--font-mono)", color: "var(--forest)", letterSpacing: "-0.5px" }}>{it.year}</div>
                <div style={{ flex: "1 1 auto", height: 1, background: "var(--line-faint)" }} />
              </div>
            </div>
          );
        }
        const t = EV[it.evidence] || EV.open;
        return (
          <div key={`e${i}`} style={{ display: "flex", gap: 18 }}>
            <div style={{ flex: "0 0 64px", position: "relative", alignSelf: "stretch", minHeight: 74 }}>
              <div style={{ position: "absolute", left: 31, top: 0, bottom: 0, width: 2, background: "var(--line-2)" }} />
              <div style={{ position: "absolute", left: 25, top: 22, width: 14, height: 14, background: t.color, border: "2px solid var(--surface-card)", boxShadow: `0 0 0 2px ${t.ring}` }} />
            </div>
            <div style={{ flex: "1 1 auto", minWidth: 0, paddingBottom: 18 }}>
              <div style={{ background: "var(--surface-card)", border: "1px solid var(--line-hair)", padding: "13px 16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 5 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--ink-muted)" }}>{it.date}</span>
                  {it.kind ? <span style={{ fontSize: 10, letterSpacing: "0.7px", textTransform: "uppercase", color: "#3a4a3e", fontWeight: 700 }}>{it.kind}</span> : null}
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 11, fontWeight: 700, color: t.color, background: t.bg, padding: "2px 9px" }}><span style={{ width: 5, height: 5, background: t.color }} />[{t.text}]</span>
                  {it.seenInCh ? <a href={it.seenInHref || "#"} style={{ marginLeft: "auto", fontSize: 11, fontWeight: 700, color: "var(--forest)", background: "var(--forest-tint)", border: "1px solid var(--forest-line)", padding: "1px 7px", textDecoration: "none", whiteSpace: "nowrap" }}>↩ story Ch.{it.seenInCh}</a> : null}
                </div>
                <div style={{ fontSize: 15.5, fontWeight: 700, letterSpacing: "-0.1px" }}>{it.title}</div>
                {it.summary ? <div style={{ fontSize: 13.5, color: "var(--ink-muted)", lineHeight: 1.5, marginTop: 3 }}>{it.summary}</div> : null}
                {it.connect && it.connect.length ? (
                  <div style={{ display: "flex", gap: 7, flexWrap: "wrap", marginTop: 10 }}>
                    {it.connect.map((c, j) => (
                      <a key={j} href={c.href || "#"} style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 12, color: "var(--forest)", textDecoration: "none", border: "1px solid var(--forest-line)", background: "var(--forest-tint)", padding: "3px 10px" }}>
                        <span style={{ fontSize: 9, letterSpacing: "0.5px", textTransform: "uppercase", color: "#3a4a3e", fontWeight: 700 }}>{c.kind}</span>{c.label}
                      </a>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
