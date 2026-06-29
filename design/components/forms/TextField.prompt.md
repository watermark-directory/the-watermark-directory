A flat, square text input or textarea with a mono uppercase micro-label, hairline border, bone fill, and a forest focus ring. The base form control.

```jsx
<TextField label="2 · What's the claim or correction?" multiline
  placeholder='e.g. "Parcel 4’s price wasn’t blank — the auditor lists it at $1.95M."'
  hint="Be specific. One checkable claim per lead works best." />

<TextField label="4 · Your contact" optional="if you're open to follow-up"
  placeholder="email or Signal…" />
```

Notes
- Square corners, no shadow; focus shows the forest ring (`--ring-focus`), never a glow.
- Pass `multiline` for textareas; `icon` for a leading glyph (e.g. a link icon on a URL field).
