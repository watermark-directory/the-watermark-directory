# BOSC PRR — Allen County production batch 1 (2026-06-05)

**Cover letter:** Brittany N. Woods, Clerk of Board, dated **June 5, 2026**. Structured index: [`bosc-prr-production-2026-06-05.response-index.yaml`](bosc-prr-production-2026-06-05.response-index.yaml). Source binaries belong at `data/documents/legal/prr-production-2026-06-05/` (5 PDFs).

> Analysis, not legal advice. Figures transcribed from the produced PDFs; verify against the originals before quoting in a filing.

## What it is

The **first of multiple rolling responses** ("we will continue to provide responses… every Friday"), answering the 19-item request item by item. Per the relator's **June 3, 2026** email, anything not listed was treated as withdrawn — which finally pins the request universe the memo flagged as ambiguous ([mandamus-analysis.md](../../../docs/legal/mandamus-analysis.md) §I.6). The county reserves the right to deny/redact later under R.C. 149.43 and 9.66 and states nothing is waived.

This is the production the unfiled mandamus draft extracted as leverage (memo §I.5) — now documented end to end. **The writ itself is now likely moot under *Henderson*, but the statutory-damages + costs claim for the ~7-week pre-production delay (Apr 14 → Jun 5) remains live, and the $1,000 cap was already reached.**

## Item-by-item

| # | Cat | Ask (short) | Status | Note |
|---|-----|-------------|--------|------|
| 1 | A | NDAs / confidentiality instruments | **Produced** | Mutual NDA, Bistrozzi LLC ↔ County |
| 2 | A | DoD / General Dynamics comms | **No records** | County narrows scope, asks for a date range |
| 3 | A | CRA / abatement + school notices | **Produced** | CRA Agreement + Elida & Apollo notices |
| 4 | A | Cost-benefit / ROI analysis | **Withheld — pending §9.66 review** | "compliance with R.C. 149.43 and R.C. 9.66" |
| 5–15 | B | Wastewater RFP / permits / Shawnee II / forcemain | **Deferred** | Punted to Sanitary Engineering Dept. |
| 16 | C | Website CMS audit logs | **No records** | "Commissioners do not manage the county website" |
| 17 | C | Internal comms re website changes | **No records** | — |
| 18 | D | Records indexed to 4110 N. Cole St. | **No records** | Partial ("categories fulfilled") |
| 19 | D | EMH&T comms | **No records** | Will supplement from Sanitary Eng. |

## The three things that matter

**1. The NDA is real, and it is early.** Item 1 produced the Mutual NDA between **Bistrozzi LLC** and the Allen County Commissioners — Resolution **#417-25 (May 27, 2025)**, executed by **Scott J. Ziance of Vorys** for Bistrozzi on **July 1, 2025**. This is the NDA-by-default mechanism (memo §III) confirmed by primary source, and it is **pre-March-20-2026**, so the §1.48 temporal wedge is why the county could hand it over.

**2. Item 4 is §9.66(D) invoked in the wild — on the weakest possible category.** The only outright confidentiality hold is the **cost-benefit / ROI analysis**, "being reviewed by legal counsel for compliance with R.C. 149.43 **and R.C. 9.66**." That is the county's **own work product** — exactly the category the memo argues is the worst fit for a §9.66(D) "submitted… from an applicant" exemption (§II categorical wedge) — and the records are 2025-dated, so the **§1.48 temporal wedge applies too**. This is the record to press, and the proportionate demand is a **record-by-record withholding log** (memo §II), not a blanket fight.

**3. Item 16 confirms the records-custody theory in the county's own words.** Asked for the website CMS audit logs, the county says **"the Commissioners do not manage the county website and therefore do not have access… no records to provide."** That is the precise point of the [web-vendor audit](allen-county-web-vendor-audit.md): the county's WordPress and its edit logs are held by the **third-party host** (AhelioTech, GoDaddy-managed WordPress), with CorpComm Group as the dissolved developer-of-record. A §149.43 request for CMS logs implicates the **third-party processor** — and the county has now admitted it does not hold them. (Note the tension: the same letter cites `commissioners.allencountyohio.com` agendas/minutes/legal-notices as a records source while disclaiming that it manages the site.)

*But "no records" overstates it — the records exist.* The Sanitary Engineering pages run on WordPress, which timestamps every edit and stores full revision history. The site's **own public REST API and XML sitemap** publish per-page `modified` dates, and the `/wp-json/wp/v2/pages/<id>/revisions` endpoint returns **HTTP 401 (gated, not 404)** — the version history exists, behind a login. Several Sanitary pages were **modified inside the requested 2025-01-01 window**, including the **Shawnee II project page (2025-02-03)** and the Sanitary **Projects index (2026-06-05 — the production-letter date)**. So the accurate framing is *custody*, not *existence*: the edit history is maintained by the county's own CMS and held by its host. Profiles + tables: [allen-county-level-sites.md](allen-county-level-sites.md); data in the [response index](bosc-prr-production-2026-06-05.response-index.yaml) under `sanitary_pages_edit_history`.

## One correction to the corpus

The memo's timeline lists **"Bistrozzi Addition LLC," registered April 6, 2026.** This production is with a **different entity — "Bistrozzi LLC"** (Delaware; Vorys/Ziance) — which was already executing an NDA (May 2025) and a 75% CRA abatement (July 2025). So:

- There are **two distinct Bistrozzi entities**, and
- the **deal was locked in mid-2025 — ~9 months before the public Google confirmation (Mar 16, 2026)** and before "Bistrozzi Addition LLC" was even registered.

That materially predates the opacity timeline (§III/§IV) and strengthens the "code-named shells, deal-before-disclosure" narrative. The memo should distinguish the two entities.

*Precision note:* the CRA's §19 "R.C. 9.66 Covenants" is the **pre-existing** clawback/false-statement covenant, **not** the new **§9.66(D)** confidentiality provision (HB 184). Only Item 4's response invokes the (D) shield — keep them distinct in any filing.

## Primary-source corroboration (Commissioners' own minutes)

Every resolution this production relies on also appears in the Board's **published meeting record**
([`data/extracted/commissioners/minutes/`](../commissioners/minutes/README.md) — 634 meetings scraped
from `commissioners.allencountyohio.com`), with the dates matching exactly: **#417-25** NDA (`M052725.pdf:3`),
**#304-25** CRA created (`M041725.pdf:1,5`), **#494-25** school notice (`M062425.pdf:9`), **#548-25** CRA
(`M071025.pdf:4`). Two things follow. First, if a later Friday batch contests a date or resolution number,
the county's own minutes are the check. Second — and sharper — the **deferred Category-B wastewater
resolutions are themselves in the Commissioners' minutes**: **#113-26** and **#136-26** (MS Consultants
forcemain feasibility) appear at `M021926.pdf:3` / `M022626.pdf:3`. The county punted items 5–15 as "better
suited for the Sanitary Engineer," but the *legislative acts* authorizing that work are Commissioners'
records, already public. The deferral may be fine as to engineering files; it is weak as to the resolutions.

There is also a tidy loop on **item 16**: this entire corpus is the public output of `commissioners.allencountyohio.com` — the CorpComm-built site the county simultaneously disclaims managing. The minutes exist and are citable; the *CMS audit trail behind them* is what sits with the third-party vendor.

## New timeline dates (for §IV)

`2025-02-04` Conditional Use Permit · `2025-04-17` Res #304-25 (CRA created) · `2025-05-20` Elida BOE Res #5-25-2 · **`2025-05-27` Res #417-25 (NDA)** · `2025-06-02` ODOD assigns CRA #003-99003-396 · `2025-06-24` Res #494-25 (school notice) · `2025-06-25` AEDG notices to Elida + Apollo · **`2025-07-01` NDA executed (Ziance)** · **`2025-07-10` Res #548-25 (CRA entered)** · `2025-08-26` CRA executed · `2026-06-03` relator narrowing email · **`2026-06-05` production batch 1**.
