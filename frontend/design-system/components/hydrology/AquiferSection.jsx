import React from "react";

const FOREST = "var(--data-1)", AMBER = "var(--ev-inference-fg)", OX = "var(--ev-gap-fg)";
const INK = "var(--ink)", MONO = "var(--font-mono)", FAINT = "var(--ink-faint)", MUTED = "var(--ink-muted)";
const SUB = "#efe9da"; // dewatered subsurface (bone, slightly warmer than surface)
const r = (n) => Math.round(n * 10) / 10;

/**
 * AquiferSection — the cone of depression in cross-section. The forest dashed
 * line is the static (rest) water level; the amber curve is the drawn-down
 * surface during pumping. Domestic wells inside the cone can be marked. The
 * signature groundwater schematic.
 */
export function AquiferSection({
  drawdownFt = 42, drawdownLabel, wellLabel = "pumping well", staticLabel = "static water level",
  surfaceLabel = "ground surface", wells = [], height = 200, style, ...rest
}) {
  const GROUND = 40, STATIC = 92, W0 = 20, W1 = 340, wellX = 180;
  const dip = Math.min(98, drawdownFt * 1.57); // px below static at the well
  const coneBottom = r(STATIC + dip);
  // cone curve, well in the middle
  const cone = `M${W0} ${STATIC} C120 ${STATIC} 150 ${coneBottom} ${wellX} ${coneBottom} C210 ${coneBottom} 260 ${STATIC} ${W1} ${STATIC}`;

  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 360 ${height}`} style={{ width: "100%", height: "auto", display: "block" }}>
        {/* subsurface + saturated zone */}
        <rect x={W0} y={GROUND} width={W1 - W0} height={height - GROUND - 10} fill={SUB} />
        <rect x={W0} y={STATIC} width={W1 - W0} height={height - STATIC - 10} fill="rgba(31,111,74,0.10)" />
        {/* carve the dewatered cone back to bone, then stroke the drawn-down surface */}
        <path d={`${cone} L${W1} ${STATIC} Z`} fill={SUB} />
        <path d={cone} fill="none" stroke={AMBER} strokeWidth="2" />
        {/* static (rest) level */}
        <line x1={W0} y1={STATIC} x2={W1} y2={STATIC} stroke={FOREST} strokeWidth="1.5" strokeDasharray="5 3" />
        {/* ground surface */}
        <line x1={W0} y1={GROUND} x2={W1} y2={GROUND} stroke={INK} strokeWidth="1.5" />
        {/* domestic well markers */}
        {wells.map((w, i) => {
          const x = r(W0 + (W1 - W0) * w.x);
          return <rect key={i} x={x - 3} y={GROUND - 2} width="6" height={r(40 + (w.depthFrac || 0.4) * 80)} fill={MUTED} />;
        })}
        {/* pumping well casing */}
        <rect x={wellX - 6} y={GROUND - 6} width="12" height={coneBottom - GROUND + 6} fill={INK} />
        {/* drawdown dimension */}
        <line x1={wellX} y1={STATIC} x2={wellX} y2={coneBottom} stroke={OX} strokeWidth="1.5" />
        <text x={wellX + 8} y={r((STATIC + coneBottom) / 2 + 4)} fontFamily={MONO} fontSize="11" fontWeight="700" fill={OX}>{drawdownLabel || drawdownFt + " ft"}</text>
        {/* labels */}
        <text x={W0 + 4} y={GROUND + 12} fontFamily={MONO} fontSize="9" fill={MUTED}>{surfaceLabel}</text>
        <text x={W0 + 4} y={STATIC - 4} fontFamily={MONO} fontSize="9" fontWeight="600" fill={FOREST}>{staticLabel}</text>
        <text x={wellX} y={Math.min(coneBottom + 16, height - 4)} textAnchor="middle" fontFamily={MONO} fontSize="8.5" fill={AMBER}>{wellLabel}</text>
        {wells.map((w, i) => {
          const x = r(W0 + (W1 - W0) * w.x);
          return w.label ? <text key={i} x={x} y={GROUND + 60} textAnchor="middle" fontFamily={MONO} fontSize="8" fill={FAINT}>{w.label}</text> : null;
        })}
      </svg>
    </div>
  );
}
