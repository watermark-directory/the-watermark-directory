AquiferSection — the cone of depression in cross-section. The groundwater signature figure.

```jsx
<AquiferSection drawdownFt={42} wells={[{x:0.2, depthFrac:0.4, label:"domestic"}]}/>
```

Notes
- `drawdownFt` drives how deep the cone dips at the pumping well; the oxblood dimension labels it.
- Forest dashed = static (rest) level; amber curve = the drawn-down surface during pumping.
- `wells` places domestic-well casings (muted) at `x` (0–1 across the section), optionally labeled.
