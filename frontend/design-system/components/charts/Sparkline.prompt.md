Sparkline — an axis-less trend sized to sit inside a record row or stat strip, next to its current figure.

```jsx
<Sparkline data={[2,3,3,5,4,6,8,7,9,12,10,14]}/>
<Sparkline color="var(--data-3)" data={[4,9,12,20,31,44,60]}/>
```

Notes
- No axes, no labels — just the shape. Put the current figure (mono) right beside it.
- Defaults to forest; use a tint for a secondary series in the same row.
