# BOSC site — permit vs earth-disturbance sequence (4110 N. Cole St.)

A cross-document reconstruction of the **order** in which the data-center site's environmental
authorizations attached relative to the documented start of earth disturbance. Structured
source: [`bosc-site-permit-sequence.yaml`](bosc-site-permit-sequence.yaml). Assembled from
records already in the corpus — the two Ohio EPA isolated-wetland (401) permits, the Allen
County stormwater permit (SW1225), and the Allen SWCD ESC inspection series.

> **Analysis, not legal advice or a determination.** This lays the sequence the produced records
> show. It does **not** assert that any authorization was required, obtained, or untimely. The
> one record that would settle the central question — the NPDES Construction General Permit
> coverage — is **not in the corpus** (the SWCD left it "TBD" and pointed to Ohio EPA); the
> timing question stays open pending that record ([#143](../corpus-completeness-audit.md)).

## The chronology

| Date | Kind | Event | Source |
|---|---|---|---|
| 2025-07-02 | wetland-401 | Level-1 isolated-wetland application received (DSW401251760W) | `permits/3788677` |
| **2025-08-12** | wetland-401 | **Ohio EPA grants** the Level-1 permit (Cat-1, 0.33 ac); fill by 2027-08-12 | `permits/3788677` |
| 2025-08-18 | wetland-401 | Mitigation Purchase Agreement complete | `permits/3796349` |
| 2025-10-30 | governance | Project BOSC preconstruction meeting requested (EMH&T) | ASWCD ex. #1 |
| 2025-11-10 | stormwater | Turner pays the $5,800 stormwater-permit fee (check #637852) | ASWCD p54 |
| **2025-11-14** | stormwater | County approves Mass Grading / **SWPPP** / Drainage Report + issues **SW1225** | ASWCD pp14,52,53 |
| **2025-12-08** | disturbance | **First ESC inspection #177506 — clearing/grubbing + mass grading underway; NPDES = TBD** | ASWCD pp10-12 |
| 2025-12-09 | wetland-401 | **Level-2** wetland application received (DSW401252260W) — *day after clearing* | `permits/3949585` |
| 2025-12-23 | wetland-401 | Ohio EPA declares the Level-2 application **INCOMPLETE** | `permits/3949585` |
| 2026-02-18 | disturbance | ESC #183948 — NPDES = TBD | ASWCD pp1-3 |
| 2026-03-18 | disturbance | ESC #186808 — dewatering ×2, mud tracking; NPDES = TBD | ASWCD pp4-6 |
| 2026-06-05 | disturbance | ESC #194263 — farm-tile + creek-west sediment; NPDES = TBD | ASWCD pp7-9 |
| 2026-06-12 | npdes-cgp | ASWCD produces no coverage number; points relator to Ohio EPA | ASWCD letter, item 1 |

## What the order raises (open questions, not conclusions)

**1. NPDES CGP coverage timing.** Ohio's Construction General Permit requires coverage (an NOI
and an assigned `OHC…` number) *before* disturbing ≥1 acre. The records show active
clearing/grubbing + mass grading from **2025-12-08** on a **195-acre** developed footprint —
far above the 1-acre threshold — while every produced inspection lists the Site NPDES Number as
**"TBD,"** through at least 2026-06-05. But the CGP coverage record itself is **not in the
corpus** — a grep finds no `OHC…` number anywhere. "TBD" on the SWCD's forms is not proof that
coverage did not exist (Turner, the assigned CGP permittee, may have held coverage the SWCD
simply didn't record). **Resolving this requires the Ohio EPA coverage record — issue #143.**

**2. Level-2 wetland authorization vs disturbance.** The narrow Category-1 wetlands (0.33 ac)
*were* authorized first (2025-08-12, before disturbance). But the broader **Level-2** fill
application (DSW401252260W) was received **2025-12-09 — the day after** the first inspection
records clearing underway, and Ohio EPA found it **incomplete** on 2025-12-23 (no practicable
on-site alternatives analysis "for the entire site" — a ~358-ac delineation). A wetland-fill
authorization covering the broader site was thus still pending/incomplete as disturbance
proceeded. The corpus does not show its later disposition.

## Gaps to close
- The **NPDES CGP coverage record** (NOI + `OHC…` number + effective date) — Ohio EPA ([#143](../corpus-completeness-audit.md)).
- The **disposition of DSW401252260W** after the 2025-12-23 incompleteness letter.
- The **exact start date** of earth disturbance (records establish "underway by 2025-12-08").

## Cross-refs
- [`bosc-prr-production-2026-06-12-aswcd.response-index.yaml`](bosc-prr-production-2026-06-12-aswcd.response-index.yaml) · [`.analysis.md`](bosc-prr-production-2026-06-12-aswcd.analysis.md) — the ASWCD production (ESC + SW1225)
- [`../../permits/3788677.epa.yaml`](../../permits/3788677.epa.yaml) · [`/3796349`](../../permits/3796349.epa.yaml) · [`/3949585`](../../permits/3949585.epa.yaml) — the three 401 records
- [`../../plans/bosc-site-footprint.yaml`](../../plans/bosc-site-footprint.yaml) — the 195/115-ac disturbance footprint (#149)
- [`../corpus-completeness-audit.md`](../corpus-completeness-audit.md) — standing audit (NPDES gap; #143)
