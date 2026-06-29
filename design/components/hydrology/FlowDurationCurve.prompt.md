FlowDurationCurve — streamflow against the % of the year it's equalled or exceeded (log Y). The signature "how often does it run this low" figure.

```jsx
<FlowDurationCurve
  data={[{exceedance:50,flow:110},{exceedance:90,flow:9},{exceedance:99.5,flow:0.3}]}
  shadeBelow={4.85}
  thresholds={[
    {value:4.85, label:"draw 4.85"},
    {value:0.2,  label:"7Q10 0.2", color:"var(--ev-gap-fg)"},
  ]}/>
```

Notes
- `data` must be sorted by ascending `exceedance` (0–100). Y is log; pass `yMin`/`yMax` to pin it.
- `shadeBelow` shades the dry tail past the exceedance where flow drops under that value (oxblood).
- Thresholds default amber (modeled); use `var(--ev-gap-fg)` for a hard limit. Hover gives the readout.
