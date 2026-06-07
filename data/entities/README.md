# Curated entities

Hand-curated entity records that aren't derived from the document corpus (the
code-built entity graph in `bosc.pipeline.entities` covers corpus-derived parties).
These are working inventories, marked by a flag in the file.

## `cloud-consumer-candidates.yaml`

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
