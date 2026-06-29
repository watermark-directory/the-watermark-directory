The record's chronology — a single ink spine with square evidence-colored nodes, forest year-diamonds, and an event card at each beat. Year dividers insert automatically when the year changes.

```jsx
<Timeline events={[
  { year: "2025", date: "2025-08-13", kind: "deed", title: "Seven-parcel deed recorded",
    summary: "Brenneman Trusts → Bistrozzi LLC, 340.2 ac. Six DTE-100 prices left blank.",
    evidence: "verified", connect: [{ kind: "entity", label: "Bistrozzi LLC", href: "/wiki/entities/bistrozzi-llc" }],
    seenInCh: 1, seenInHref: "/.../stories/project-bosc/who" },
  { year: "2026", date: "2026 · pending", kind: "records request", title: "Cost-benefit analysis withheld",
    summary: "PRR item 4 refused; mandamus thread open.", evidence: "open" },
]} />
```

Notes
- Each node's color is its evidence standing; the spine is a 2px `--line-2`.
- Keep events in chronological order — the component groups them under year markers itself.
- An event tied to a story chapter carries an **"↩ story Ch.N" badge** (`seenInCh` + `seenInHref`) that backlinks into the chapter; connect chips carry real `href`s.
- Use on a site's chronology view and in record teardowns.
