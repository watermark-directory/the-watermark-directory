# Economics — regional cloud-consumer demand & the public benefits extended to it

> A demand-side companion to [HYDROLOGY.md](HYDROLOGY.md). **Unlike HYDROLOGY, this
> document is not `bosc`-generated** — it is hand-assembled analysis over cited
> records. Every figure is tagged: `[verified]` (read from a committed extraction
> or cited record), `[inference]` (a labelled derivation), `[assumption]`, or
> `[open]` (a question, not a finding). The spine is civil/land/hydrology; this is
> the second axis — **what the campus consumes, and what the public gives it** —
> not a claim about who benefits.

## 1. The load — what the campus draws

The one hard, document-anchored magnitude is electrical:

| Quantity | Value | Tag | Source |
|---|---|---|---|
| Backup generation | **114 gensets × 2,750 ekW ≈ 313 MW** | `[verified]` | OEPA Air PTI **P0138965** (`data/extracted/permits/3987141.epa.yaml`) |
| Implied IT load | **~250–300 MW** (midpoint 275) | `[inference]` | N+1 backup≈IT (`bosc.hydrology.cooling`) |
| Cooling towers | **36** | `[verified]` | air permit |
| Consumptive water | **3.1–10 MGD** | `[inference]` | power × WUE / blowdown × cycles ([HYDROLOGY §3](HYDROLOGY.md)) |

A ~275 MW IT load is a **large** consumer — roughly the scale of a mid-size city's
electricity demand, sited on one corridor. The water consequence is already
modeled in HYDROLOGY (net basin loss ≈ 24–77× the Ottawa 7Q10). This page is the
*power and tax-base* half of that consumption story.

## 2. The public benefits extended to it

What the public side committed, from the county's own production `[verified:
data/extracted/legal/prr-mandamus/bosc-prr-production-2026-06-05.response-index.yaml]`:

| Benefit | Term | Tag |
|---|---|---|
| CRA real-property tax abatement | **15-year / 75%** | `[verified]` (Res #548-25) |
| Capital investment (stated) | **~$500M** | `[verified]` |
| Jobs / payroll committed | **~50 jobs / ~$4M payroll by 2030** | `[verified]` |
| Roadwork (publicly-routed) | **$14.2M** via the Port Authority | `[verified]` (OPC + DOSSIER §6) |

## 3. The mismatch — benefit vs. jobs vs. consumption `[inference]`

Set the verified columns side by side:

- **~275 MW IT load** and **3.1–10 MGD** consumptive water, against
- **~50 permanent jobs** and a **15-yr/75%** abatement on a **~$500M** build.

That is on the order of **~5–6 MW per job** and a multi-MGD basin draw for a
headcount a single big-box store would exceed. The economic argument the corpus
*substantiates* is structural: **the public subsidizes load and consumption, not
employment** — and does so for a counterparty it cannot name (the Delaware shell;
see DOSSIER §2). `[inference]` This is the demand-side mirror of HYDROLOGY's
"burden already maxed" finding (the 1996 SSO consent decree, the $11.8M I/I
backlog).

## 4. Why this load exists *here* — demand-side drivers `[open]`

These explain the *incentive* to site authorized cloud capacity in a low-cost,
low-scrutiny jurisdiction. **They are analysis/context, not facts about this
campus**, and carry no document values here (stating a premium percentage would be
fabrication):

- **Authorized-region premium.** Government/regulated cloud (GovCloud-class,
  FedRAMP / DoD IL2–IL6 authorized regions) commands a price premium over
  commercial regions; authorization is costly and capacity-constrained, which
  rewards building dedicated, hardened capacity. `[open]`
- **Tax-base forecasting risk.** Ohio's data-center **sales-tax exemption** (DCTE)
  and the local CRA shift the fiscal bet onto forecasted indirect benefit; whether
  the abated base ever materializes against the consumption is the open question.
  `[open]`
- **Refresh / AI-rack cost curve.** Server refresh cycles and rising rack power
  densities drive recurring capital and escalating MW/water per rack — i.e. the
  consumption side trends *up*, not flat, over the abatement window. `[open]`

> These four bullets are the substance of the relator's committee testimony
> (`data/extracted/legal/select-committee-2026/relator-testimony/`). They live here
> as labelled `[open]` drivers so the repo *carries* the demand-side argument
> without asserting unverified magnitudes.

## 5. Document-backed vs. analysis — the discipline line

| Claim | State |
|---|---|
| ~313 MW backup / ~275 MW IT; 36 cooling towers | `[verified]` / `[inference]` |
| 15-yr/75% CRA; ~$500M; ~50 jobs; $14.2M roadwork | `[verified]` |
| 3.1–10 MGD consumptive; basin-loss multiple | `[inference]` (see HYDROLOGY) |
| ~5–6 MW/job; "subsidizes load not jobs" | `[inference]` |
| GovCloud/IL premium; DCTE forecasting; refresh curve | `[open]` (no corpus document) |

**Nothing on this page promotes a defense-intelligence thesis.** Defense-ecosystem
actors enter only as `[open]` context where the public record already names them
(see COURSE §1.4); the load, the benefits, and the consumption are the findings.
