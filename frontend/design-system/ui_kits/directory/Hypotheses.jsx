// Watermark — the Hypotheses index (network tier). Pick a lens; the network re-reads
// under that thesis as a table of sites with their standing.
function Hypotheses() {
  const { Eyebrow, EvidenceTag, PhaseDot } = window.WatermarkDesignSystem_dbe30a;
  const [lens, setLens] = React.useState("H1");
  const LENSES = {
    H1: { name: "Water & Power", claim: "Where compute meets the watershed — cooling draw against design low flow.", live: true },
    H2: { name: "Defense & Federal Enclave", claim: "Where the build-out meets federal land and the defense base.", live: false },
    H3: { name: "Corporate & Economic Surveillance", claim: "Who owns it, through which shells, and where the money moves.", live: false },
  };
  const ROWS = {
    H1: [
      ["BOSC", "Lima", "Ottawa River · 7Q10 0.2 cfs", "verified", "live"],
      ["GCP", "Fort Wayne", "Maumee headwaters", "inference", "building"],
      ["DEF", "Defiance", "Maumee mainstem withdrawal", "inference", "queued"],
      ["TOL", "Toledo", "Lake Erie discharge", "open", "queued"],
    ],
    H2: [
      ["DAY", "Dayton", "Wright-Patterson AFB adjacency", "inference", "queued"],
      ["NAL", "New Albany", "CHIPS megasite · federal incentive", "open", "tracking"],
    ],
    H3: [
      ["BOSC", "Lima", "Bistrozzi LLC · Delaware shell cluster", "verified", "live"],
      ["COL", "Columbus", "Common registered agent", "open", "tracking"],
      ["LDT", "Lordstown", "Voltage Valley incentive stack", "open", "tracking"],
    ],
  };
  const L = LENSES[lens];
  return (
    <div style={{ color: "var(--ink)", padding: "34px 28px 40px" }}>
      <Eyebrow tone="forest">Hypotheses · the network, re-read</Eyebrow>
      <h1 style={{ fontSize: 38, fontWeight: 800, letterSpacing: "-1px", margin: "8px 0 6px", lineHeight: 1.03 }}>One map, three theses under test.</h1>
      <p style={{ fontSize: 16, lineHeight: 1.55, color: "var(--ink-prose)", margin: 0, maxWidth: 680, textWrap: "pretty" }}>Each lens reads the same 32 sites against a different question. These are hypotheses, not findings — every row carries its current standing.</p>

      <div style={{ display: "flex", gap: 1, marginTop: 24, borderBottom: "1px solid var(--line-hair)" }}>
        {Object.entries(LENSES).map(([k, v]) => {
          const on = lens === k;
          return (
            <span key={k} onClick={() => setLens(k)} style={{ display: "flex", alignItems: "center", gap: 9, padding: "11px 16px", cursor: "pointer", borderBottom: on ? "3px solid var(--forest)" : "3px solid transparent", marginBottom: -1 }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600, color: on ? "var(--forest)" : "var(--ink-muted)", border: `1px solid ${on ? "var(--forest)" : "var(--line-2)"}`, padding: "1px 7px" }}>{k}</span>
              <span style={{ fontSize: 14, fontWeight: on ? 700 : 500, color: on ? "var(--ink)" : "var(--ink-muted)" }}>{v.name}</span>
            </span>
          );
        })}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10, margin: "18px 0 12px", flexWrap: "wrap" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, fontWeight: 600, color: L.live ? "var(--forest)" : "var(--ink-muted)" }}>{lens}</span>
        <span style={{ fontSize: 14.5, color: "var(--ink-prose)" }}>{L.claim}</span>
        {L.live ? <EvidenceTag kind="verified" label="reference build" size="sm" /> : <EvidenceTag kind="inference" label="emerging" size="sm" />}
      </div>

      <div style={{ border: "1px solid var(--line-hair)" }}>
        <div style={{ display: "grid", gridTemplateColumns: "70px 180px 1fr 130px 120px", fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "1px", textTransform: "uppercase", color: "var(--ink-faint)", padding: "9px 14px", background: "var(--bone-sunk)", borderBottom: "1px solid var(--line-hair)" }}>
          <span>Code</span><span>Place</span><span>Reading under {lens}</span><span>Standing</span><span style={{ textAlign: "right" }}>Phase</span>
        </div>
        {ROWS[lens].map((r, i) => (
          <div key={r[0] + i} style={{ display: "grid", gridTemplateColumns: "70px 180px 1fr 130px 120px", alignItems: "center", padding: "12px 14px", borderBottom: i < ROWS[lens].length - 1 ? "1px solid var(--line-faint)" : "none", background: i % 2 ? "var(--bone-band)" : "transparent" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600 }}>{r[0]}</span>
            <span style={{ fontSize: 14, fontWeight: 600 }}>{r[1]}</span>
            <span style={{ fontSize: 13, color: "var(--ink-muted)" }}>{r[2]}</span>
            <span><EvidenceTag kind={r[3]} size="sm" /></span>
            <span style={{ display: "flex", justifyContent: "flex-end" }}><PhaseDot phase={r[4]} size="sm" /></span>
          </div>
        ))}
      </div>
    </div>
  );
}
Object.assign(window, { Hypotheses });
