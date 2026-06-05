# Who manages the websites of Allen County, Ohio governments — vendor audit

**Captured 2026-06-05.** Original records: [`data/documents/legal/allen-county-web-audit/`](../../documents/legal/allen-county-web-audit/) (41 sites, raw HTML + WHOIS). Structured findings: [`allen-county-web-vendor-audit.yaml`](allen-county-web-vendor-audit.yaml).

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

## Why this matters to the records campaign

Ex. C asks for the **county website CMS audit logs**. Those logs don't live with the county — they live with **CorpComm Group**, the private vendor running the county's WordPress install (and the constitutional-office subdomains, and AEDG). That is a concrete records-custody point: a §149.43 request for CMS audit logs implicates a **third-party processor**, and the county cannot treat records held by its web contractor as beyond reach. It also means the **same vendor** touches both the county's public-records portal *and* the economic-development group's site — worth a line in any follow-up request (who has admin/edit access, retention of audit logs, contract terms).

The one BOSC-adjacent subdivision with its own site, **Shawnee Township** (Shawnee II Phase 2 / sewer), is on **Anne Decker** — the vendor pattern is township-level, not county-wide.

## Full results

### County offices — all CorpComm Group, WordPress 6.9.4 on GoDaddy
`allencountyohio.com` (Developed by CorpComm Group, Inc.) · Engineer · Clerk of Courts *(both credited + linked to corpcommgroup.com)* · Commissioners, Auditor, Treasurer, Prosecutor *(same template/version/registrar, no in-page credit — inferred CorpComm)*. **Sheriff** sits behind Cloudflare with no credit; **Board of Elections** runs on the Ohio SOS statewide template (not county-procured).

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

_Sources for entity rosters and URLs: Allen County Commissioners/Treasurer directories, LACRPC, and per-entity searches; full citations are in the capture log. Vendor attributions are first-party (the sites' own footers/links), saved under the records folder above._
