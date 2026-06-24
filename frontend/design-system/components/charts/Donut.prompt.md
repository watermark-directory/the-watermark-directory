Donut — composition of a whole in forest tints, total set mono in the center, optional legend.

```jsx
<Donut center="318" data={[
  {label:"Emails · FOIA", value:96},
  {label:"Permits & filings", value:78},
  {label:"Deeds & instruments", value:52},
]}/>
```

Notes
- Slices auto-take the forest series; pass `color` per datum only to override.
- `center` overrides the auto-summed total; `centerSub` is the caption beneath it.
