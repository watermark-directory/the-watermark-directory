# Curated entities

Hand-curated entity inputs that aren't derived from the document corpus (the
code-built entity graph in `bosc.pipeline.entities` covers corpus-derived parties).
These are working inventories under `profiles/`, each marked by a flag/marker in
the file and loaded by `bosc.candidates`.

```
data/entities/profiles/
  cloud-consumer-candidates.yaml   # demand-fit corridor operations
  defense-contractors.yaml         # DoD-prime seed list + match patterns
```

## `profiles/cloud-consumer-candidates.yaml`

29 corridor operations (I-75 / I-70 / US-68) marked `cloud_consumer_candidate:
true` on **demand-fit only** — i.e. each has at least one workload class
(industrial telemetry, vision/ML, ERP/data-warehouse, low-latency edge, or
regulated-data compute) that hyperscale/edge infrastructure exists to serve.

**Important — what the marker means.** A candidate is selected for *what the
business does*, from public descriptions. It is **not** a customer, prospect, or a
party connected to Project BOSC; nothing here asserts any entity uses, plans to
use, or was approached about data-center capacity. `confirmed_cloud_relationship`
records a publicly documented cloud tie where one exists (5 of 29, e.g. Ford/Google,
P&G/Google Cloud, Nutrien/AWS, Honda's own data center) — typically corporate-level,
not a local project. `speculative: true` flags entries that are placeholders or
pending (Gateway Commerce Park future tenants; Roshel pending acquisition).

Fields per entity: `name, tier (1–4 by workload relevance), kind, sector, location,
workload_classes, confirmed_cloud_relationship, cloud_consumer_candidate, basis`.

Source: a June-2026 demand-fit inventory working note (corridor operations), used
here purely as a list of organizations.

## `profiles/defense-contractors.yaml`

A seed list of major U.S. Department of Defense **prime contractors**, each with a
display `name`, optional `note`, and a list of uppercase `patterns`. The patterns
are matched **case-insensitively, as substrings** against (a) the corpus entity
graph and (b) Allen County parcel owner names from the `allen_gis` connector.

**Important — what a match means.** A hit is a *lead to verify*, **not** a
classification and **not** an accusation. It does not change an entity's graph
classification, and a hit on a dual-use firm (e.g. Honeywell) may be a purely
commercial holding. See the file header for matching semantics and how to add a
contractor without introducing false positives.

Origin: imported from the Periplus (`../gis`) fork at the BOSC spin-out point
(where it seeded a `flag_defense_contractor` anomaly flag), then promoted here to a
first-class curated entity input.
