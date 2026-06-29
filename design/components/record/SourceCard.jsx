import React from "react";

/**
 * SourceCard — the record's `① source` viewer. Mirrors the live TeardownSourceCard's
 * four-tier preview priority (the scan is shown, not hidden — the record never pretends
 * a gap isn't there):
 *   1. `crop`     — a committed scan crop of the real region, carrying its own redaction
 *                   overlay (the preferred preview for degraded scans);
 *   2. `embed`    — the live source document, embedded (only when the source is published);
 *   3. `fields`   — the real extraction rendered as a key/value facsimile from the feed;
 *   4. fallback   — a quiet "view source on request" pill.
 * A catalogued source that isn't embedded inline still links to its full viewer via `docHref`.
 */
export function SourceCard({ file = "document.pdf", badge = "SCAN", pages, collection, note, crop, embed, fields, docHref, redactionLabel, action = "View source on request", style, ...rest }) {
  const tier = crop ? "crop" : embed ? "embed" : (fields && fields.length) ? "facsimile" : "fallback";
  const showBar = redactionLabel && !(crop && crop.redaction);
  return (
    <div className="wm-source" style={{ maxWidth: 360, border: "1px solid var(--line-2)", background: "var(--surface-card)", overflow: "hidden", ...style }} {...rest}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px", background: "var(--bone-sunk)", borderBottom: "1px solid var(--line-2)" }}>
        <div style={{ width: 13, height: 16, border: "1.5px solid var(--ink-faint)", flex: "0 0 auto" }} />
        <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--ink-prose)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {docHref ? <a href={docHref} style={{ color: "var(--ink-prose)", textDecoration: "none" }}>{file}</a> : file}
        </div>
        {badge ? <div style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--ev-inference-fg)", background: "var(--ev-inference-bg)", padding: "2px 6px" }}>{badge}</div> : null}
      </div>

      <div style={{ position: "relative" }}>
        {/* tier 1 — committed scan crop + its own redaction overlay */}
        {tier === "crop" ? (
          <figure style={{ margin: 0, position: "relative", background: "var(--bone-sunk)" }}>
            <img src={crop.src} alt={crop.alt || "source scan crop"} style={{ display: "block", width: "100%" }} />
            {crop.redaction ? (
              <div style={{ position: "absolute", left: crop.redaction.x, top: crop.redaction.y, width: crop.redaction.w, height: crop.redaction.h, background: "var(--ink)", color: "var(--bone-surface)", fontSize: 9, fontFamily: "var(--font-mono)", letterSpacing: "0.5px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                {crop.redaction.label}
              </div>
            ) : null}
          </figure>
        ) : null}

        {/* tier 2 — live document embed (published sources only) */}
        {tier === "embed" ? (
          <div style={{ height: 120, background: "var(--bone-page)", border: "1px solid var(--line-hair)", margin: 8, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 6, color: "var(--ink-muted)" }}>
            <div style={{ width: 26, height: 32, border: "1.5px solid var(--ink-faint)" }} />
            <div style={{ fontSize: 11, fontFamily: "var(--font-mono)" }}>live document · embedded</div>
          </div>
        ) : null}

        {/* tier 3 — extraction facsimile (real fields from the feed) */}
        {tier === "facsimile" ? (
          <dl style={{ margin: 0, padding: "10px 12px", display: "flex", flexDirection: "column", gap: 6 }}>
            {fields.map((f, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", gap: 12, borderBottom: "1px solid var(--line-faint)", paddingBottom: 5 }}>
                <dt style={{ fontSize: 12, color: "var(--ink-muted)" }}>{f.label}</dt>
                <dd style={{ margin: 0, fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600, textAlign: "right", color: f.warn ? "var(--ev-gap-fg)" : "var(--ink)" }}>{f.value}</dd>
              </div>
            ))}
          </dl>
        ) : null}

        {/* tier 4 — fallback "on request" pill over a striped scan body */}
        {tier === "fallback" ? (
          <div style={{ height: 96, background: "repeating-linear-gradient(0deg,#ece7db 0,#ece7db 8px,#e2ddd0 8px,#e2ddd0 10px)" }}>
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ background: "var(--surface-card)", border: "1px solid var(--line-2)", padding: "6px 14px", fontSize: 12, color: "var(--ink-muted)" }}>⤓ {action}</div>
            </div>
          </div>
        ) : null}

        {/* generic redaction bar when a non-crop tier still marks a gap */}
        {showBar ? (
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, background: "var(--ink)", color: "var(--bone-surface)", fontSize: 10, fontFamily: "var(--font-mono)", letterSpacing: "0.5px", padding: "3px 10px" }}>{redactionLabel}</div>
        ) : null}
      </div>

      {/* a catalogued source not embedded inline still links to its full viewer */}
      {docHref && tier !== "embed" ? (
        <a href={docHref} style={{ display: "block", padding: "7px 10px", borderTop: "1px solid var(--line-hair)", fontSize: 12, color: "var(--forest)", textDecoration: "none", fontWeight: 600 }}>View the source document →</a>
      ) : null}

      {(pages || collection) ? (
        <div style={{ padding: "8px 10px", borderTop: "1px solid var(--line-hair)", fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--ink-faint)" }}>
          {pages}{pages && collection ? " · " : ""}{collection}
        </div>
      ) : null}

      {note ? <div style={{ padding: "7px 10px", borderTop: "1px solid var(--line-faint)", fontSize: 12, color: "var(--ink-muted)", lineHeight: 1.45 }}>{note}</div> : null}
    </div>
  );
}
