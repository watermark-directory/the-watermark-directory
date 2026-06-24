import React from "react";

/**
 * SourceCard — the source-excerpt fallback. Stands in for a document scan with a
 * file header, a striped "scan" body, and a provenance footer. The scan is shown,
 * not hidden — the record never pretends a gap isn't there.
 */
export function SourceCard({ file = "document.pdf", badge = "SCAN", pages, collection, action = "View source on request", style, ...rest }) {
  return (
    <div className="wm-source" style={{ maxWidth: 360, border: "1px solid var(--line-2)", background: "var(--surface-card)", overflow: "hidden", ...style }} {...rest}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px", background: "var(--bone-sunk)", borderBottom: "1px solid var(--line-2)" }}>
        <div style={{ width: 13, height: 16, border: "1.5px solid var(--ink-faint)", flex: "0 0 auto" }} />
        <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--ink-prose)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{file}</div>
        {badge ? <div style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--ev-inference-fg)", background: "var(--ev-inference-bg)", padding: "2px 6px" }}>{badge}</div> : null}
      </div>
      <div style={{ position: "relative", height: 96, background: "repeating-linear-gradient(0deg,#ece7db 0,#ece7db 8px,#e2ddd0 8px,#e2ddd0 10px)" }}>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ background: "var(--surface-card)", border: "1px solid var(--line-2)", padding: "6px 14px", fontSize: 12, color: "var(--ink-muted)" }}>⤓ {action}</div>
        </div>
      </div>
      {(pages || collection) ? (
        <div style={{ padding: "8px 10px", borderTop: "1px solid var(--line-hair)", fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--ink-faint)" }}>
          {pages}{pages && collection ? " · " : ""}{collection}
        </div>
      ) : null}
    </div>
  );
}
