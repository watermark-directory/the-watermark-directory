A "library door" — a typed link chip out to a connected entity, concept, timeline event, place, or map layer. Used in a record's "Where it connects" row and inline in prose.

```jsx
<ConnectChip kind="entity">Tetra Tech</ConnectChip>
<ConnectChip kind="concept">[[7Q10]]</ConnectChip>
<ConnectChip kind="timeline">2025-08-13 · recorded</ConnectChip>
<ConnectChip kind="map">roundabout layer</ConnectChip>
```

Notes
- The `kind` renders as a tiny mono uppercase prefix; the children are the link text.
- `tone="forest"` (default) for record connection rows; `tone="neutral"` to recede into denser UI.
- Concepts use the `[[wikilink]]` convention; entities/people use their proper name.
