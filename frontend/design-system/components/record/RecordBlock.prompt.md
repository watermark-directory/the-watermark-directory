The canonical record card — a single documented fact shown at reference density: header with evidence pill, an optional "seen in the story" backlink, a flat fields grid, structured nested-field trees, flagged gaps, a provenance footer (structured `verify` + `correctHref`), and "where it connects" chips. `compact` collapses it to a list row.

```jsx
<RecordBlock record={{
  kind: "Record · deed",
  title: "Limited Warranty Deed",
  recordId: "instr. 202508130008300",
  evidence: "verified",
  seenIn: { href: "/.../stories/project-bosc/who", ch: 1, label: "Who is actually building this?" },
  fields: [
    { label: "Grantor", value: "Brenneman Family Trusts" },
    { label: "Other DTE-100 prices", value: "~ blank", warn: true, tag: "open" },
  ],
  nested: [
    { label: "parcels_conveyed", value: [
      { parcel: "0100-03-002.000", acres: 5.0, price: "$600,000" },
      { parcel: "0100-03-003.000", acres: "~120.4", price: "~ blank" },
    ] },
  ],
  warnings: ["6 of 7 conveyance prices left blank on the DTE-100."],
  source: { file: "AUD_DTE100_…08300.pdf", pages: "instrument …08300", collection: "Allen County Recorder" },
  verify: { href: "/site/records/recorder/0008300", label: "Open instrument · Recorder" },
  correctHref: "/submit?ref=recorder-0008300",
  connect: [{ kind: "entity", label: "Bistrozzi LLC", href: "/wiki/entities/bistrozzi-llc" }],
}} />

<RecordBlock density="compact" record={{ title: "Rezoning application", recordId: "PZ-2024-118", evidence: "verified", headlineValue: "$600,000", seenIn: { href: "#", ch: 2, label: "How it was assembled" }, href: "/site/records/planning/pz-2024-118" }} />
```

Notes
- The forest left-rail (4px full / 3px compact) is the record signature.
- Flat field values are mono; `warn` fields go oxblood. **`nested`** fields render as a recursive key/value tree (objects → tree, arrays → list); a leaf carrying the `~` approximate marker renders oxblood. The provenance footer always carries the source file, pages, and collection.
- `seenIn` backlinks to the story chapter that tears this record down ("↩ seen in the story" on full, "↩ story Ch.N" badge on compact). `verify` is a `{href,label}` link; `correctHref` opens the submit form pre-referenced to this record; connect chips carry real `href`s.
- Use `full` on a record screen; `compact` in record-group lists and search results.
