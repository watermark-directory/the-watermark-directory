StackedBar — a single proportion bar (e.g. evidence status across N records) with an optional legend.

```jsx
<StackedBar segments={[
  {value:196, label:"verified",  kind:"verified"},
  {value:78,  label:"inference", kind:"inference"},
  {value:44,  label:"open",      kind:"open"},
]}/>
```

Notes
- This is the one chart that legitimately wears the evidence palette — pass each segment a `kind`.
- For a non-status proportion, drop `kind` and the forest series fills in; or set explicit `color`s.
