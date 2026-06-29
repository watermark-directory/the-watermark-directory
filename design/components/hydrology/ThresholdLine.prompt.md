ThresholdLine — a cumulative or time series measured against a horizontal limit (permit cap, draw). Marks the crossing and shades the overage in oxblood.

```jsx
<ThresholdLine
  data={months.map((m,i)=>({label:m, value:cumulative[i]}))}
  limit={3200} limitLabel="cap" unit="af" area/>
```

Notes
- Auto-finds where the line first crosses `limit`, drops an oxblood dot there, and fills the region above the limit.
- Hover any point for its value and share of the limit. `area` adds the forest fill under the whole line.
