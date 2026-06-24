// Watermark — adaptive site home. The same landing reveals as the record fills in:
// Investigation (open leads) ↔ Live (two doors + the six-chapter walk + corpus).
function SiteHome({ phase = "live", onOpenRecord, onOpenLeads }) {
  const { Eyebrow, Button, LeadCard, SectionCard } = window.WatermarkDesignSystem_dbe30a;
  const isLive = phase === "live";

  const chapters = [
    ["1", "Who is actually building this?", "Reading a deed · entity resolution"],
    ["2", "How it was assembled & hidden", "Options-to-assignment · confidentiality-first"],
    ["3", "How big is it — and what won't they tell you?", "Reading an air permit · CBI redaction"],
    ["4", "What it does to the water", "NPDES permit · the 7Q10 low-flow screen"],
    ["5", "What it costs the public", "A cost estimate · a contract clause"],
    ["6", "How to read it yourself", "Citations · confidence tags · where it's silent"],
  ];
  const corpus = [["1,615", "source files"], ["55", "records"], ["174", "timeline events"], ["72", "entities & places"], ["13", "essays"]];
  const leads = [
    { kind: "Open question", confidence: "unanswered", title: "Who is behind the Parcel 7 buyer?", detail: "The deed names a trust with no public principals. Anyone recognize the agent?", source: "Auditor · 0008300", action: "Answer this", count: "open thread" },
    { kind: "Redaction", confidence: "withheld", title: "Land price — withheld", detail: "The transfer shows the sale, but the consideration field is blank. Have the auditor card?", source: "Transfer · 2025", action: "Fill the gap", count: "2 looking" },
    { kind: "Signal", confidence: "low", title: "A Delaware LLC quietly assembled four parcels", detail: "Same registered agent as two known data-center shells. Not yet tied to an operator.", source: "OH Sec. of State · 2025", action: "Help confirm", count: "3 on this" },
    { kind: "Claim", confidence: "review", title: "A 200 MW substation upgrade is planned", detail: "Heard at a zoning meeting; no filing found yet. Corroborate with a document?", source: "Public comment", action: "Corroborate", count: "1 corroboration" },
  ];

  return (
    <div style={{ color: "var(--ink)" }}>
      {/* state banner */}
      {isLive ? (
        <div style={{ background: "var(--forest-tint)", borderBottom: "1px solid var(--line-hair)", padding: "9px 30px", display: "flex", alignItems: "center", gap: 11, flexWrap: "wrap" }}>
          <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: "0.5px", textTransform: "uppercase", color: "var(--forest)", background: "#dde8df", border: "1px solid var(--forest-line)", padding: "2px 8px" }}>Live record</span>
          <span style={{ fontSize: 13, color: "#2c3a30" }}>Sourced end to end. Follow any citation to its source.</span>
        </div>
      ) : (
        <div style={{ background: "#f6efe0", borderBottom: "1px solid #e6d8b8", padding: "9px 30px", display: "flex", alignItems: "center", gap: 11, flexWrap: "wrap" }}>
          <span style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: "0.5px", textTransform: "uppercase", color: "var(--ev-inference-fg)", background: "var(--ev-inference-bg)", border: "1px solid var(--ev-inference-border)", padding: "2px 8px" }}>Open case</span>
          <span style={{ fontSize: 13, color: "#6a5524" }}>This site is <b>under investigation.</b> Most of what's here is inference — labeled, and open for you to confirm.</span>
        </div>
      )}

      <div style={{ padding: "34px 44px 30px" }}>
        <div style={{ display: "flex", gap: 30, alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 540px", maxWidth: 680 }}>
            <Eyebrow tone={isLive ? "forest" : "muted"} style={{ color: isLive ? "var(--forest)" : "var(--ev-inference-fg)" }}>{isLive ? "Public record · Lima, Allen County, Ohio" : "Open investigation · Lima, Allen County, Ohio"}</Eyebrow>
            <h2 style={{ fontSize: 36, fontWeight: 800, letterSpacing: "-0.8px", lineHeight: 1.06, margin: "10px 0 0" }}>{isLive ? "A 340-acre data center, built to be invisible." : "We think a data center is coming here. Help prove it."}</h2>
            <p style={{ fontSize: 16.5, lineHeight: 1.55, color: "var(--ink-prose)", margin: "14px 0 0", textWrap: "pretty" }}>{isLive ? "A Delaware shell. Withheld land prices. Backup generators by the hundred. A cooling draw on a river whose design low flow is 0.2 cfs. The record was made thin on purpose — here it's reassembled in the open, and every figure is checkable." : "Land is moving and shells are forming, but nothing is confirmed. We've published the little that's on the record and every lead we're chasing — so the people who know can close the gaps."}</p>
          </div>
          <div style={{ flex: "0 0 300px", maxWidth: 300 }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 7 }}>
              <span style={{ fontSize: 11, letterSpacing: "0.8px", textTransform: "uppercase", color: "var(--ink-faint)", fontWeight: 700 }}>Record assembled</span>
              <span style={{ marginLeft: "auto", fontSize: 15, fontWeight: 800, fontFamily: "var(--font-mono)", color: isLive ? "var(--forest)" : "var(--ev-inference-fg)" }}>{isLive ? "100%" : "14%"}</span>
            </div>
            <div style={{ height: 9, background: "var(--ev-open-bg)", overflow: "hidden" }}><div style={{ width: isLive ? "100%" : "14%", height: "100%", background: isLive ? "var(--forest)" : "#c98a16" }} /></div>
            <div style={{ display: "flex", gap: 16, marginTop: 11, fontSize: 11.5, color: "var(--ink-faint)" }}>
              <span><b style={{ fontFamily: "var(--font-mono)", color: "#3a4036" }}>{isLive ? "55" : "3"}</b> sourced</span>
              <span><b style={{ fontFamily: "var(--font-mono)", color: "var(--ev-inference-fg)" }}>{isLive ? "0" : "12"}</b> open leads</span>
            </div>
          </div>
        </div>

        {isLive ? (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 26 }}>
              <a onClick={onOpenRecord} style={{ display: "flex", flexDirection: "column", textDecoration: "none", color: "var(--ink)", border: "1.5px solid var(--forest-line)", padding: 22, background: "var(--surface-card)", cursor: "pointer" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 9 }}><span style={{ fontSize: 11, letterSpacing: "1px", textTransform: "uppercase", color: "#3a4a3e", fontWeight: 700 }}>For the researcher</span><span style={{ marginLeft: "auto", fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--ink-faint)" }}>1,615 files</span></div>
                <div style={{ fontSize: 23, fontWeight: 800, letterSpacing: "-0.4px", margin: "9px 0 6px" }}>Browse the record</div>
                <div style={{ fontSize: 14.5, color: "var(--ink-muted)", lineHeight: 1.5 }}>Straight to the documents, records, timeline, and entities. Provenance-first; follow any citation to its source.</div>
                <div style={{ marginTop: 16, display: "inline-flex", alignItems: "center", gap: 8, alignSelf: "flex-start", background: "var(--surface-card)", border: "1.5px solid var(--line-2)", color: "#3a4036", fontWeight: 700, fontSize: 14, padding: "10px 18px" }}>Enter the library →</div>
              </a>
              <a style={{ display: "flex", flexDirection: "column", textDecoration: "none", color: "#f5f2ea", border: "1.5px solid var(--forest)", padding: 22, background: "var(--forest)", cursor: "pointer" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 9 }}><span style={{ fontSize: 11, letterSpacing: "1px", textTransform: "uppercase", color: "#bcd2c4", fontWeight: 700 }}>For the newcomer</span><span style={{ marginLeft: "auto", fontSize: 11, fontFamily: "var(--font-mono)", color: "#9aa890" }}>6 chapters · ~18 min</span></div>
                <div style={{ fontSize: 23, fontWeight: 800, letterSpacing: "-0.4px", margin: "9px 0 6px" }}>Take the guided walk</div>
                <div style={{ fontSize: 14.5, color: "#d4dccf", lineHeight: 1.5 }}>A staged path that teaches you to read the record one document at a time — no jargon, no prior knowledge.</div>
                <div style={{ marginTop: 16, display: "inline-flex", alignItems: "center", gap: 8, alignSelf: "flex-start", background: "#f5f2ea", color: "var(--forest)", fontWeight: 700, fontSize: 14, padding: "10px 18px" }}>▶ Start the walk →</div>
              </a>
            </div>

            <div style={{ marginTop: 26, paddingTop: 22, borderTop: "1px solid var(--line-faint)" }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginBottom: 15, flexWrap: "wrap" }}>
                <Eyebrow tone="faint">The story · in six chapters</Eyebrow>
                <span style={{ fontSize: 12.5, color: "var(--ink-faint)" }}>— one project, read one document at a time.</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {chapters.map(([n, title, method]) => (
                  <a key={n} onClick={n === "1" ? onOpenRecord : undefined} style={{ display: "flex", gap: 13, alignItems: "flex-start", textDecoration: "none", color: "var(--ink)", background: "var(--surface-card)", border: "1px solid var(--line-hair)", padding: "14px 15px", cursor: "pointer" }}>
                    <span style={{ flex: "0 0 auto", width: 26, height: 26, background: "var(--forest)", color: "#f5f2ea", fontSize: 13, fontWeight: 800, fontFamily: "var(--font-mono)", display: "flex", alignItems: "center", justifyContent: "center" }}>{n}</span>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontSize: 15, fontWeight: 700, lineHeight: 1.25 }}>{title}</div>
                      <div style={{ fontSize: 12, color: "var(--forest)", fontWeight: 600, marginTop: 3 }}>{method}</div>
                    </div>
                  </a>
                ))}
              </div>
            </div>

            <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid var(--line-faint)" }}>
              <Eyebrow tone="faint" style={{ marginBottom: 14 }}>The corpus at a glance</Eyebrow>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 20 }}>
                {corpus.map(([n, l]) => (
                  <div key={l}><div style={{ fontSize: 26, fontWeight: 800, fontFamily: "var(--font-mono)", letterSpacing: "-1px" }}>{n}</div><div style={{ fontSize: 12, color: "var(--ink-faint)" }}>{l}</div></div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <>
            <div style={{ marginTop: 26 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 13 }}>
                <Eyebrow style={{ color: "var(--ev-inference-fg)" }}>Open leads</Eyebrow>
                <span style={{ fontSize: 12, color: "var(--ink-faint)" }}>— unverified. Pick one up.</span>
                <span onClick={onOpenLeads} style={{ marginLeft: "auto", fontSize: 11, color: "var(--ink-ghost)", fontFamily: "var(--font-mono)", cursor: "pointer" }}>12 open · 4 shown →</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                {leads.map((l, i) => <LeadCard key={i} {...l} onAction={onOpenLeads} />)}
              </div>
            </div>
            <div style={{ marginTop: 26, background: "var(--ink)", padding: "22px 26px", display: "flex", alignItems: "center", gap: 22, flexWrap: "wrap" }}>
              <div style={{ flex: "1 1 360px" }}>
                <div style={{ fontSize: 11, letterSpacing: "1.1px", textTransform: "uppercase", color: "#a7b0a3", fontWeight: 700 }}>Build the record</div>
                <div style={{ fontSize: 21, fontWeight: 800, color: "#f5f2ea", marginTop: 4, letterSpacing: "-0.3px" }}>Know something about this site?</div>
                <div style={{ fontSize: 14, color: "#bcd2c4", marginTop: 6, lineHeight: 1.5 }}>A document, a name, a correction — drop it in. We treat every submission as a lead, not a verdict.</div>
              </div>
              <Button variant="solid" style={{ background: "#f5f2ea", color: "var(--ink)", borderColor: "#f5f2ea" }}>Submit a lead →</Button>
            </div>
          </>
        )}
      </div>

      <div style={{ padding: "14px 44px", background: "var(--bone-sunk)", borderTop: "1px solid var(--line-faint)", display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 700, color: isLive ? "var(--forest)" : "var(--ev-inference-fg)", background: isLive ? "var(--forest-tint)" : "var(--ev-inference-bg)", padding: "3px 11px" }}><span style={{ width: 6, height: 6, background: isLive ? "var(--forest)" : "var(--ev-inference-fg)" }} />{isLive ? "provenance-first" : "inference-labeled"}</span>
        <div style={{ fontSize: 13, color: "var(--ink-muted)", lineHeight: 1.5 }}><b style={{ color: "#3a4036" }}>{isLive ? "Draft." : "Open case."}</b> {isLive ? "Sourced figures carry citations; open leads stay labeled as inference until corroborated." : "Nothing here is a verdict. Leads are unverified until corroborated."}</div>
      </div>
    </div>
  );
}
Object.assign(window, { SiteHome });
