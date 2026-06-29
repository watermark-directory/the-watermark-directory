The flat, square-cornered action button — use for every call to action; `solid` (ink) is primary, `forest` for the affirmative/live action, `ghost` for secondary, `link` for inline navigation.

```jsx
<Button variant="solid" iconRight={<Arrow />}>Explore the directory</Button>
<Button variant="forest" href="/walk">Start the walk</Button>
<Button variant="ghost">Browse archive</Button>
<Button variant="link" iconRight="↗">Verify link</Button>
```

Notes
- No border-radius, no shadow — ever. The button is a rectangle.
- `solid` fills with `--ink`, `forest` with `--forest`; `ghost` is a 1.5px ink outline.
- Pair a trailing arrow (→) with navigation and a ↗ with "open the source" verify links.
- Sizes: `sm` / `md` (default) / `lg`. Disabled drops opacity to 0.45.
