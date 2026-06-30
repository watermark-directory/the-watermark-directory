import React from "react";

/**
 * Watermark Footer — two-band site footer.
 *
 * Band 1 (notice): pre-launch disclosure, the provenance-first chip,
 * and a "Submit a tip or correction" CTA. Hidden when prelaunch=false.
 *
 * Band 2 (nav): left column holds the w. mark + wordmark and the
 * technical manifesto; right side holds nav links in labeled column
 * groups (The investigation · Resources · Site).
 *
 * Background: --bone-sunk throughout. No radius. Flat by doctrine.
 */

function PencilIcon({ size = 13 }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
    </svg>
  );
}

function WMark({ size = 22 }) {
  return (
    <span
      aria-hidden="true"
      style={{
        display:         "inline-flex",
        alignItems:      "flex-end",
        justifyContent:  "center",
        width:           size,
        height:          size,
        background:      "var(--ink)",
        flex:            "0 0 auto",
        paddingBottom:   Math.round(size * 0.1),
      }}
    >
      <span style={{
        fontFamily:    "var(--font-sans)",
        fontWeight:    800,
        fontSize:      Math.round(size * 0.72),
        letterSpacing: "-1px",
        lineHeight:    0.65,
        color:         "var(--bone-surface)",
      }}>
        w<span style={{ color: "var(--forest-bright)" }}>.</span>
      </span>
    </span>
  );
}

const DEFAULT_GROUPS = [
  {
    heading: "The investigation",
    links: [
      { label: "Overview",      href: "#" },
      { label: "Open leads",    href: "#" },
      { label: "The watershed", href: "#" },
      { label: "The economy",   href: "#" },
      { label: "The story",     href: "#" },
      { label: "The record",    href: "#" },
    ],
  },
  {
    heading: "Resources",
    links: [
      { label: "Directory", href: "#" },
      { label: "Research",  href: "#" },
      { label: "Docs",      href: "#" },
      { label: "Wiki",      href: "#" },
    ],
  },
  {
    heading: "Site",
    links: [
      { label: "Connect",     href: "#" },
      { label: "Methodology", href: "#" },
      { label: "About",       href: "#" },
    ],
  },
];

export function Footer({
  prelaunch    = true,
  noticePrefix = "Pre-launch — this site isn't public yet.",
  noticeBody   = "Every figure carries a source; inference is labeled; redactions are shown, not hidden. Nothing here is a verdict.",
  groups       = DEFAULT_GROUPS,
  manifesto    = "static · no trackers · every page reads with JS off",
  submitHref,
  onSubmitTip,
  style,
  ...rest
}) {
  return (
    <footer
      className="wm-footer"
      style={{
        background:  "var(--bone-sunk)",
        borderTop:   "1px solid var(--line-hair)",
        fontFamily:  "var(--font-sans)",
        ...style,
      }}
      {...rest}
    >

      {/* ── Band 1 · notice ─────────────────────────────────────────── */}
      {prelaunch && (
        <div style={{
          display:      "flex",
          alignItems:   "center",
          gap:          20,
          padding:      "16px 44px",
          borderBottom: "1px solid var(--line-2)",
          flexWrap:     "wrap",
        }}>
          <p style={{
            flex:       "1 1 320px",
            margin:     0,
            fontSize:   14,
            lineHeight: 1.55,
            color:      "var(--ink-muted)",
            textWrap:   "pretty",
          }}>
            <strong style={{ color: "var(--ink)", fontWeight: 700 }}>
              {noticePrefix}
            </strong>{" "}
            {noticeBody}
          </p>

          <div style={{ flex: "0 0 auto", display: "flex", alignItems: "center", gap: 10 }}>
            {/* provenance-first chip */}
            <span style={{
              display:       "inline-flex",
              alignItems:    "center",
              gap:           7,
              fontSize:      12,
              fontWeight:    700,
              letterSpacing: "0.2px",
              color:         "var(--forest)",
              background:    "var(--bone-raised)",
              border:        "1.5px solid var(--forest-line)",
              padding:       "7px 13px",
              whiteSpace:    "nowrap",
            }}>
              <span style={{ width: 7, height: 7, background: "var(--forest)", flex: "0 0 auto" }} />
              provenance-first
            </span>

            {/* submit CTA */}
            <a
              href={submitHref || "#"}
              onClick={onSubmitTip}
              style={{
                display:             "inline-flex",
                alignItems:          "center",
                gap:                 8,
                fontSize:            14,
                fontWeight:          700,
                color:               "var(--bone-surface)",
                background:          "var(--forest)",
                padding:             "9px 18px",
                textDecoration:      "underline",
                textDecorationColor: "rgba(255,255,255,0.45)",
                textUnderlineOffset: "3px",
                whiteSpace:          "nowrap",
                cursor:              "pointer",
              }}
            >
              <PencilIcon size={13} />
              Submit a tip or correction
            </a>
          </div>
        </div>
      )}

      {/* ── Band 2 · nav ────────────────────────────────────────────── */}
      <div style={{
        display:               "grid",
        gridTemplateColumns:   "200px 1fr",
        gap:                   "0 52px",
        padding:               "28px 44px",
        alignItems:            "start",
      }}>

        {/* left: wordmark + manifesto */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <WMark size={22} />
            <span style={{
              fontSize:      14,
              fontWeight:    800,
              letterSpacing: "-0.2px",
              color:         "var(--ink)",
            }}>
              Watermark<span style={{ color: "var(--forest-bright)" }}>.</span>
            </span>
          </div>
          <span style={{
            fontFamily:    "var(--font-mono)",
            fontSize:      11,
            color:         "var(--ink-faint)",
            letterSpacing: "0.1px",
            lineHeight:    1.7,
          }}>
            {manifesto.split(" · ").map((part, i, arr) => (
              <React.Fragment key={part}>
                {part}
                {i < arr.length - 1 && (
                  <span style={{ color: "var(--ink-ghost)", padding: "0 3px" }}>·</span>
                )}
              </React.Fragment>
            ))}
          </span>
        </div>

        {/* right: grouped nav columns */}
        <nav
          aria-label="Footer site navigation"
          style={{
            display:  "flex",
            gap:      "0 48px",
            flexWrap: "wrap",
          }}
        >
          {groups.map((group) => (
            <div key={group.heading} style={{
              display:       "flex",
              flexDirection: "column",
              gap:           7,
              minWidth:      100,
            }}>
              {/* group heading */}
              <span style={{
                fontFamily:    "var(--font-mono)",
                fontSize:      10,
                fontWeight:    600,
                letterSpacing: "1.3px",
                textTransform: "uppercase",
                color:         "var(--ink-faint)",
                marginBottom:  3,
              }}>
                {group.heading}
              </span>
              {/* group links */}
              {group.links.map((link) => (
                <a
                  key={link.label}
                  href={link.href || "#"}
                  style={{
                    fontSize:       13.5,
                    color:          "var(--ink-muted)",
                    textDecoration: "none",
                    lineHeight:     1.35,
                    transition:     "color 0.12s",
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.color = "var(--ink)"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.color = "var(--ink-muted)"; }}
                  onFocus={(e) => { e.currentTarget.style.color = "var(--ink)"; }}
                  onBlur={(e) => { e.currentTarget.style.color = "var(--ink-muted)"; }}
                >
                  {link.label}
                </a>
              ))}
            </div>
          ))}
        </nav>

      </div>
    </footer>
  );
}
