// Watermark — the grouped site selector. Drops from the "All sites" chip / site chip.
// Search + group-by basin; each row is a site with codename + phase.
function SiteSelector({ active, onPick }) {
  const { PhaseDot } = window.WatermarkDesignSystem_dbe30a;
  const groups = [
    { basin: "Maumee", sites: [
      { code: "BOSC", place: "Lima", note: "Ottawa River", phase: "live" },
      { code: "GCP", place: "Fort Wayne", note: "headwaters", phase: "building" },
      { code: "DEF", place: "Defiance", note: "mainstem", phase: "queued" },
      { code: "TOL", place: "Toledo", note: "mouth · Lake Erie", phase: "queued" },
    ]},
    { basin: "Great Miami", sites: [
      { code: "DAY", place: "Dayton", note: "WPAFB", phase: "queued" },
    ]},
    { basin: "Scioto", sites: [
      { code: "NAL", place: "New Albany", note: "CHIPS megasite", phase: "tracking" },
      { code: "COL", place: "Columbus", note: "mainstem", phase: "tracking" },
    ]},
    { basin: "Mahoning", sites: [
      { code: "LDT", place: "Lordstown", note: "Voltage Valley", phase: "tracking" },
    ]},
  ];
  return (
    <div style={{ background: "var(--surface-card)", border: "1px solid var(--line-2)", borderTop: "3px solid var(--forest)", boxShadow: "none" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 16px", borderBottom: "1px solid var(--line-hair)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flex: "1 1 auto", background: "var(--bone-sunk)", border: "1px solid var(--line-hair)", padding: "7px 11px" }}>
          <window.WmIcon size={14} stroke="var(--ink-faint)" sw={2}><circle cx="11" cy="11" r="6.5" /><line x1="16" y1="16" x2="21" y2="21" /></window.WmIcon>
          <span style={{ fontSize: 13, color: "var(--ink-faint)" }}>Filter sites…</span>
        </div>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "0.8px", textTransform: "uppercase", color: "var(--ink-faint)" }}>grouped by basin</span>
      </div>
      <div style={{ maxHeight: 380, overflow: "auto", padding: "6px 0" }}>
        {groups.map((g) => (
          <div key={g.basin}>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: "1px", textTransform: "uppercase", color: "var(--ink-faint)", padding: "10px 16px 5px" }}>{g.basin} basin</div>
            {g.sites.map((s) => {
              const on = active === s.place;
              return (
                <div key={s.code} onClick={() => onPick && onPick(s)} style={{ display: "flex", alignItems: "center", gap: 12, padding: "9px 16px", cursor: "pointer", background: on ? "var(--forest-tint)" : "transparent" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700, letterSpacing: "0.4px", color: on ? "var(--forest)" : "var(--ink-muted)", background: on ? "transparent" : "var(--bone-sunk)", border: `1px solid ${on ? "var(--forest-line)" : "var(--line-hair)"}`, padding: "3px 6px", width: 44, textAlign: "center" }}>{s.code}</span>
                  <span style={{ flex: "1 1 auto", minWidth: 0 }}>
                    <span style={{ display: "block", fontSize: 14, fontWeight: 700 }}>{s.place}</span>
                    <span style={{ display: "block", fontSize: 11.5, color: "var(--ink-faint)" }}>{s.note}</span>
                  </span>
                  <PhaseDot phase={s.phase} size="sm" />
                  {on ? <span style={{ color: "var(--forest)", fontWeight: 800 }}>✓</span> : <span style={{ color: "var(--ink-ghost)" }}>›</span>}
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 16px", borderTop: "1px solid var(--line-hair)", background: "var(--bone-sunk)" }}>
        <span style={{ fontSize: 12, color: "var(--ink-muted)" }}><b>32</b> sites · <b>9</b> basins</span>
        <span style={{ marginLeft: "auto", fontSize: 12.5, fontWeight: 700, color: "var(--forest)", cursor: "pointer" }}>Open the full directory →</span>
      </div>
    </div>
  );
}
Object.assign(window, { SiteSelector });
