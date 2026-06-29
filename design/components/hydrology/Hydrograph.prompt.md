Hydrograph — flow across the year, in three modes that share one √-scaled axis.

```jsx
<Hydrograph mode="area" series={monthly} drawLine={4.85}/>
<Hydrograph mode="bars" series={dryYear} drawLine={4.85}/>      // months below the draw flag oxblood
<Hydrograph mode="envelope" typical={typ} dry={dry}/>           // hoverable band
```

Notes
- `mode="bars"` is the deficit hero — any month under `drawLine` turns oxblood.
- `mode="envelope"` draws the typical (forest) vs dry-year (amber dashed) band; hover shows both.
- √-scaling is on by default so a late-summer trough still reads against the spring freshet.
