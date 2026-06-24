// Watermark — the watershed / chronology screen (site tier). The record's timeline.
function WatershedScreen() {
  const { Eyebrow, Timeline } = window.WatermarkDesignSystem_dbe30a;
  const EVENTS = [
    { year: "2025", date: "2025-05-27", kind: "governance", title: "First executive session closed to the public", summary: "An R.C. 121.22(G)(8) session seals the earliest discussions — the start of the withholding stack the record later has to work around.", evidence: "open" },
    { year: "2025", date: "2025-07-11", kind: "cost estimate", title: "Tetra Tech Opinion of Probable Cost filed", summary: "A $14,223,081 roadwork program, priced to the dollar — but drainage is 7.5% of it, the only line itemized.", evidence: "verified", connect: [{ kind: "entity", label: "Tetra Tech" }, { kind: "record", label: "OPC pp.317–328" }] },
    { year: "2025", date: "2025-08-13", kind: "deed", title: "Seven-parcel deed recorded", summary: "Brenneman Trusts → Bistrozzi LLC, 340.2 ac. Only the 5-acre parcel carries a public price ($600k); six DTE-100s are blank.", evidence: "verified", connect: [{ kind: "entity", label: "Bistrozzi LLC" }] },
    { year: "2025", date: "2025-09-15", kind: "agreement", title: "Roadwork Development Agreement effective", summary: "The $14.5M “company contribution” is structured by §5.5 grant-refund, §9.13 records-notice, and §9.17 procurement waiver.", evidence: "verified", connect: [{ kind: "concept", label: "[[grant-refund-clause]]" }] },
    { year: "2026", date: "2026-03", kind: "disclosure", title: "Google confirmed as ultimate offtaker", summary: "An AEDG release ties the shell cluster to Google — turning a cross-doc inference into a verified attribution.", evidence: "verified" },
    { year: "2026", date: "2026-05-28", kind: "air permit", title: "Air Permit-to-Install P0138965 finalized", summary: "115 emissions units in three matched groups; per-engine power is CBI-locked, so ~313 MW survives only in the draft.", evidence: "verified", connect: [{ kind: "record", label: "PTI P0138965" }] },
    { year: "2026", date: "2026 · pending", kind: "records request", title: "Cost-benefit analysis withheld — mandamus thread open", summary: "PRR item 4 is refused; the public cost-vs-benefit basis remains out of the record as the mandamus proceeds.", evidence: "open" },
  ];
  return (
    <div style={{ color: "var(--ink)", padding: "28px 32px 40px" }}>
      <Eyebrow tone="forest">The watershed · chronology</Eyebrow>
      <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.6px", margin: "6px 0 4px" }}>How the record was assembled — and withheld.</h2>
      <p style={{ fontSize: 15, lineHeight: 1.55, color: "var(--ink-prose)", margin: "0 0 22px", maxWidth: 660 }}>Every beat carries its standing. Verified events are sourced; open events mark where the record is still being fought for.</p>
      <Timeline events={EVENTS} />
    </div>
  );
}
Object.assign(window, { WatershedScreen });
