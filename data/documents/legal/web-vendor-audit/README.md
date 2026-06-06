# Allen County, OH — government-entity website vendor audit (original records)

**Captured:** 2026-06-05 · **Collection:** `legal/` · **Method:** raw HTTP GET + WHOIS

This folder holds the **immutable original records** for an audit of who builds,
hosts, and registers the public-facing websites of Allen County, Ohio government
entities and subdivisions. It exists to document, with primary artifacts, the
third-party private vendors that sit between the public and these governments'
web/CMS infrastructure — relevant to the BOSC public-records campaign's
**Ex. C "county website CMS audit logs"** request and the records-custody question
(if a private vendor runs the CMS, that vendor holds the audit logs).

## Contents

- `html/<slug>.html` — the raw, unmodified HTML body returned by the entity's
  homepage (`curl -L`, redirects followed). The vendor/CMS evidence lives in the
  footer credit (`Developed by …`, `Website by …`, `Site by …`), the
  `<meta name="generator">` tag, outbound vendor links, and `wp-content/themes/…`
  paths.
- `whois/<slug>.whois.txt` — the full WHOIS registration record for each
  registrable domain (registrar, creation date, name servers, registrant where
  not privacy-shielded).
- `capture.sh` — the capture script. Input: `slug|Entity Name|url` lines on stdin.
  Saves HTML + WHOIS and emits a TSV finding row. Idempotent (re-running re-pulls).
- `finalize.sh` — re-derives the vendor/CMS/registrar/created fields from the saved
  captures, for reproducibility independent of the live sites.

## Reproduce

```sh
echo 'allen-county-main|Allen County (main)|https://allencountyohio.com/' | ./capture.sh
./finalize.sh | column -t -s$'\t'
```

## Provenance & cautions

- Captures reflect each site **as served on 2026-06-05**; sites change. The WHOIS
  `Creation Date` is the domain's, not the current build's.
- A few homepages were JS-rendered or bot-blocked at capture time and have a thin
  HTML body (see the audit's `notes` per entity): `delphos-city` (HTTP 403),
  `shawnee-schools`, `bath-schools`. Their platform is marked *undetermined*.
- `allen.boe.ohio.gov` is hosted on the Ohio Secretary of State's statewide
  template, not a county-procured vendor.
- The reviewed, structured analysis derived from these records is the committed
  artifact at `data/extracted/legal/allen-county-web-vendor-audit.{yaml,md}`.
  **Never edit files here to match the analysis — re-capture instead.**
