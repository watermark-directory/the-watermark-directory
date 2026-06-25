import React from "react";

const EV = {
  verified:  { text: "verified",  color: "var(--ev-verified-fg)",  bg: "var(--ev-verified-bg)" },
  inference: { text: "inference", color: "var(--ev-inference-fg)", bg: "var(--ev-inference-bg)" },
  open:      { text: "open",      color: "var(--ev-open-fg)",      bg: "var(--ev-open-bg)" },
};

// Recursive renderer for a structured field value: objects → a key/value tree,
// arrays → a bulleted list, scalars → a mono leaf. A leaf whose string carries the
// `~` approximate marker renders oxblood (the transcription-uncertain convention).
function FieldValue({ value }) {
  const leaf = (v) => {
    const s = String(v);
    const approx = s.trim().startsWith("~");
    return <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: approx ? "var(--ev-gap-fg)" : "var(--ink)" }}>{s}</span>;
  };
  if (Array.isArray(value)) {
    return (
      <ul style={{ margin: 0, paddingLeft: 22, display: "flex", flexDirection: "column", gap: 4, lineHeight: 1.5 }}>
        {value.map((item, i) => <li key={i}>{item && typeof item === "object" ? <FieldValue value={item} /> : leaf(item)}</li>)}
      </ul>
    );
  }
  if (value && typeof value === "object") {
    return (
      <ul style={{ margin: 0, listStyle: "none", paddingLeft: 12, borderLeft: "1px solid var(--forest-line)", display: "flex", flexDirection: "column", gap: 4, lineHeight: 1.5 }}>
        {Object.entries(value).map(([k, v]) => (
          <li key={k}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-muted)" }}>{k}:</span>{" "}
            {v && typeof v === "object" ? <FieldValue value={v} /> : leaf(v)}
          </li>
        ))}
      </ul>
    );
  }
  return leaf(value);
}

/**
 * RecordBlock — the canonical record card. `full` is reference density (header, an
 * optional "seen in the story" backlink, flat fields, structured nested-field trees,
 * gaps, a provenance footer with a structured `verify {href,label}` + `correctHref`,
 * and connect chips); `compact` is a list row carrying a "↩ story Ch.N" badge.
 */
export function RecordBlock({ density = "full", record = {}, style, ...rest }) {
  const r = record;
  const t = EV[r.evidence] || EV.open;

  if (density === "compact") {
    return (
      <a href={r.href || "#"} className="wm-record wm-record--compact" style={{ display: "flex", alignItems: "center", gap: 14, textDecoration: "none", color: "var(--ink)", background: "var(--surface-card)", border: "1px solid var(--border-card)", padding: "12px 16px", ...style }} {...rest}>
        <span style={{ flex: "0 0 3px", alignSelf: "stretch", background: "var(--forest)", minHeight: 30 }} />
        <span style={{ flex: "1 1 auto", minWidth: 0 }}>
          <span style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <span style={{ fontSize: 15, fontWeight: 700, letterSpacing: "-0.1px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{r.title}</span>
            {r.seenIn ? <span style={{ flex: "0 0 auto", fontSize: 11, fontWeight: 700, color: "var(--forest)", background: "var(--forest-tint)", border: "1px solid var(--forest-line)", padding: "1px 7px", whiteSpace: "nowrap" }}>↩ story Ch.{r.seenIn.ch}</span> : null}
          </span>
          <span style={{ display: "block", fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--ink-faint)", marginTop: 2 }}>{r.recordId}{r.source ? ` · ${r.source.collection}` : ""}</span>
        </span>
        {r.headlineValue ? <span style={{ flex: "0 0 auto", fontFamily: "var(--font-mono)", fontSize: 14, fontWeight: 700, color: r.headlineWarn ? "var(--ev-gap-fg)" : "var(--ink)" }}>{r.headlineValue}</span> : null}
        <span style={{ flex: "0 0 auto", display: "inline-flex", alignItems: "center", gap: 5, fontSize: 11, fontWeight: 700, color: t.color, background: t.bg, padding: "3px 9px" }}>
          <span style={{ width: 5, height: 5, background: t.color }} />[{t.text}]
        </span>
        <span style={{ flex: "0 0 auto", color: "var(--ink-ghost)", fontSize: 18 }}>›</span>
      </a>
    );
  }

  const rows = r.fields || [];
  return (
    <div className="wm-record wm-record--full" style={{ background: "var(--surface-card)", border: "1px solid var(--border-card)", overflow: "hidden", ...style }} {...rest}>
      <div style={{ padding: "15px 20px", borderBottom: "1px solid var(--line-faint)", display: "flex", alignItems: "flex-start", gap: 13 }}>
        <div style={{ flex: "0 0 4px", alignSelf: "stretch", background: "var(--forest)", minHeight: 40 }} />
        <div style={{ flex: "1 1 auto", minWidth: 0 }}>
          <div style={{ fontFamily: "var(--font-sans)", fontSize: 11, letterSpacing: "1.3px", textTransform: "uppercase", color: "var(--forest)", fontWeight: 700 }}>{r.kind}</div>
          <div style={{ fontSize: 19, fontWeight: 700, letterSpacing: "-0.2px", marginTop: 2 }}>{r.title}</div>
          {r.recordId ? <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--ink-faint)", marginTop: 3 }}>{r.recordId}</div> : null}
        </div>
        <div style={{ flex: "0 0 auto", display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 700, color: t.color, background: t.bg, padding: "3px 11px" }}>
          <span style={{ width: 6, height: 6, background: t.color }} />[{t.text}]
        </div>
      </div>

      {/* seen-in-the-story backlink — present when a story chapter tears this record down */}
      {r.seenIn ? (
        <a href={r.seenIn.href} style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", textDecoration: "none", padding: "9px 20px", background: "var(--forest-tint)", borderBottom: "1px solid var(--line-faint)" }}>
          <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: "0.8px", textTransform: "uppercase", color: "var(--bone-surface)", background: "var(--forest)", padding: "2px 7px" }}>↩ seen in the story</span>
          <span style={{ fontSize: 12, color: "var(--ink-prose)" }}>Chapter {r.seenIn.ch} · <b style={{ color: "var(--forest)" }}>{r.seenIn.label}</b></span>
          <span style={{ marginLeft: "auto", fontSize: 12, color: "var(--forest)" }}>resume the story ›</span>
        </a>
      ) : null}

      {rows.length ? (
        <div style={{ padding: "16px 20px 6px" }}>
          <div style={{ fontSize: 11, letterSpacing: "1px", textTransform: "uppercase", color: "var(--ink-faint)", fontWeight: 700, marginBottom: 8 }}>Fields</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 30px" }}>
            {rows.map((row, i) => {
              const ft = row.tag ? (EV[row.tag] || EV.open) : null;
              return (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12, padding: "8px 0", borderBottom: "1px solid var(--line-faint)" }}>
                  <div style={{ fontSize: 13, color: "var(--ink-muted)" }}>{row.label}</div>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 7 }}>
                    {ft ? <span style={{ fontSize: 10, fontWeight: 700, color: ft.color, background: ft.bg, padding: "1px 6px" }}>[{ft.text}]</span> : null}
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: 13, fontWeight: 600, textAlign: "right", color: row.warn ? "var(--ev-gap-fg)" : "var(--ink)" }}>{row.value}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      {/* structured (object/array) fields — rendered as a key/value tree, `~` leaves oxblood */}
      {r.nested && r.nested.length ? (
        <div style={{ padding: "4px 20px 12px", display: "flex", flexDirection: "column", gap: 12 }}>
          {r.nested.map((n, i) => (
            <div key={i}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--forest)", fontWeight: 700, marginBottom: 5 }}>{n.label}</div>
              <FieldValue value={n.value} />
            </div>
          ))}
        </div>
      ) : null}

      {r.warnings && r.warnings.length ? (
        <div style={{ margin: "8px 20px 0", border: "1px solid var(--ev-gap-border)", background: "var(--ev-gap-bg)", padding: "11px 14px" }}>
          <div style={{ fontSize: 11, letterSpacing: "0.8px", textTransform: "uppercase", color: "var(--ev-gap-fg)", fontWeight: 700, marginBottom: 5 }}>⚠ Gaps in the record</div>
          {r.warnings.map((w, i) => <div key={i} style={{ fontSize: 13, color: "#6a3b34", lineHeight: 1.45 }}>{w}</div>)}
        </div>
      ) : null}

      {r.source ? (
        <div style={{ marginTop: 14, padding: "13px 20px", background: "var(--bone-sunk)", borderTop: "1px solid var(--line-faint)", display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 0 }}>
            <div style={{ width: 13, height: 16, border: "1.5px solid var(--ink-faint)", flex: "0 0 auto" }} />
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 11.5, color: "var(--ink-muted)", lineHeight: 1.45, minWidth: 0 }}>{r.source.file}<span style={{ color: "var(--ink-ghost)" }}> · </span>{r.source.pages}<span style={{ color: "var(--ink-ghost)" }}> · </span>{r.source.collection}</div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 16 }}>
            {r.verify ? <a href={r.verify.href} style={{ fontSize: 13, color: "var(--forest)", textDecoration: "none", fontWeight: 600, whiteSpace: "nowrap" }}>↗ {r.verify.label}</a> : null}
            {r.correctHref ? <a href={r.correctHref} style={{ fontSize: 12.5, color: "var(--ink-faint)", textDecoration: "none", whiteSpace: "nowrap" }}>✎ Suggest a correction</a> : null}
          </div>
        </div>
      ) : null}

      {r.connect && r.connect.length ? (
        <div style={{ padding: "13px 20px 16px", borderTop: "1px solid var(--line-faint)" }}>
          <div style={{ fontSize: 11, letterSpacing: "1px", textTransform: "uppercase", color: "var(--ink-faint)", fontWeight: 700, marginBottom: 9 }}>Where it connects</div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {r.connect.map((c, i) => (
              <a key={i} href={c.href || "#"} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--forest)", textDecoration: "none", border: "1px solid var(--forest-line)", background: "var(--forest-tint)", padding: "5px 13px" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 9.5, letterSpacing: "0.6px", textTransform: "uppercase", color: "#3a4a3e", fontWeight: 600 }}>{c.kind}</span>{c.label}
              </a>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
