The source-excerpt fallback — stands in for a document scan with a file header, a striped scan body, and a provenance footer. Use wherever the underlying source isn't inline-renderable; the gap is shown, never hidden.

```jsx
<SourceCard
  file="PRR-01-bundle.pdf"
  badge="SCAN"
  pages="pp. 317–328"
  collection="Public Records Request 01"
/>
```

Notes
- The striped body reads as a document standing in for itself; the centered chip is the retrieval action.
- The "fingerprint" icon (1.5px outline rectangle) is the standard document marker — pair it with mono provenance text.
