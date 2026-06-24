The evidence pill — Watermark's central trust grammar. Place one beside any figure, record, or lead so the reader always knows whether it's sourced, modeled, or unverified. Never present a number without one.

```jsx
<EvidenceTag kind="verified" />
<EvidenceTag kind="inference" />
<EvidenceTag kind="open" brackets />
<EvidenceTag kind="gap" label="land price withheld" />
<EvidenceTag kind="key" />
```

Notes
- Five kinds, each fixed to its palette — never recolor them: `verified` (forest), `inference` (amber), `open` (muted), `gap` (oxblood / scope-gap / redaction), `key` (highlight).
- `brackets` renders `[verified]` — the convention inside record screens and field rows.
- `size="sm"` for inline field rows; default `md` for headers and cards.
