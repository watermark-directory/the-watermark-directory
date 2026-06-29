import React from "react";

const SERIES = ["var(--data-1)", "var(--data-2)", "var(--data-3)", "var(--data-4)", "var(--data-5)"];
const MONO = "var(--font-mono)";

/**
 * BarChart — categorical (vertical) or ranked (horizontal) bars in the
 * record grammar. Forest carries the data; figures are mono; light grid,
 * no chrome. Mark a bar `highlight` to make it the load-bearing one, or
 * `muted` to draw it as a withheld / secondary value.
 */
export function BarChart({
  data = [], max, orientation = "vertical", height = 200,
  unit = "", valueLabels = true, style, ...rest
}) {
  const vmax = max || Math.max(1, ...data.map((d) => d.value)) * (orientation === "vertical" ? 1.06 : 1);
  const r = (n) => Math.round(n * 10) / 10;
  const fillOf = (d) => (d.muted ? "var(--data-withheld)" : d.highlight ? "var(--data-1)" : "var(--data-3)");

  if (orientation === "horizontal") {
    const W = 360, x0 = 76, plotW = W - x0 - 38, rowH = 26, barH = 14;
    const H = data.length * rowH + 26;
    const ticks = [0, vmax / 2, vmax].map((v) => ({ v, x: r(x0 + (v / vmax) * plotW) }));
    return (
      <div style={{ width: "100%", ...style }} {...rest}>
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto", display: "block" }}>
          {ticks.map((t, i) => (
            <g key={i}>
              <line x1={t.x} y1="6" x2={t.x} y2={H - 20} stroke="var(--data-grid)" strokeWidth="1" />
              <text x={t.x} y={H - 6} textAnchor="middle" fontFamily={MONO} fontSize="9" fill="var(--ink-ghost)">{r(t.v)}</text>
            </g>
          ))}
          {data.map((d, i) => {
            const w = (d.value / vmax) * plotW;
            const y = 8 + i * rowH;
            const ty = y + barH / 2 + 3.5;
            return (
              <g key={i}>
                <text x="6" y={ty} fontFamily={MONO} fontSize="10" fill="var(--ink-muted)">{d.label}</text>
                <rect x={x0} y={y} width={r(w)} height={barH} fill={fillOf(d)} stroke={d.muted ? "var(--forest-line)" : "none"} strokeWidth={d.muted ? 1 : 0} />
                {valueLabels ? <text x={r(x0 + w + 6)} y={ty} fontFamily={MONO} fontSize="9.5" fill="var(--ink-muted)">{d.value}{unit ? " " + unit : ""}</text> : null}
              </g>
            );
          })}
        </svg>
      </div>
    );
  }

  // vertical
  const W = 360, l = 34, rpad = 12, top = 14, base = height - 28;
  const plotH = base - top, plotW = W - l - rpad, slot = plotW / Math.max(1, data.length), barW = Math.min(28, slot * 0.55);
  const gridVals = [0, 0.25, 0.5, 0.75, 1].map((f) => r(f * vmax));
  return (
    <div style={{ width: "100%", ...style }} {...rest}>
      <svg viewBox={`0 0 ${W} ${height}`} style={{ width: "100%", height: "auto", display: "block" }}>
        {gridVals.map((v, i) => {
          const y = r(base - (v / vmax) * plotH);
          return (
            <g key={i}>
              <line x1={l} y1={y} x2={W - rpad} y2={y} stroke="var(--data-grid)" strokeWidth="1" />
              <text x={l - 6} y={y + 3} textAnchor="end" fontFamily={MONO} fontSize="9" fill="var(--ink-ghost)">{v}</text>
            </g>
          );
        })}
        <line x1={l} y1={base} x2={W - rpad} y2={base} stroke="var(--data-axis)" strokeWidth="1" />
        {data.map((d, i) => {
          const h = (d.value / vmax) * plotH;
          const x = l + slot * i + (slot - barW) / 2;
          const cx = r(x + barW / 2);
          return (
            <g key={i}>
              <rect x={r(x)} y={r(base - h)} width={r(barW)} height={r(h)} fill={fillOf(d)} />
              {valueLabels ? <text x={cx} y={r(base - h - 5)} textAnchor="middle" fontFamily={MONO} fontSize="9" fontWeight={d.highlight ? 700 : 400} fill={d.highlight ? "var(--ink)" : "var(--ink-faint)"}>{d.value}</text> : null}
              <text x={cx} y={base + 16} textAnchor="middle" fontFamily={MONO} fontSize="10" fill="var(--ink-faint)">{d.label}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
