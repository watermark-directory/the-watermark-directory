BulletBar — a measure against a limit. The oxblood `marker` is the available threshold; the comparison is the whole story.

```jsx
<BulletBar max={5} unit="cfs" rows={[
  {label:"Design low flow · 7Q10", evidence:"verified", evidenceNote:"USGS", value:0.2},
  {label:"Cooling draw · modeled", evidence:"inference", evidenceNote:"permit calc", value:4.85, color:"var(--ev-inference-fg)", marker:0.2},
]}/>
```

Notes
- `max` sets one shared scale across every row so the bars are comparable.
- `marker` draws the oxblood limit rule; keep the takeaway line ("~24× larger") beside it.
- `evidence` + `evidenceNote` give a row a typed evidence register (`[verified] · USGS`), colored from the evidence palette — preferred over the raw `note` / `noteColor`.
