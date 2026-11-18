# Data-center policy research — reviewed reads

Reviewed reads of third-party policy research on Ohio's data-center industry: commissioned
economic, fiscal and community-benefit studies. Source files live under
[`data/documents/legal/datacenter-policy/`](../../../documents/legal/datacenter-policy/README.md).

## Contents

| Path | What |
|---|---|
| `ocrf-2026-state-of-ohio-data-centers.digest.yaml` | Structured read of **"The State of Ohio Data Centers in 2026"** (SRC EvalMetrics for the Ohio Chamber of Commerce Research Foundation, November 2026). It covers the IMPLAN contribution estimate (2025 and 2030), the 90-campus facility inventory and its 13-site out-of-Central-Ohio pipeline, the market, power and investment figures, the R.C. 122.175 sales-tax exemption's cost, break-even attribution and repeal scenarios, the 4,479-district property-tax simulation (Ross), and the community-benefit framework (Woodrum). It closes with a relevance-to-the-corpus synthesis and the `[open]` list. |

## Standing

- **Every figure is `[reference]`.** A commissioned study reporting a number is not the record
  of that number. Where the report rests a figure on a primary source (a Department of Taxation
  actual, a TIRC report, a PUCO order, an OPSB case), the digest names it in `rests_on`. Capture
  *that* document to upgrade the figure; never cite this one as `[verified]`.
- **Gross contribution, not net impact.** By its own statement (p. 52) the report does not
  estimate net effects, public-service and infrastructure costs, or the effects of electricity
  and water demand on other users. Do not quote it as a net benefit.
- **Not cleared for the public site.** The source is held `redistributable: false`.
- **The Technical Appendix (A–I) is not held.** Every method that rests on it is `[open]`.

## Conventions

"p. N" is the printed page number, which equals the 1-based PDF page. Figures were read from
the native text layer. That layer puts a stray space inside some numbers ("97 ,900"), which was
removed in transcription and changes no value. The `network_site` mapping of the report's
pipeline counties, and the `relevance` block, are this repo's `[inference]`, not the report's.
The program terms on p. 7 and p. 29 agree with ODOD Director Mihalik's testimony of 2026-05-27,
which is already in the corpus as a primary source
(`../select-committee-2026/witness-submissions.digest.yaml`). Cite that testimony, not this report.
