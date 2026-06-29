# H3 · Corporate & Economic Surveillance

Who owns it, who's watching, and where the money moves: the operators behind shell LLCs,
the public-subsidy stack that pulls them in, and the capital/data flows the facilities
sit on. **Emerging hypothesis, under test** — mostly under investigation, with Lima's
abatement on record.

- `fields`: `operator` (the entity behind the LLC), `capital` (capital + public subsidy),
  `end_use` (application class — see end-use sub-thesis below).
- `groups`: `onrecord` · `subsidy` · `watch`.
- Backing narrative: `docs/ECONOMICS.md` (the public subsidizes load and consumption, not
  employment — for a counterparty it cannot name).

## Two investigative sub-theses (#904)

**Ownership/subsidy** (`sub_thesis: capture`): the operator behind the LLC + the CRA/PILOT
capture of public subsidy. This is the current primary frame. Lima is the anchor (`signal:
anchor`, CRA #548-25 on record). `tag: verified` when the subsidy instrument is on record;
`inference` when the operator is inferred but not confirmed.

**End-use** (`sub_thesis: end-use`): what the compute is actually for — the application
class running inside the facility. Once the operator is resolved, their active consumer-facing
product lines at the time of the permit application are public record (10-K, product
announcements, AWS availability-zone expansion announcements). A confirmed operator collapses
the end-use ambiguity. Field: `end_use` (e.g., `consumer_surveillance`, `financial_processing`,
`ai_inference`, `mixed`). Tag as `[inference]` until sourced from the operator's own filings.

Gate: `end_use` cannot be `[verified]` until the operator principal is on record and their
product lines are matched to the facility's announced capacity and commissioning date.
