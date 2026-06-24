A numbered square pin for annotating document scans and stepping through the guided walk. Forest pins are reads/steps; oxblood pins flag a scope gap or redaction.

```jsx
<AnnotationPin n={1} />
<AnnotationPin n={2} tone="forest" active />
<AnnotationPin n={3} tone="oxblood" />
```

Notes
- Square, mono numeral, bone text knocked out of the fill.
- `active` adds the forest-line outline ring (the pin currently in view).
- Size scales the numeral automatically; default 28px.
