// Watermark — the directory home (network tier). Hero + network ledger, three lenses,
// "start here" doors, and the across-the-network table.
function DirectoryHome({ onEnterSite }) {
  const { Eyebrow, Button, PhaseDot, EvidenceTag } = window.WatermarkDesignSystem_dbe30a;
  const ink = "#16201a", muted = "#566159", faint = "#8c9389", forest = "#1f6f4a";
  const stats = [["32", "SITES"], ["09", "BASINS"], ["01", "LIVE REFERENCE"], ["41", "CONTRIBUTORS"]];
  const phaseSegs = [["3%", forest], ["3%", ink], ["19%", muted], ["75%", faint]];
  const phaseLegend = [[forest, "1 live"], [ink, "1 building"], [muted, "6 queued"], [faint, "24 tracking"]];
  const lenses = [
    { n: "H1", name: "Water & Power", claim: "Where compute meets the watershed.", status: "Reference build", live: true },
    { n: "H2", name: "Defense & Federal Enclave", claim: "Where it meets federal land & the defense base.", status: "Emerging", live: false },
    { n: "H3", name: "Corporate & Economic Surveillance", claim: "Who owns it, and where the money moves.", status: "Emerging", live: false },
  ];
  const doors = [
    { nn: "01", title: "The reference build", meta: "LIMA (BOSC) · LIVE", desc: "The one fully-assembled site — and the best place to start. New here? Its guided walk teaches you to read the record.", cta: "Enter the site", act: true },
    { nn: "02", title: "How the record is built", meta: "PROVENANCE-FIRST", desc: "Sources, labeled inference, and the two-clock model — what Watermark is, and how to read it.", cta: "Read the method" },
    { nn: "03", title: "Contribute a lead", meta: "NO ACCOUNT NEEDED", desc: "A document, a name, a correction — every confirmed figure started as a lead.", cta: "Submit a lead" },
  ];
  const process = [
    ["01", "Source", "Start at the document itself — a deed, a permit, a filing — scanned or linked, exactly as it was filed.", false],
    ["02", "Structured read", "We lift the load-bearing facts into fields you can scan — parties, parcels, figures, dates.", false],
    ["03", "Meaning", "What those facts add up to, said plainly — and connected to the entities, places, and concepts around them.", false],
    ["04", "Verify", "Every figure carries its standing and a citation. Follow it back to the source — or flag where we’re wrong.", true],
  ];
  const grammar = [
    ["verified", "Backed by a cited source you can open."],
    ["inference", "Modeled or derived, and labeled as such."],
    ["open", "An unverified lead, published for you to corroborate."],
    ["gap", "Withheld or redacted — the gap is shown, not hidden."],
    ["key", "The one number a whole record turns on."],
  ];
  const featured = [
    ["BOSC", "Lima", "Maumee · Ottawa River", "live"],
    ["GCP", "Fort Wayne", "Maumee headwaters", "building"],
    ["DEF", "Defiance", "Maumee mainstem", "queued"],
    ["DAY", "Dayton", "Great Miami · WPAFB", "queued"],
    ["TOL", "Toledo", "Maumee mouth · Lake Erie", "queued"],
    ["NAL", "New Albany", "Scioto · CHIPS megasite", "tracking"],
    ["LDT", "Lordstown", "Mahoning · Voltage Valley", "tracking"],
    ["COL", "Columbus", "Scioto mainstem", "tracking"],
  ];
  return (
    <div style={{ color: "var(--ink)" }}>
      {/* hero */}
      <div style={{ display: "flex", gap: 40, padding: "42px 28px 34px", borderBottom: "1px solid var(--line-hair)", flexWrap: "wrap" }}>
        <div style={{ flex: "1 1 520px", maxWidth: 600 }}>
          <Eyebrow>The Watermark directory</Eyebrow>
          <h1 style={{ fontSize: 52, fontWeight: 800, letterSpacing: "-2px", lineHeight: 0.98, margin: "14px 0 0" }}>The build-out, on the public record.</h1>
          <p style={{ fontSize: 16.5, lineHeight: 1.55, margin: "18px 0 0", maxWidth: 560, textWrap: "pretty" }}>Watermark assembles the public record behind the hyperscale data-center build-out — <b>32 sites across 9 basins</b>, each a point where compute meets ground, water, and power. Provenance-first, and built in the open.</p>
          <div style={{ display: "flex", gap: 12, marginTop: 26, flexWrap: "wrap" }}>
            <Button variant="solid" iconRight="→">Explore the directory</Button>
            <Button variant="ghost" onClick={onEnterSite} iconRight="→">See the reference build</Button>
          </div>
        </div>
        <div style={{ flex: "1 1 320px", maxWidth: 356, border: "1px solid var(--ink)" }}>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "1.5px", textTransform: "uppercase", color: muted, padding: "11px 14px", borderBottom: "1px solid var(--ink)" }}>Network at a glance</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", margin: "-1px 0 0 -1px" }}>
            {stats.map(([n, l]) => (
              <div key={l} style={{ borderLeft: "1px solid var(--line-hair)", borderTop: "1px solid var(--line-hair)", padding: "15px 16px" }}>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 30, fontWeight: 600, letterSpacing: "-1px", lineHeight: 1 }}>{n}</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "1px", textTransform: "uppercase", color: faint, marginTop: 6 }}>{l}</div>
              </div>
            ))}
          </div>
          <div style={{ padding: 14, borderTop: "1px solid var(--ink)" }}>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "1.5px", textTransform: "uppercase", color: muted, marginBottom: 9 }}>Build phase</div>
            <div style={{ display: "flex", height: 10, border: "1px solid var(--ink)" }}>
              {phaseSegs.map(([w, c], i) => <span key={i} style={{ width: w, background: c, borderRight: "1px solid #f5f2ea" }} />)}
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "5px 14px", marginTop: 11 }}>
              {phaseLegend.map(([c, l], i) => (
                <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontFamily: "var(--font-mono)", fontSize: 11, color: muted }}><span style={{ width: 8, height: 8, background: c }} />{l}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* lenses */}
      <div style={{ padding: "28px 28px 30px", borderBottom: "1px solid var(--line-hair)" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 11, marginBottom: 20, flexWrap: "wrap" }}>
          <h2 style={{ fontSize: 19, fontWeight: 800, letterSpacing: "-0.4px", margin: 0 }}>Read the network three ways</h2>
          <span style={{ fontSize: 13, color: faint }}>— one map, three hypotheses.</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", marginLeft: -1 }}>
          {lenses.map((L) => (
            <div key={L.n} style={{ borderLeft: "1px solid var(--line-hair)", padding: "4px 22px", cursor: "pointer" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600, color: L.live ? forest : ink, border: `1px solid ${L.live ? forest : ink}`, padding: "1px 7px" }}>{L.n}</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "1px", textTransform: "uppercase", color: L.live ? forest : faint }}>{L.status}</span>
              </div>
              <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: "-0.3px", marginTop: 13 }}>{L.name}</div>
              <div style={{ fontSize: 13, color: muted, lineHeight: 1.45, marginTop: 5 }}>{L.claim}</div>
            </div>
          ))}
        </div>
      </div>

      {/* how to read the record */}
      <div style={{ padding: "28px 28px 32px", borderBottom: "1px solid var(--line-hair)" }}>
        <Eyebrow style={{ marginBottom: 6 }}>How to read the record</Eyebrow>
        <h2 style={{ fontSize: 19, fontWeight: 800, letterSpacing: "-0.4px", margin: "0 0 20px", maxWidth: 680 }}>Source first, meaning second — never the other way around.</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", marginLeft: -1 }}>
          {process.map(([nn, title, desc, live]) => (
            <div key={nn} style={{ borderLeft: "1px solid var(--line-hair)", padding: "2px 20px" }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 22, fontWeight: 600, color: live ? forest : faint }}>{nn}</div>
              <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: "-0.2px", marginTop: 8 }}>{title}</div>
              <div style={{ fontSize: 13, color: muted, lineHeight: 1.5, marginTop: 7 }}>{desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* a lead, not a verdict — the evidence grammar */}
      <div style={{ display: "flex", gap: 48, padding: "30px 28px 34px", borderBottom: "1px solid var(--line-hair)", flexWrap: "wrap" }}>
        <div style={{ flex: "1 1 300px", maxWidth: 380 }}>
          <Eyebrow style={{ marginBottom: 6 }}>The evidence grammar</Eyebrow>
          <h2 style={{ fontSize: 30, fontWeight: 800, letterSpacing: "-1px", lineHeight: 1.05, margin: 0 }}>A lead, not a verdict.</h2>
          <p style={{ fontSize: 15, lineHeight: 1.55, margin: "16px 0 0", color: "var(--ink-soft, #3a4036)", textWrap: "pretty" }}>We publish unconfirmed material — but never as fact. Every figure, record, and claim wears its standing, so you always know what you’re reading: sourced, modeled, or still open. That tag is the whole contract.</p>
        </div>
        <div style={{ flex: "1 1 420px", maxWidth: 560, alignSelf: "center" }}>
          <div style={{ borderTop: "1px solid var(--line-hair)" }}>
            {grammar.map(([kind, desc]) => (
              <div key={kind} style={{ display: "flex", alignItems: "center", gap: 16, padding: "13px 0", borderBottom: "1px solid var(--line-hair)" }}>
                <span style={{ flex: "0 0 132px" }}><EvidenceTag kind={kind} /></span>
                <span style={{ fontSize: 13.5, color: muted }}>{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* start here */}
      <div style={{ padding: "26px 28px 30px", borderBottom: "1px solid var(--line-hair)" }}>
        <Eyebrow tone="faint" style={{ marginBottom: 18 }}>Start here</Eyebrow>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", marginLeft: -1 }}>
          {doors.map((d) => (
            <div key={d.nn} onClick={d.act ? onEnterSite : undefined} style={{ borderLeft: "1px solid var(--line-hair)", padding: "2px 22px", cursor: d.act ? "pointer" : "default", display: "flex", flexDirection: "column" }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 22, fontWeight: 600, color: faint }}>{d.nn}</div>
              <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: "-0.3px", marginTop: 8 }}>{d.title}</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "0.5px", color: faint, marginTop: 5 }}>{d.meta}</div>
              <div style={{ fontSize: 13, color: muted, lineHeight: 1.5, marginTop: 9, flex: "1 1 auto" }}>{d.desc}</div>
              <div style={{ fontSize: 13, fontWeight: 700, marginTop: 14, color: d.act ? forest : ink }}>{d.cta} →</div>
            </div>
          ))}
        </div>
      </div>

      {/* table */}
      <div style={{ padding: "26px 28px 30px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 11, marginBottom: 14, flexWrap: "wrap" }}>
          <Eyebrow tone="faint">Across the network</Eyebrow>
          <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.5px", color: ink, fontWeight: 600, cursor: "pointer" }}>See all 32 →</span>
        </div>
        <div style={{ borderTop: "1px solid var(--ink)", borderBottom: "1px solid var(--ink)" }}>
          <div style={{ display: "grid", gridTemplateColumns: "42px 70px 200px 1fr 130px", fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "1px", textTransform: "uppercase", color: faint, padding: "8px 6px", borderBottom: "1px solid var(--line-hair)" }}>
            <span>#</span><span>Code</span><span>Place</span><span>Basin</span><span style={{ textAlign: "right" }}>Phase</span>
          </div>
          {featured.map(([code, place, basin, phase], i) => (
            <div key={code} onClick={code === "BOSC" ? onEnterSite : undefined} style={{ display: "grid", gridTemplateColumns: "42px 70px 200px 1fr 130px", alignItems: "center", padding: "9px 6px", color: ink, background: i % 2 ? "var(--bone-band)" : "transparent", borderBottom: "1px solid var(--line-hair)", cursor: code === "BOSC" ? "pointer" : "default" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: faint }}>{String(i + 1).padStart(2, "0")}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600 }}>{code}</span>
              <span style={{ fontSize: 14, fontWeight: 600 }}>{place}</span>
              <span style={{ fontSize: 12.5, color: muted, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{basin}</span>
              <span style={{ display: "flex", justifyContent: "flex-end" }}><PhaseDot phase={phase} size="sm" /></span>
            </div>
          ))}
        </div>
      </div>

      {/* footer */}
      <div style={{ borderTop: "2px solid var(--ink)", padding: "20px 28px", display: "flex", alignItems: "center", gap: 22, flexWrap: "wrap" }}>
        <div style={{ fontSize: 13, lineHeight: 1.5, maxWidth: 600 }}><b>Draft — the record is still being assembled.</b> Every figure carries a source; inference is labeled; redactions are shown, not hidden.</div>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 13 }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 7, fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.5px", textTransform: "uppercase", color: ink, border: "1px solid var(--ink)", padding: "4px 11px" }}><span style={{ width: 7, height: 7, background: forest }} />provenance-first</span>
          <Button variant="solid" size="sm">Submit a lead</Button>
        </div>
      </div>
    </div>
  );
}
Object.assign(window, { DirectoryHome });
