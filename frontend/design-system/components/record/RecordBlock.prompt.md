The canonical record card — a single documented fact shown at reference density: header with evidence pill, a fields grid, flagged gaps, a provenance footer, and "where it connects" chips. `compact` collapses it to a list row.

```jsx
<RecordBlock record={{
  kind: "Record · deed",
  title: "Limited Warranty Deed",
  recordId: "instr. 202508130008300",
  evidence: "verified",
  fields: [
    { label: "Grantor", value: "Brenneman Family Trusts" },
    { label: "Grantee", value: "Bistrozzi LLC" },
    { label: "Other DTE-100 prices", value: "~ blank", warn: true, tag: "open" },
  ],
  warnings: ["6 of 7 conveyance prices left blank on the DTE-100."],
  source: { file: "AUD_DTE100_…08300.pdf", pages: "instrument …08300", collection: "Allen County Recorder" },
  verify: "Open instrument · Recorder",
  connect: [{ kind: "entity", label: "Bistrozzi LLC" }, { kind: "concept", label: "[[common-control]]" }],
}} />

<RecordBlock density="compact" record={{ title: "Rezoning application", recordId: "PZ-2024-118", evidence: "verified", headlineValue: "$600,000" }} />
```

Notes
- The forest left-rail (4px full / 3px compact) is the record signature.
- Field values are mono; `warn` fields go oxblood. The provenance footer always carries the source file, pages, and collection.
- Use `full` on a record screen; `compact` in record-group lists and search results.
