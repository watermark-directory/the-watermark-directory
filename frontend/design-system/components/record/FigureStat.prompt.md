A load-bearing number shown with its evidence standing and provenance. The unit of every figure in the record — never show a bare number.

```jsx
<FigureStat
  label="Cooling draw ÷ 7Q10"
  value="24.3×"
  unit="design low flow"
  evidence="inference"
  basis="modeled"
  sub="4.85 cfs consumptive ÷ 0.2 cfs"
  source="USGS 04187100 · OEPA"
/>

<FigureStat size="sm" label="Program total" value="$14.2M" evidence="verified" />
```

Notes
- The value is ALWAYS IBM Plex Mono. `warn` turns it oxblood — for figures the record was made thin to hide.
- `evidence` shows the bracketed pill; `basis` (grounded/modeled) is a second qualifier for derived figures.
- `lg` fills its grid cell height (use in dashboards); `sm` is a compact inline stat for profile strips.
