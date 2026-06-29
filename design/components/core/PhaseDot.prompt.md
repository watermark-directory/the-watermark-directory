Build-phase marker for a site — a square status dot followed by a mono uppercase label. Used in the directory table, site cards, and chrome live-pill.

```jsx
<PhaseDot phase="live" />
<PhaseDot phase="building" />
<PhaseDot phase="queued" />
<PhaseDot phase="tracking" />
```

Notes
- Four phases map to the neutral ramp: live → forest, building → ink, queued → muted, tracking → faint.
- Always mono, uppercase, 0.5px tracking. The dot is square (no radius), same color as the label.
