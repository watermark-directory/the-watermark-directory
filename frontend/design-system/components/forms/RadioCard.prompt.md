A selectable option card — used for the "what kind of lead?" picker. A square radio dot, a title, and a one-line description; the selected card goes forest-tinted with a forest border.

```jsx
<RadioCard title="Correction" desc="A figure or fact in the record is wrong." selected onSelect={...} />
<RadioCard title="New source" desc="A document we don't have yet." onSelect={...} />
```

Notes
- Lay them out in a 2-col grid for a 4-option picker.
- Selected state mirrors the brand: forest border + forest tint + forest title. Square dot, never a circle.
