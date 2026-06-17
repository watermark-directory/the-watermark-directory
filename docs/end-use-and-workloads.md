# End use & workloads — what the facility is for

> A `#233` extension narrative. Like [HYDROLOGY.md](HYDROLOGY.md) and
> [ECONOMICS.md](ECONOMICS.md) this is hand-assembled analysis over cited records,
> and like the guided walk it ends at the open question rather than closing it.
> Every statement carries its register: `[verified]` (read from a cited record),
> `[inference]` (a labeled reading of it), `[open]` (a question the record does not
> answer), `[reference]` (an outside-published spec). The customer question is
> **settled** — the developer is Google ([DOSSIER.md](DOSSIER.md) §1; corrected to
> `[verified]` in the walk). This is the question one layer downstream: not *who
> builds it*, but *what it is for, and who can use it.*

A data center is real infrastructure, and the people building one are entitled to
the presumption that they are doing ordinary economic-development work on the
information they have. The campus on Cole Street will be a genuine facility doing
genuine computing. The question this report asks is narrow and fair: the public is
being asked to abate a building and route public roadwork to it, and the size of
that public benefit turns on *what kind* of data center it is — a thing the record,
so far, does not say.

The Ohio Select Committee on Data Centers spent late May and early June of 2026
taking testimony from the industry itself. That record is the gift here: it draws
the distinctions cleanly, in the operators' own words, so we don't have to.

———

## "data center" names three different things

Across the 2026-06-04 hearings the witnesses span three businesses that share a
name and almost nothing else `[verified:
data/extracted/legal/select-committee-2026/select-committee-2026.hearing-index.yaml]`:

- **Bitcoin mining.** MARA Holdings — $397M in Ohio, behind-the-meter, curtailed
  770+ MW in the January storm — volunteered the distinction itself: *"we don't
  have customers in Bitcoin."* A mine is its own customer.
- **Hyperscale.** Google, Meta, AWS, Microsoft — the owner runs the compute on its
  own account. The company you can name is the company using the machines.
- **Colocation.** QTS, Vantage — a landlord. The operator builds and powers the
  hall; its *tenants* own the compute and decide what runs.

The three answer the public's two plain questions — *who benefits* and *who can use
it* — in completely different ways. The abatement math, the job math, and the
national-security question all change depending on which one a given campus is. So
the category is not a technicality; it is the first fact you need, and it is the
fact the Lima record withholds.

———

## who owns the compute — the opacity, on the record

In colocation the beneficial-ownership question the walk's "Who is actually building
this?" chapter keeps open about the shells reappears as an operating fact. Asked who ultimately captures
the sales-and-use abatement on its campus, **Vantage could not say** `[verified:
hearing-index.yaml, closing session 2026-06-04-pm2]`:

> "I do not know … passed through … or taken advantage by the tenants themselves."

That is not evasiveness; it is the structure. A colocation landlord genuinely may
not know which of its hyperscale tenants books the benefit. The opacity is built
in — and it means that confirming *Google* as the developer of a campus does not, by
itself, tell you that Google is the entity running, benefiting from, or even
present in the halls once they are built. Hyperscale developers do sometimes lease
capacity to others; the deed and the development agreement fix the builder, not the
tenant list.

For Lima this stays `[open]`: the record names the developer, not the occupant.

———

## federal operations is a named customer segment

The committee record establishes something the general reader may not assume — that
hosting the federal government is not a fringe use but a *named, marketed segment*
of the data-center industry `[verified]`:

- **QTS** lists "federal customers, where we operate secure, compliant facilities
  that support national security" as one of its core segments, alongside hyperscale
  and colocation `[verified:
  data/extracted/legal/select-committee-2026/witness-submissions.digest.yaml;
  docs/legal/proponent-analysis.md]`.
- **AWS**, before the same committee, named **the Department of War and the CIA**
  among 11,000 government customers and described the "shared responsibility model"
  — the customer controls its own region and access `[verified: hearing-index.yaml,
  morning panel 2026-06-04-am]`.

This is the structure the relator (Cory Parent, a cloud engineer for regulated
industries) put to the committee as the dimension no other witness raised: not
*how much* power or water, but **who can even use the facility** `[verified:
relator-testimony/bosc-written-testimony-2026-06-01.md]`.

———

## the enclave — why "who can use it" is a real question

Government cloud is not just commercial cloud with a flag on it. The federal
authorization ladder is a published spec `[reference]`:

- **FedRAMP** governs federal civilian cloud work.
- The **DoD impact levels** sit above it: **IL4/IL5** for sensitive and
  national-security data, **IL6** for classified up to SECRET `[reference: DoD
  Cloud Computing SRG]`.

At the higher rungs the capacity is, by regulation, *not* the flexible shared pool
a commercial abatement forecast assumes: an IL5/IL6 environment is **wholly
dedicated**, U.S.-citizen-staffed, and physically and logically isolated `[reference;
relator-testimony §]`. **Google's own Distributed Cloud air-gapped appliance holds
DoD IL5** and was demonstrated with GDIT at Exercise Mobility Guardian 2025
`[reference: Google Cloud blog; Breaking Defense; GDIT, 2024–25]`. High-authorization
hosting is a realistic end use for a hyperscaler, not a hypothetical.

The consequence is economic, and it is the reason this matters to the public ledger:
a high-authorization enclave's supply chain is federal and sealed. It does **not**
sell spare capacity to the open market, and it does not seed the local technology
cluster that an incentive is sold as buying. Whether the campus *anchors a regional
tech economy or remains a sealed island* is the difference the workload class
decides `[inference: relator-testimony §; the spec is reference, the application to
Lima is open]`.

———

## what the record does not say

Set the confirmed facts side by side. The developer is Google `[verified]`. The
campus is real and large `[verified]`. The industry's own testimony establishes the
taxonomy — Bitcoin, hyperscale, colocation — and a named federal segment with a
dedicated-enclave structure above it `[verified]`/`[reference]`. Every one of those
is register-one.

The question those facts cannot answer is the one the public benefit turns on:
**which is the Lima campus, and who can use it?** Hyperscale running Google's own
workloads; a colocation hall whose tenants are unnamed; or a high-authorization
GovCloud/DoD enclave whose capacity never touches the local economy at all. The
record does not say, and two of its silences are pointed rather than neutral:

- **Google's own legislative testimony omits Lima.** Liz Schwab's 2026-06-04
  submission lists Google's Ohio footprint as New Albany, Columbus, and Lancaster —
  a ">$20 billion" total — and does **not** name Lima or Allen County, while
  testifying to this very committee about Ohio data centers `[verified: the
  omission — witness-submissions.digest.yaml]`. The omission is documented; what it
  *means* is `[inference]`, not a finding.
- **The defense channel returned "no records."** The public-records request for
  County ⇄ DoD / General Dynamics Land Systems communications came back empty
  `[verified: PRR item 2]`. An absence is not evidence of a thing; it is the
  continued absence of an answer.

That is where this report stops. The defense nexus — GDLS runs the Joint Systems
Manufacturing Center in the same corridor; Google holds DoD IL5; a Google witness
answered the classification question only in indirect language and never named Lima
— is the sharpest facet of the open question, and it is carried as exactly that: a
corridor of `[open]` context, not a finding. Co-location, an indirect answer, and an
absence are not, separately or together, proof of a use the record has not disclosed.

The honest end state is a question the confirmed facts cannot close, and a public
decision being made without the one input that would size it. The abatement is being
scored against a facility whose end use — and whose eligible users — the public is
not permitted to see. The per-job abatement model already carries this as a modeling
profile, not a claim: a GovCloud/defense-hardened build is one of the scenarios that
moves the public cost per job ([ECONOMICS.md](ECONOMICS.md); the Cost chapter's
abatement band). Which profile is real is `[open]` — and the mechanism that could
close it is the records-disclosure fight, not this page.

———

## sources

- Ohio Select Committee on Data Centers, hearing index and cross-cutting read —
  `data/extracted/legal/select-committee-2026/select-committee-2026.hearing-index.yaml`
- Witness written-submission digest (16 submissions) —
  `data/extracted/legal/select-committee-2026/witness-submissions.digest.yaml`
- Relator written testimony, 2026-06-01 (the GovCloud / impact-level argument) —
  `data/extracted/legal/select-committee-2026/relator-testimony/bosc-written-testimony-2026-06-01.md`
- Proponent analysis (QTS federal-segment candor) —
  [legal/proponent-analysis.md](legal/proponent-analysis.md)
- The developer-identity and public-benefit spine — [DOSSIER.md](DOSSIER.md),
  [ECONOMICS.md](ECONOMICS.md)
