Waterfall — a value drawn down step by step, reading as an equation (intake − returned = consumed).

```jsx
<Waterfall steps={[
  {label:"intake",   value:7.0,  kind:"base"},
  {label:"returned", value:2.15, kind:"down"},
  {label:"consumed", value:4.85, kind:"result"},
]}/>
```

Notes
- `kind`: `base` (full bar from zero), `down`/`up` (a delta floating from the running total), `result` (the net remainder). Tones: base ink, down forest, up/result amber.
- Dashed connectors carry the eye from each bar's top to the next.
