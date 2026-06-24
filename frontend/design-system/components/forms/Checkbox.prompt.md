A flat square checkbox with an inline label. Checked fills forest with a bone check; unchecked is a hairline square.

```jsx
<Checkbox checked={credit} onChange={setCredit}>
  Credit me as a contributor (a handle, not your name)
</Checkbox>
```

Notes
- Square, 18px, 2px border. Never rounded.
- `onChange` receives the next boolean. Pair with `TextField`/`RadioCard` to build forms.
