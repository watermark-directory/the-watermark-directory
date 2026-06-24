// Watermark — the leads board. Every open thread for a site, filterable by kind.
function LeadsBoard({ onBack }) {
  const { Eyebrow, LeadCard, EvidenceTag } = window.WatermarkDesignSystem_dbe30a;
  const [filter, setFilter] = React.useState("all");
  const LEADS = [
    { kind: "Open question", confidence: "unanswered", title: "Who is behind the Parcel 7 buyer?", detail: "The deed names a trust with no public principals. Anyone recognize the agent?", source: "Auditor · 0008300", action: "Answer this", count: "open thread", g: "question" },
    { kind: "Redaction", confidence: "withheld", title: "Land price — withheld", detail: "The transfer shows the sale, but the consideration field is blank. Have the auditor card?", source: "Transfer · 2025", action: "Fill the gap", count: "2 looking", g: "redaction" },
    { kind: "Signal", confidence: "low", title: "A Delaware LLC quietly assembled four parcels", detail: "Same registered agent as two known data-center shells. Not yet tied to an operator.", source: "OH Sec. of State · 2025", action: "Help confirm", count: "3 on this", g: "signal" },
    { kind: "Claim", confidence: "review", title: "A 200 MW substation upgrade is planned", detail: "Heard at a zoning meeting; no filing found yet. Corroborate with a document?", source: "Public comment", action: "Corroborate", count: "1 corroboration", g: "signal" },
    { kind: "Open question", confidence: "unanswered", title: "What is the cooling-water source of record?", detail: "The air permit implies a draw; the NPDES file doesn't name the intake. Which is it?", source: "PTI P0138965", action: "Answer this", count: "open thread", g: "question" },
    { kind: "Redaction", confidence: "withheld", title: "Generator count claimed as CBI", detail: "The emissions table is redacted as confidential business information. Anyone have the public-comment copy?", source: "OEPA · CBI", action: "Fill the gap", count: "4 looking", g: "redaction" },
  ];
  const FILTERS = [["all", "All"], ["question", "Questions"], ["redaction", "Redactions"], ["signal", "Signals"]];
  const shown = filter === "all" ? LEADS : LEADS.filter((l) => l.g === filter);
  return (
    <div style={{ color: "var(--ink)", padding: "30px 36px 40px" }}>
      <a onClick={onBack} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12.5, fontWeight: 600, color: "var(--forest)", textDecoration: "none", marginBottom: 14, cursor: "pointer" }}>← The site</a>
      <Eyebrow tone="forest">Open leads · Lima (BOSC)</Eyebrow>
      <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.8px", margin: "8px 0 6px" }}>Twelve threads, open in the record.</h1>
      <p style={{ fontSize: 15.5, lineHeight: 1.55, color: "var(--ink-prose)", margin: 0, maxWidth: 640 }}>Each is published as a lead, not a verdict. Pick one up — bring a document, a name, or a correction.</p>

      <div style={{ display: "flex", alignItems: "center", gap: 8, margin: "22px 0 16px", flexWrap: "wrap" }}>
        {FILTERS.map(([k, label]) => {
          const on = filter === k;
          return (
            <span key={k} onClick={() => setFilter(k)} style={{ fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600, letterSpacing: "0.4px", textTransform: "uppercase", color: on ? "#f5f2ea" : "var(--ink-muted)", background: on ? "var(--ink)" : "transparent", border: `1px solid ${on ? "var(--ink)" : "var(--line-2)"}`, padding: "5px 12px", cursor: "pointer" }}>{label}</span>
          );
        })}
        <span style={{ marginLeft: "auto", display: "inline-flex", alignItems: "center", gap: 8 }}>
          <EvidenceTag kind="open" label={`${shown.length} shown`} size="sm" dot={false} />
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {shown.map((l, i) => <LeadCard key={i} {...l} />)}
      </div>
    </div>
  );
}
Object.assign(window, { LeadsBoard });
