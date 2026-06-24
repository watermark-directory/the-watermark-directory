GaugeBar — one figure against a permitted cap, with the overage past the cap mark in oxblood.

```jsx
<GaugeBar value={3470} cap={3200} unit="af" label="of the annual permit cap"/>
```

Notes
- Fill runs to the cap in amber; anything beyond is oxblood, with an ink cap tick.
- The big percent (value ÷ cap) turns oxblood once the cap is exceeded. Set `showPercent={false}` for the bare bar.
