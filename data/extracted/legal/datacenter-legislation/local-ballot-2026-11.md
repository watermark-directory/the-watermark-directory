# Ohio local data-center ballot measures — 2026-11-03

Network-level governance record. The structured peer is
[`local-ballot-2026-11.yaml`](local-ballot-2026-11.yaml); it holds the per-measure detail, the
R.C. 149.43 queue, and the standing limits. This file is the reading of it.

Tags are BOSC evidentiary discipline: `[verified]` = stated in a captured primary record,
`[reference]` = secondary or self-published, `[inference]` = reasoned and labelled, `[open]` =
not established.

## ⚠️ This file holds no `[verified]` claim

Not one certification, part petition, protest record or slip opinion is captured under
`data/documents/`. Every measure below rests on press reporting, the Supreme Court of Ohio's own
*news service* summaries, or a municipality's web notice. The controlling instrument in every
case is a **county board of elections certification**, and none has been obtained.

That is a statement about this record's standing, not a hedge. The route is already established
in this corpus — `data/extracted/van-wert/regulatory-watch.yaml` names "Van Wert County Board of
Elections — R.C. 149.43 for the 2026-07-27 certification and part petitions" — and the YAML
reuses it per county rather than reinventing it. Each measure carries its own `records_route`.

## ⚠️ A ballot measure is not an outcome

Until 2026-11-03 every measure here is a **pending instrument**. Nothing in this record licenses
a claim about what any community decided, and nothing here may move a site's `readiness` —
readiness is domain activation off committed evidence, and a pending question is not a record
domain.

## The count does not reconcile

Reporting is headlined "18 Ohio communities." A full read of the source article and six
syndicated mirrors yields **17 distinguishable communities**. The eighteenth is `[open]`.

Three explanations are plausible and none is adopted: the count may treat one community's
multiple questions as multiple entries (Piqua filed four petitions; Wilmington carries four
referendums), it may include Sidney — whose questions may land on a **special** election rather
than 2026-11-03 — or there is an eighteenth the mirrors do not reproduce. The way to close it is
the Ohio Secretary of State's certified list of local questions and issues, not another pass
through the press. That is pull priority 1.

## The measures

| Community | County | BOSC | Instrument | Threshold | Standing |
|---|---|---|---|---|---|
| **Piqua** | Miami | `troy-piqua` — site, live + selectable | charter §138 | 25 MW | certified (Ord. O-11-26); a 2nd amendment `[open]` |
| **Urbana** | Champaign | `urbana` — site, live + selectable | charter | **7.5 MW** | certified |
| **Defiance** | Defiance | `defiance` — site, queued | charter | 25 MW | certified — 270 valid / 225 required |
| **Oregon** | Lucas | `toledo` — county-adjacent | charter | 25 MW | **unconfirmed** |
| **Trenton** | Butler | `hamilton-middletown` — register entry (Project Mila) | charter | 25 MW | ordered to ballot — 336 / 128 |
| **Pataskala** | Licking | `new-albany` — register entry (Beech Rd) | charter | 25 MW | certified |
| **Granville** | Licking | `new-albany` — county-adjacent | charter | 25 MW | certified |
| **Sunbury** | Delaware | not registered | charter | 25 MW | certified — 351 valid / 174 required |
| **Conneaut** | Ashtabula | not registered | charter | 25 MW | **unconfirmed** |
| **Upper Sandusky** | Wyandot | not registered | charter | 25 MW | **unconfirmed** |
| **Hubbard** | Trumbull | `lordstown` — county-adjacent | initiative | **full ban** | certified by the Auditor 2026-07-16 |
| **Grove City** | Franklin | `columbus` — county-adjacent | charter (Community Consent) | **20 MW** / 50 ac / 500k gpd | certified |
| **Wilmington** | Clinton | `wilmington` — site, queued | **4 referendums** | — | certified; a 5th initiative **refused 4–0** |
| **Ashville** | Pickaway | not registered | referendum on Res. 06-2026 | — | certified 2026-08-24, 4–0 |
| **Sidney** | Shelby | `sidney` — site, live + selectable | 3 petitions | — | **ballot date `[open]`** |
| **2 Adams Co. townships** | Adams | `west-union` — site, queued | township zoning | — | **unconfirmed; which two is `[inference]`** |

All `[reference]` except the Adams County pairing, which is `[inference]`.

## Four measures the premise did not carry

This pass was briefed on fourteen communities. Four of the ones it found are not among them, and
two of the four reach registered BOSC sites.

- **Wilmington (Clinton County)** — the most consequential. `wilmington` is a registered site
  with committed places, power and water work (#1470 / #1469 / #1472). Four referendums against
  city zoning ordinances are on the ballot; a **fifth instrument**, an initiative ordinance
  titled "Regulating Data Centers and Data Center Campuses" that would have established Chapter
  1161 of the zoning code, was **kept off** it by a 4–0 Clinton County BOE vote on
  reconsideration (reported 2026-08-28). Counsel's ground was the **scope of municipal power** —
  the initiative "creates a new private civil cause of action that Wilmington lacks legislative
  authority to enact" — not signatures. Four certified, one refused; do not collapse them. The
  underlying project is a reported ~$4B Amazon Web Services facility sited next to a residential
  subdivision.
- **Grove City (Franklin County)** — the "Community Consent Amendment." It **does not name data
  centers**: it reaches any industrial development at ≥50 acres, >500,000 gpd of water, or ≥20 MW,
  and sends it to a vote of the electorate. Reported reasoning is that a data-center-specific ban
  was avoided on litigation-risk advice. Whether the certified text is *any-of* or *all-of* those
  thresholds is `[open]` and decides the measure's entire reach.
- **Ashville (Pickaway County)** — the only measure attacking a **signed agreement**. The
  referendum would repeal Village Resolution No. 06-2026, which approved terms with EdgeConneX
  for two data centers plus an ~800 MW gas plant on ~195 acres of village property *and*
  suspended a moratorium the council had passed in December 2025.
- **Sidney (Shelby County)** — see below. `sidney` is live + selectable.

## Traps

**The statewide amendment failed; these did not.** The Conserve Ohio initiated constitutional
amendment reached ~70,000 of the 413,488 signatures required by 2026-07-01 and did not qualify;
the signatures were not submitted and remain valid, targeting 2027 (already recorded in the
`west-union` and `troy-piqua` registers, lead `BALLOT-2027`). The nine 25-MW **local charter
amendments mirror it and were organized by the same campaign — and they qualified.** The
statewide failure says nothing about them. "The data-center ban failed" collapses two different
instruments.

**Sidney's adjudicated petition is about recall, not data centers.** *State ex rel. Turner v.
Barhorst*, No. 2026-1088, 2026-Ohio-3439 (2026-09-03), concerns a charter amendment
**establishing a uniform procedure for recalling elected city officials**. The Court held that
R.C. 731.32 — which the City Clerk invoked to reject the 561-signature petition as "facially
invalid" — applies only to initiatives adopting ordinances and to referendums against
ordinances, **not to charter amendments**. The petition is *motivated* by the data-center
dispute; its text is recall procedure. The other two of the "trio" are `[open]`, unenumerated in
any source reached. And the ballot date is `[open]`: the decision landed one day before the
2026-09-04 filing deadline with verification not yet done, and reporting says a **special
election** is likely. **Do not list Sidney as a November measure.**

**Urbana is 7.5 MW.** Not 25. The lowest threshold in the file, by a factor of ~3.3 against the
others. Grove City is 20 MW. Hubbard has no threshold because it is a full ban. Normalizing any
of these into "the 25-MW measures" misstates three of them.

**The two Adams County townships are an `[inference]`, and one half is weak.** Reporting names
them only as "two Adams County townships on the Ohio River." The `west-union` register records,
both dated 2026-03-02: **Sprigg Township** (Stuart plant) passing a one-year *voluntary*
moratorium with no land-use force, and **Monroe Township** (27 sq mi, Killen plant) resolving to
establish a **zoning commission**. Monroe is a direct mechanical fit — R.C. 519 requires an
electoral vote to adopt township zoning. Sprigg's voluntary moratorium is not that mechanism at
all, so Sprigg is the weaker half of the pairing. **Do not name either without the Adams County
Board of Elections.**

**Trenton and Pataskala are register entries, not sites.** Trenton is the Prologis "Project Mila"
entry inside `hamilton-middletown`; Pataskala sits in `new-albany`'s Licking corridor. Any
extraction from these must be shelved under its owning collection and site subdirectory — an
artifact filed flat lands in Lima's reference record (`_eponymous_prefixes`, #1405).

**Adjacency is not identity.** Hubbard is Trumbull County and so is `lordstown`, a `tracking`
site with its own moratorium history. Grove City is Franklin County, which is `columbus`'s.
Oregon is Lucas County, which is `toledo`'s. Upper Sandusky is Wyandot, next to `tiffin`'s
Seneca. A measure in a registered site's *county* is not a measure at that site, and the table
says `county-adjacent` where that is all it is.

**Court News Ohio is the Court's news service, not its reporter.** Every litigation block is
`[reference]` for that reason and upgrades only on the captured slip opinion. Four are queued:
2026-Ohio-3035 (Ashville), 2026-Ohio-3439 (Sidney), the Trenton decision of 2026-09-01
(No. 2026-1035, slip citation not obtained), and whatever the pending signature-requirement case
Piqua's law director referenced turns out to be.

## Dated negatives

Three measures are recorded **unconfirmed**, not confirmed-with-missing-numbers. As of
**2026-09-16**, each appears only as a member of the source article's list of nine; searches on
the community name against "charter amendment", "certified", "board of elections" and the county
returned no local coverage and no certification detail.

- **Conneaut** — Ashtabula County Board of Elections not queried.
- **Upper Sandusky** — Wyandot County Board of Elections not queried.
- **Oregon** — reporting reached "gathered the required signatures" (2026-07) and stopped; Lucas
  County Board of Elections not queried.

An undocumented route is no route. These three, the Adams County pairing, and the count gap are
all answered by the same priority-1 pull.

## Why this could not wait for the election

The certification record is what makes the **question** auditable — signature counts, the
sufficiency determination, the part petitions, any protest. After 2026-11-03 that record still
exists but stops being the live thread, and the analysis shifts to outcomes. Three sites are
publishing now: `troy-piqua` and `urbana` are live + selectable and `sidney` is live +
selectable, and each publishes a governance picture that until this record omitted a pending
measure against its own facility. `wilmington` is queued and omits four.

## Next check

Weekly through 2026-11-03 — the election is a hard dated trigger, not an interval, and the
pre-election window is when the certification record is live and cheapest to obtain. Dated
triggers, cadence rationale and the full pull queue are in the YAML's `next_check` block.
