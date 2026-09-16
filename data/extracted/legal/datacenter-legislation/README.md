# Data-center legislation — reviewed reads

Reviewed reads of Ohio legislation directed at data centers and their associated power
generation. Source bills live under
[`data/documents/legal/datacenter-legislation/`](../../../documents/legal/datacenter-legislation/README.md).

## Contents

| Path | What |
|---|---|
| `hb983-3744.digest.yaml` | Provision-by-provision structured read of **H.B. 983 (136th G.A., As Introduced)** — the new R.C. Chapter 3744 (citizen vote, air/water discharge standards for cooling, existing- vs voter-approved-facility duties, water-supply liability, enforcement ladder, grid-independence, revolving door, tax-incentive ban), the R.C. 9.66(D)(2) confidentiality carve-out, and a relevance-to-the-corpus synthesis mapping each provision to the network's water, cooling, discharge, grid, subsidy, and public-records work. |
| `hb983-3744.analysis.md` | Narrative memo: what the bill creates, the five-mile-radius spine, the open-loop/closed-loop gate, and why it lands on nearly every domain the platform models. |
| `local-ballot-2026-11.md` | Network-level reading of the **local data-center ballot measures certified for the 2026-11-03 general election** — 17 communities against reporting headlined "18", with the reconciliation gap left open. Counties, instrument types (charter amendment / zoning referendum / initiative), thresholds (7.5 / 20 / 25 MW / full ban), certifying bodies, the four measures the brief did not carry, and the traps that collapse them. |
| `local-ballot-2026-11.yaml` | Structured peer of the above: one block per measure with its certifying body, signature counts where obtained, litigation, `records_route`, and the R.C. 149.43 pull queue. |

One source version is ingested under
[`documents/legal/datacenter-legislation/`](../../../documents/legal/datacenter-legislation/README.md):
`hb983_00_IN.pdf` (As Introduced). There is no committee substitute yet, so no
introduced-to-passed diff is tracked.

## The ballot record's standing is different from the bill reads

`local-ballot-2026-11.*` holds **no `[verified]` claim, by construction.** The controlling
instrument for every measure is a **county board of elections certification**, and none is
captured under `data/documents/`. Press, the Supreme Court of Ohio's own *news service*
summaries, and a city's web notice are all `[reference]`. The record carries a `records_route`
per measure and a prioritised R.C. 149.43 queue; the first captured certification converts its
own measure and nothing else.

Two standing limits travel with that file. **A ballot measure is not an outcome** — until
2026-11-03 every measure is a pending instrument and nothing licenses a claim about what a
community decided. And **nothing there may move a site's `readiness`**: readiness is domain
activation off committed evidence, and a pending question is not a record domain.

## Conventions

Provision reads are `[verified]` against the cited section and printed page of the bill
text (printed page N equals PDF page N for this document); the relevance synthesis is
`[inference]`; status and enacted-text questions are `[open]`. This is an as-introduced
bill — **not enacted law**, and possibly never enacted — verify against the enacted
R.C. Chapter 3744 / R.C. 9.66 before relying on any read in a filing. The R.C. 9.66
amendatory strike/underline markup is lost in the plain text layer; cite section and
page against the PDF.
