The wiki identity card for an entity, person, or place — the head of a `/wiki/[kind]/[slug]` profile. Forest rail + name + alias chips, evidence standing, an optional "seen in the story" backlink, a stat strip, an attributes grid, and a graph-neighborhood relationship row.

```jsx
<ProfileHeader profile={{
  kindLabel: "Entity · shell company",
  name: "Bistrozzi LLC",
  variants: ["Bistrozzi Addition LLC", "DE 7•••214"],
  descriptor: "Delaware LLC; grantee on the seven-parcel deed chain.",
  evidence: "inference",
  graphHref: "/wiki/graph/?focus=bistrozzi-llc",
  seenIn: { href: "/.../stories/project-bosc/who", ch: 1, label: "Who is actually building this?" },
  stats: [
    { label: "Parcels controlled", value: "7", evidence: "verified", sub: "340.2 ac" },
    { label: "Sibling shells", value: "3", evidence: "inference", sub: "shared agent" },
  ],
  attrs: [
    { label: "State of formation", value: "Delaware", tag: "verified" },
    { label: "Ultimate control", value: "Google (AEDG)", tag: "inference" },
  ],
  relLabel: "Graph neighborhood",
  relationships: [
    { kind: "grantor", label: "Brenneman Trusts", href: "/wiki/entities/brenneman-trusts" },
    { kind: "sibling", label: "Tilted Gate LLC", href: "/wiki/entities/tilted-gate-llc" },
  ],
  correctHref: "/submit?ref=bistrozzi-llc",
}} />
```

Notes
- Stat dots and attribute `[tags]` carry the evidence palette — an entity's profile shows exactly how much of it is sourced vs inferred.
- The relationship chips are typed (grantor / sibling / contractor) and carry real `href`s into the graph/profiles.
- `graphHref` opens the entity graph focused on this node; `seenIn` backlinks to the story chapter that tears this entity down ("↩ seen in the story"); `correctHref` opens the submit form pre-referenced to this record.
