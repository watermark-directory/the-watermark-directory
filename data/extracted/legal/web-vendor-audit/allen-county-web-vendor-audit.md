# Who manages the websites of Allen County, Ohio governments — vendor audit

**Captured 2026-06-05.** Original records: [`data/documents/legal/allen-county-web-audit/`](../../../documents/legal/web-vendor-audit/) (41 sites, raw HTML + WHOIS). Structured findings: [`allen-county-web-vendor-audit.yaml`](allen-county-web-vendor-audit.yaml).

> Method: each entity's homepage pulled by raw HTTP GET; the web vendor read from the **footer credit** (`Developed by…`, `Website by…`, `Site by…`), the `<meta name="generator">` CMS tag, **outbound vendor links**, and the WordPress theme path. WHOIS captured per domain. "Credited" = the vendor names itself in-page or is linked; "inferred" = identical county template/version/registrar with no in-page credit; "platform only" = self-service builder/CMS with no human vendor named.

## Headline

**No single private firm runs Allen County government's web presence — but one comes close, and it is not the one a casual look would suggest.** Anne Decker Marketing, often visible on local sites, is explicitly credited on only **two** of the 41 entities captured: **Shawnee Township** and the **Allen Soil & Water Conservation District** (both WordPress 7.0).

The vendor that actually dominates **county government** is **CorpComm Group, Inc.** of Lima — and, most relevant to BOSC, **CorpComm also builds the AEDG site** (the Allen Economic Development Group, the entity steering the Google/BOSC project). So the county's own offices *and* the development arm that brought the data center share one private web vendor:

| Vendor | # entities | Who |
|---|---:|---|
| **CorpComm Group, Inc.** | 8 | County main/Recorder, Engineer, Clerk of Courts, **AEDG** (all credited); Commissioners, Auditor, Treasurer, Prosecutor (inferred — same WP 6.9.4 county template) |
| **NOW Marketing Group** | 3 | Regional Transit Authority (ACRTA), Apollo Career Center, Fairgrounds/Ag Society |
| **Finalsite** (K-12 CMS) | 4 | Allen East, Delphos City, Elida Local, Spencerville Local schools |
| **Anne Decker Marketing** | 2 | **Shawnee Township**, Allen Soil & Water Conservation District |
| **Modo Media** | 2 | Board of Developmental Disabilities, Metropolitan Housing Authority (both Wix) |
| **CivicPlus** (gov CMS) | 2 | **City of Lima**, Lima-Allen County Regional Planning Commission |
| Munibit · Revize · MCG · Edlio · eSchoolView | 1 each | Auglaize Twp (.gov) · Beaverdam · Elida Village · Perry schools · ESC |

*This table counts **developers** (who built/credits the site). It is not the whole custody story: the county sites are **hosted/managed by AhelioTech** and edited in part **in-house** (county IT). See the three-layer model under "Why this matters."*

## Why this matters to the records campaign

Ex. C asks for the **county website CMS audit logs**. "Who manages the site" turns out to have **three answers, not one** — and that strengthens the custody point rather than weakening it:

| Layer | Who | How we know |
|---|---|---|
| **Developer / theme** | **CorpComm Group, Inc.** — *dissolved 2023-06-05* | footer credits + bespoke child themes (`ALC`, `twentyseventeenCCG`, `AEDG2021`) on main/Recorder/Engineer/Clerk/AEDG |
| **Host / managed IT** | **AhelioTech Services, Ltd.** (Powell, OH) | commissioners minutes: *"transition of county website to AhelioTech for hosting"* (`ACC-M102423.pdf:5`, 2023-10-24); recurs 9–12× across the 2024 minutes |
| **In-house admin / author** | **Brian Mauk, county IT Director** | WordPress author `b_mauk` on `allencountyohauditor.com` (*"by Brian Mauk"*); IT Director per Res #447-23 |

So a §149.43 request for CMS audit logs has **named, reachable custodians**: the host of record (AhelioTech) and the in-house user (`b_mauk`) whom the logs would name. Two facts sharpen the contradiction in the county's item-16 answer (*"the Commissioners do not manage the county website… no access"*): **`CorpComm` appears 0 times in 634 meetings while AhelioTech is named repeatedly** (the county knows its host), and **the county's own IT Director is a WordPress author** within the same install cluster. The public output of that install is in the corpus — [`data/extracted/commissioners/minutes/`](../../commissioners/minutes/README.md) — but the **CMS audit trail behind it** is exactly what item 16 says the county doesn't hold. *(Caveat: Mauk's authorship is confirmed on the Auditor site, not yet on `commissioners.allencountyohio.com` specifically.)* Full legal identities + the three-layer model: [`allen-county-web-vendor-corporate-records.yaml`](allen-county-web-vendor-corporate-records.yaml).

The one BOSC-adjacent subdivision with its own site, **Shawnee Township** (Shawnee II Phase 2 / sewer), is on **Anne Decker** — the vendor pattern is township-level, not county-wide.

## Full results

### County offices — all CorpComm Group, WordPress 6.9.4 on GoDaddy

`allencountyohio.com` (Developed by CorpComm Group, Inc.) · Engineer · Clerk of Courts *(both credited + linked to corpcommgroup.com)* · Commissioners, Treasurer, Prosecutor *(same template/version/registrar, no in-page credit — inferred CorpComm)*. **Sheriff** sits behind Cloudflare with no credit; **Board of Elections** runs on the Ohio SOS statewide template (not county-procured). The whole cluster is **one GoDaddy account** — `160.153.0.x` /24 (main `.4`, clerk `.61`, commissioners `.225`, auditor `.236`), all WordPress 6.9.4, **hosted/managed by AhelioTech** (per the 2023–24 minutes).

> **The Auditor's site breaks the "outside vendor only" picture.** `allencountyohauditor.com` (own domain, theme `thegov`, GoDaddy `160.153.0.236`, **no CorpComm footer credit**) carries a WordPress author archive for **`b_mauk` — "Brian Mauk – Allen County Auditor," the county IT Director**. That is direct evidence of **in-house edit access** to a site in the county cluster: the county is not merely a passive client of an outside firm. (Confirmed on the Auditor site; the other office archives didn't resolve, so not yet proven for the Commissioners' own host.) Note also classic WP author-enumeration — `/author/b_mauk/` leaks the admin username even though the `wp-json` user list is locked (401).

> **Vendor of record is a dissolved corporation.** Ohio SOS filings show **CorpComm Group, Inc.** (charter #532078; f/k/a *T. R. Stuckey and Associates, Inc.*, renamed 1996; pres./agent **Timothy R. Stuckey**) filed a **Certificate of Dissolution effective June 5, 2023** (resolution dated Jan 20, 2023). Yet its credit and a live link to corpcommgroup.com still appear on the county main/Recorder, Engineer, Clerk, and AEDG sites as of this audit — i.e., the county's web presence is credited to an entity that has not legally existed for three years. This sharpens the Item-16 custody question (who holds the CMS audit logs now?). Corporate records: [`allen-county-web-vendor-corporate-records.yaml`](allen-county-web-vendor-corporate-records.yaml). Finding of fact; legal effect not asserted.

### County boards / districts / authorities

- **CorpComm:** AEDG (`aedg.org`) — *credited, links corpcommgroup.com*
- **NOW Marketing Group:** ACRTA (`acrta.com`), Fairgrounds (`allencofair.com`)
- **Modo Media (Wix):** Board of DD (`acbdd.org`), Metropolitan Housing Authority (`allenmha.com`)
- **Anne Decker:** Soil & Water Conservation District (`allenswcd.com`)
- **CivicPlus:** LACRPC (`lacrpc.com`)
- **eSchoolView:** Educational Service Center (`allencountyesc.org`)
- **Unattributed WordPress (no credit):** Public Health (`allencountypublichealth.org`, WP 7.0), Job & Family Services (`acjfs.org`), Johnny Appleseed Parks (`jampd.com`, WP 7.0). *These share the WordPress-7.0 fingerprint of the Anne Decker sites but do **not** credit her in-page — left unattributed rather than guessed.*
- **Drupal (library consortium):** Lima Public Library (`limalibrary.com`)
- **Unattributed Wix:** Port Authority (`allencoport.org`)

### Municipalities

- **City of Lima** — CivicPlus (`limaohio.gov`, .gov) + a SmartGov public portal
- **Auglaize Township** — Munibit (`auglaizetwpallencooh.gov`, .gov)
- **Shawnee Township** — **Anne Decker Marketing**
- **Village of Beaverdam** — Revize (government CMS)
- **Village of Elida** — "Site by MCG"
- **American Township** — Wix, **built by students** ("created by the students of…")
- **Village of Bluffton** — Duda platform, "Site by:" unresolved
- **Village of Spencerville** — legacy Xara static site
- **Village of Cairo** — unattributed WordPress 7.0
- **City of Delphos** — blocked the audit client (HTTP 403); platform undetermined

### School districts

**Finalsite:** Allen East, Delphos City, Elida Local, Spencerville Local · **Edlio:** Perry Local · **eSchoolView:** ESC · **Wix:** Lima City Schools · **NOW Marketing:** Apollo Career Center · **Undetermined (JS-rendered):** Shawnee Local (`limashawnee.com`), Bath Local (`bathwildcats.org`)

### No official website

- **Townships:** Amanda, Jackson, Marion, Monroe, Richland, Spencer, Sugar Creek (contact via county only)
- **Villages:** Harrod (Facebook only), Lafayette (placeholder)
- **Fort Shawnee** — residents voted to **disincorporate in 2012**; no municipal government or site

## Caveats

- Reflects sites **as served on 2026-06-05**; the WHOIS creation date is the domain's, not the current build.
- "Inferred CorpComm" on the four county subdomains rests on an identical WordPress-6.9.4 / GoDaddy / shared-template signature, not an in-page credit — strong but not a self-attribution. If you need it courtroom-solid, the proof is a single `view-source` on each footer (or the county's web-services contract).
- Three sites were bot-blocked or JS-rendered at capture (Delphos, Shawnee/Bath schools) and are marked undetermined rather than guessed.

*Sources for entity rosters and URLs: Allen County Commissioners/Treasurer directories, LACRPC, and per-entity searches; full citations are in the capture log. Vendor attributions are first-party (the sites' own footers/links), saved under the records folder above.*
