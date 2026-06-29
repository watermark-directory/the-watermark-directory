The record's `① source` viewer — a four-tier preview that shows the real source, with the gap shown and never hidden. The tier is chosen by what's available, in priority order: a committed **scan crop** (with its own redaction overlay) → a **live embed** of a published document → an **extraction facsimile** (key/value from the feed) → a quiet **"view source on request"** fallback.

```jsx
// Tier 1 — committed scan crop with a precise redaction overlay (preferred)
<SourceCard
  file="3987141.epa.pdf" badge="SCAN" pages="p. 4 · Table 1" collection="Ohio EPA eDoc"
  crop={{ src: "/scans/p0138965-genset-table.png", alt: "genset table", redaction: { label: "CBI", x: "62%", y: "38%", w: "30%", h: "12%" } }}
  docHref="/site/documents/permits/3987141"
/>

// Tier 3 — extraction facsimile (no scan/embed available)
<SourceCard
  file="AUD_DTE100_…08300.pdf" badge="PDF" pages="instrument …08300" collection="Allen County Recorder"
  fields={[
    { label: "Grantee", value: "Bistrozzi LLC" },
    { label: "Parcel 7 price", value: "~ blank", warn: true },
  ]}
  docHref="/site/documents/recorder/0008300"
/>

// Tier 4 — fallback
<SourceCard file="PRR-01-bundle.pdf" badge="SCAN" pages="pp. 317–328" collection="Public Records Request 01" />
```

Notes
- **Tier priority is automatic:** `crop` wins, then `embed`, then `fields`, else the fallback pill. A `crop` carries its own `redaction` box; otherwise `redactionLabel` draws a generic bar over the body.
- Only a **published** source embeds inline (`embed`); a catalogued-but-gated source still links to its full viewer via `docHref` ("View the source document →").
- The header `badge` is the source's render class (SCAN / PDF / HTML). The "fingerprint" icon (1.5px outline rectangle) is the standard document marker; pair it with the mono provenance footer (pages · collection).
