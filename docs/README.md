# docs/

Curated narrative / analysis layer for Project BOSC — the prose that frames and
synthesizes the structured data under [`data/`](../data/). The site generator
(`bosc.site`) mirrors this tree into the published site alongside the extracted
artifacts.

## Top-level notes

| File | What | Generated? |
|---|---|---|
| `COURSE.md` | Research course — what we're investigating and what to build next. | hand-written (living draft) |
| `DOSSIER.md` | Cross-document synthesis of everything deconstructed from the corpus. | hand-written |
| `HYDROLOGY.md` | Tier-0 municipal water-flow findings. | **`bosc`-generated** (`bosc.hydrology`); figures tagged `[verified]`/`[assumption]` |
| `COMPUTE.md` | The facility's compute / AI capacity, derived from disclosed power/water/footprint by three bracketing methods. | **`bosc`-generated** (`bosc.facility`; `bosc compute`); figures tagged `[verified]`/`[reference]`/`[inference]` |
| `ECONOMICS.md` | Demand-side companion to HYDROLOGY — regional cloud-consumer demand & public benefits. | hand-assembled over cited sources |

## Subdirs

- [`legal/`](legal/) — legal analysis memos (mandamus, proponent case).
- [`reference/periplus/`](reference/periplus/) — notes carried over from the Periplus fork.

## Conventions

Note per-file whether content is **`bosc`-generated** or **hand-written** —
generated docs should not be hand-edited (regenerate the source instead), and
hand-written analysis must cite the underlying corpus/source for every factual claim.
Never invent a figure or a source.
