# Ohio Revised Code (ORC) full text

Statutory full text pulled from the Ohio LSC code portal, **codes.ohio.gov**, for
the ORC sections the BOSC corpus cites. Text is **verbatim** from the portal —
nothing is summarized, paraphrased, or fabricated. Regenerate with `bosc orc`
(add `--titles` to also pull the whole titles the cited sections belong to).

## What's here

- `citations.yaml` — every ORC section cited in the corpus (scanned from
  `data/extracted/**` and `docs/**`), resolved to its Title, Chapter, heading, and
  canonical URL. A short list of marker-matched numbers the portal had no section
  for is recorded under `unresolved`.
- `orc.cited.yaml` — the full text of those cited sections (number, heading, Title,
  Chapter, body, amendment history, URL), with a provenance `meta` block.
- `orc.title-<n>.yaml` — *(only after `bosc orc --titles`)* the full text of every
  section in a whole Title. These are large.

## How it's pulled

The portal serves HTML, not JSON. A **section** page carries the text + a
breadcrumb naming its Title/Chapter; a **chapter** page inlines every section
(one fetch per chapter); a **title** page lists its chapters. The connector
(`bosc.hydrology.connectors.orc`) parses these and caches the raw pages under the
git-ignored `data/cache/` so re-runs don't refetch.

## Gaps / caveats

- **"General Provisions"** chapters (1, 9, …) sit under a *named* pseudo-title with
  no number, so their `title` is recorded as `General Provisions` (no number) and
  they are not swept by the numbered-title `--titles` crawl. The cited sections
  themselves are still captured.
- **Statutes change.** Each record carries the section URL and the portal's
  amendment history — verify the current text before quoting it in a filing.
- Citation scanning requires an ORC marker (`R.C.`, `O.R.C.`, `ORC`, `§`,
  `section`, `Ohio Revised Code`) before the number; a bare `12.34` is ignored.
  Marker-matched numbers that aren't real ORC sections are dropped (not invented)
  and listed under `unresolved`.
