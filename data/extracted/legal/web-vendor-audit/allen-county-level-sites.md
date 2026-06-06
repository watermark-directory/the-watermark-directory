# Allen County government websites — county-level reference

**Captured 2026-06-05.** A consolidated technical + custody profile of the **county-level** office
sites (constitutional offices, the Board, and the county-adjacent development arm). Companion to the
full 41-entity audit ([`allen-county-web-vendor-audit.md`](allen-county-web-vendor-audit.md)) and the
vendor legal registry ([`allen-county-web-vendor-corporate-records.yaml`](allen-county-web-vendor-corporate-records.yaml)).

> Method: homepage pulled by raw HTTP GET; CMS/theme from `<meta generator>` + theme path; footer
> credit from the rendered footer; **edit-history metadata from the site's own WordPress REST API**
> (`/wp-json/wp/v2/pages?orderby=modified` and `/pages/<id>/revisions`) and XML sitemap. All read-only,
> first-party public endpoints. `modified` dates reflect real edits (staggered, not a bulk stamp);
> treat as strong but not forensic — the authoritative diff is the auth-gated revision history.

## The county web estate at a glance

**Eight of the ten county-level sites are WordPress 6.9.4 on a single GoDaddy hosting account**
(`160.153.0.x` /24), **hosted/managed by AhelioTech** (per the 2023–24 Commissioners minutes), with
**CorpComm Group, Inc. as the original developer** (dissolved 2023-06-05). **The whole estate sits
behind Cloudflare's CDN** (`server: cloudflare` + `cf-ray` on every site) — but the eight offices
expose **GoDaddy Managed-WordPress origin IPs** (`160.153.0.x`) behind it. The Sheriff and Board of
Elections are the exceptions: they resolve to **Cloudflare anycast directly** (origin hidden) and are
**not WordPress** (Sheriff = `alsher` theme; BOE = the Ohio SOS `evolve` statewide template, state-run).

| Office | Domain | Host IP | CMS | Theme | "Developed by CorpComm"? | CMS author (latest) | Revisions API | Latest page edit |
|---|---|---|---|---|:--:|---|:--:|---|
| **Main / Recorder** | `allencountyohio.com` | 160.153.0.4 | WP 6.9.4 | `ALC` | ✅ yes | `wp` (id 5) | 401 (gated) | 2026-06-05 (`projects`) |
| **Commissioners** | `commissioners.allencountyohio.com` | 160.153.0.225 | WP 6.9.4 | `ALC` | ❌ no (© only) | id 4 + `admin` (id 6) | 401 | 2026-06-04 (`legal-notices`) |
| **Auditor** | `allencountyohauditor.com` | 160.153.0.236 | WP 6.9.4 | `thegov` | ❌ no | **`b_mauk` = Brian Mauk** (id 2) | 401 | 2026-06-03 |
| **Engineer** | `allencountyohengineer.com` | 160.153.0.210 | WP 6.9.4 | `ace` | ✅ yes | id 4 | 401 | 2026-06-01 (`engconsultants`) |
| **Treasurer** | `allencountyohtreasurer.com` | 160.153.0.114 | WP 6.9.4 | `citygov` | ❌ no | id 1 | 401 | 2026-05-21 (`about`) |
| **Prosecutor** | `allencountyprosecutor.net` | 160.153.0.178 | WP 6.9.4 | `dt-the7` | ❌ no | id 1 | 401 | 2026-02-11 (`career-opportunities`) |
| **Clerk of Courts** | `clerkofcourts.allencountyohio.com` | 160.153.0.61 | WP 6.9.4 | `twentyseventeenCCG` | ✅ yes | id 3 | 401 | 2026-03-12 (`home`) |
| **Sheriff** | `allencountysheriff.org` | 104.21.47.224 (Cloudflare) | not WP | `alsher` | ❌ no | — | — | — |
| **Board of Elections** | `allen.boe.ohio.gov` | 104.16.11.44 (Cloudflare) | not WP | Ohio SOS `evolve` template | ❌ no | — | — | state-run, not county-procured |
| *county-adjacent →* **AEDG** | `aedg.org` | 141.193.213.x (WP Engine) | WP | `AEDG2021-child` | ✅ yes | — | — | the dev arm steering BOSC |

## What the table shows

1. **One account, one host, one developer-of-record.** The eight WordPress offices share a single
   GoDaddy `/24`, all on WP 6.9.4 — i.e. one managed-hosting account (AhelioTech) over CorpComm's
   builds. This is a centrally-administered estate, not eight independent vendors.
2. **A dead vendor still credited on three sites.** *"Developed by CorpComm Group, Inc."* persists on
   **Main/Recorder, Engineer, and Clerk** — a corporation dissolved **2023-06-05**. The offices that
   dropped the credit (Commissioners, Auditor, Treasurer, Prosecutor) run **off-the-shelf themes**
   (`thegov`, `citygov`, `dt-the7`) rather than CorpComm's bespoke ones (`ALC`, `ace`,
   `twentyseventeenCCG`) — suggesting **post-dissolution rebuilds** on those four.
3. **The county CMS keeps full version history — it is just access-gated.** **Every** county WordPress
   site returns **HTTP 401** (not 404) on `/wp-json/wp/v2/pages/<id>/revisions`: WordPress *is* storing
   who-changed-what-when, behind a login held by the host. The public `modified` timestamps and XML
   `<lastmod>` are the visible edge of that record.
4. **All actively edited.** Latest edits cluster within days/weeks of the 2026-06-05 capture — these
   are live, maintained sites, not abandoned installs.
5. **Edits are published through generic role accounts — with one named exception.** Most offices
   author via numeric/role logins (`wp`, `admin`, ids 1–4) that name no individual. The **Auditor is
   the exception: content is authored under `b_mauk` — "Brian Mauk – Allen County Auditor," the county
   IT Director** — direct evidence of *in-house* edit access. (Confirmed on the Auditor site only.)

## Item-16 centerpiece — Sanitary Engineering edit history exists

PRR **item 16** sought *"the website CMS audit trail / edit history / version-control for the Sanitary
Engineering project pages, 2025-01-01 to date"* and the county answered **"no records… the Commissioners
do not manage the county website."** The Sanitary pages live on `allencountyohio.com` (footer:
*"Site Designed and Developed by CorpComm Group, Inc."*), and the site's own REST API publishes the
very edit-history metadata that was requested — multiple project pages **modified inside the requested
window**:

| Sanitary page | ID | Last modified | In item-16 window (≥ 2025-01-01)? |
|---|---|---|:--:|
| **Shawnee II** *(the data-center sewer project)* | 333 | **2025-02-03** | ✅ |
| Projects (index) | 370 | **2026-06-05** *(production-letter date)* | ✅ |
| Wastewater Collection/Maintenance | 335 | **2026-02-27** | ✅ |
| Reports | 368 | **2026-02-04** | ✅ |
| Employment | 313 | **2025-03-19** | ✅ |
| Sanitary Engineering (dept root) | 275 | 2024-06-07 | — |
| Rules / Regs / Specs | 388 | 2024-02-22 | — |

**The records exist.** WordPress timestamps every edit; the full revision history is stored (the
`/revisions` endpoint is **401-gated, not 404**). "No records" conflates *"we don't hold it"* with
*"it doesn't exist"* — the edit history is maintained by the county's own CMS, in custody of the
**third-party host (AhelioTech / GoDaddy-managed WordPress)** and reachable by whoever holds the shared
`wp` admin login. The `Projects` page's `2026-06-05` `modified` date (the production-letter date) is
notable but **not asserted as causal** without the gated revision diff.

## Caveats

- `modified` dates are WordPress's content-modified field, read from the public REST API/sitemap on
  2026-06-05. Staggered values indicate real edits; a migration *can* touch them, so they are strong
  evidence, not a forensic log. The authoritative who/what/when is the **401-gated revision history**.
- Author **IDs** are exposed; author **display names** are mostly locked (`/wp-json/wp/v2/users` → 401).
  Named authorship is confirmed only where an author archive resolves (`b_mauk` on the Auditor; `admin`
  on the Commissioners; `wp` on Main).
- "Developed by CorpComm" is a first-party footer self-credit. Theme/host inferences rest on
  template/IP/version signatures, not contracts — the authoritative source is the county's
  web-services/hosting agreement (a fair PRR target, and §9.66(D)-non-exempt).

_Cross-refs: [`allen-county-web-vendor-audit.md`](allen-county-web-vendor-audit.md) ·
[`allen-county-web-vendor-corporate-records.yaml`](allen-county-web-vendor-corporate-records.yaml) (three-layer custody model) ·
[`bosc-prr-production-2026-06-05.response-index.yaml`](../prr-mandamus/bosc-prr-production-2026-06-05.response-index.yaml) (item 16)._
