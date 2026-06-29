Icon — the single stroke-based family. One weight, 24px grid, `currentColor` so each glyph inherits the ink, forest, or evidence color of its row. Inline these rather than reaching for a third-party set; if you must substitute, Lucide is the closest match.

```jsx
<Icon name="search" />
<Icon name="document" size={20} />
<Icon name="verify-link" color="var(--forest)" />
<Icon name="verified" />          // semantic — keeps its evidence color
<Icon name="scope-gap" />         // semantic — oxblood
<Icon name="repo" size={18} />    // the lone filled, foreign mark (octocat)
```

Notes
- Color comes from the parent by default (`currentColor`). Set a row's `color` and the icon follows.
- **Semantic icons are fixed to the evidence palette** — `verified` (forest), `inference` (amber), `open` (muted), `scope-gap` (oxblood), `key-figure` (highlight). Pass `inherit` only if you deliberately want them to take the ink color.
- `repo` and `redaction` are the two filled glyphs; everything else is a 1.7 stroke with round caps.
- Import the name list with `ICON_NAMES` when you need to iterate (pickers, legends).
