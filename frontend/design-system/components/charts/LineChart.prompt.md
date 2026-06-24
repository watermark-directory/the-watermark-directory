LineChart — a time series with an optional forest-tint area and an emphasized last point. Pass `lastLabel` for the inline figure at the end.

```jsx
<LineChart lastLabel="340.2 ac" data={[
  {label:"'24", value:300},
  {label:"'25", value:335},
  {label:"'26", value:340.2},
]}/>
```

Notes
- `area` (default on) fills the forest tint under the line; turn it off for a bare trend.
- Every value is mono; pair with an `[verified]` / `[inference]` note underneath.
