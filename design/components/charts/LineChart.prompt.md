LineChart — a time series with an optional forest-tint area and an emphasized last point. Pass `lastLabel` for the inline figure at the end.

```jsx
<LineChart lastLabel="340.2 ac"
  refs={[{ value: 340, label: "340-ac site footprint" }]}
  data={[
  {label:"'24", value:300},
  {label:"'25", value:335},
  {label:"'26", value:340.2},
]}/>
```

Notes
- `area` (default on) fills the forest tint under the line; turn it off for a bare trend.
- `refs` draws dashed horizontal threshold lines (a disclosed cap, a design low flow, a target) with a right-aligned label — the value the series is read against.
- Every value is mono; pair with an `[verified]` / `[inference]` note underneath.
