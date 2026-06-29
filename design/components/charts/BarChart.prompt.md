BarChart — categorical columns or ranked rows. Forest carries the data; mark one bar `highlight` to make it load-bearing, or `muted` to show a withheld value.

```jsx
<BarChart data={[
  {label:"'24", value:24},
  {label:"'25", value:31, highlight:true},
]}/>
<BarChart orientation="horizontal" unit="ac" data={[
  {label:"Parcel 2", value:92},
  {label:"Parcel 1", value:5, muted:true},   // price withheld
]}/>
```

Notes
- The evidence palette is never spent here — `highlight` uses `--data-1`, others `--data-3`, `muted` the withheld fill.
- Keep a legend and a source line beside it, exactly like the figures it visualizes.
