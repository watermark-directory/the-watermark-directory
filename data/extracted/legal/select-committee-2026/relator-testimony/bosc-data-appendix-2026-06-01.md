# Data Appendix — Cloud Pricing, AI Hardware, and Facility Resource Economics

**Companion to the Response Fact Sheet — Ohio Select Committee on Data Centers**

**Witness:** Cory Parent — interested party (cloud infrastructure engineer)

**Dated:** Reference figures as of **May 2026** · **prepared but not submitted** to the Committee.

**Source:** [bosc-data-appendix-2026-06-01.pdf](../../../../documents/legal/select-committee-2026/relator-testimony/bosc-data-appendix-2026-06-01.pdf) (4 pp., text layer)

> Faithful reproduction of the appendix text. Figures are **industry reference
> ranges** with the witness's own cited sources (footnotes 1–7) — representative
> magnitudes, **not** facility-specific values for any single data center. Three
> points the figures establish: a government cloud carries a real, recurring price
> premium; AI-class hardware is an order of magnitude more power-dense and costly
> than the equipment a sales-tax-exemption forecast was built around; and a single
> large facility's power and water footprint is a community-scale resource
> commitment.

---

## 1. The government-cloud premium

Government and sovereign cloud environments cost more than equivalent commercial
cloud — physical isolation, U.S.-persons staffing, and compliance overhead rather
than added compute. The premium is **recurring**: it applies to every hour and
every gigabyte, for the life of the workload.

**Representative commercial vs. GovCloud pricing (AWS)**

| Service / example | Commercial AWS | AWS GovCloud | Premium |
|---|---|---|---|
| EC2 t3.medium (on-demand, per hour) | $0.0416 | $0.0520 | ~25% |
| S3 standard storage (per GB-month) | $0.0240 | $0.0288 | ~20% |
| EC2 compute, general range | baseline | +20–25% | 20–25% |
| Overall GovCloud vs. commercial | baseline | +20–30% | 20–30% ¹ |

*Sources: CapLinked GovCloud pricing analysis (2026); AWS EC2 on-demand pricing; Matlock LLC defense-cloud guide (5–25% application-infrastructure range). Representative on-demand rates; reserved/committed-use pricing differs.*

Not unique to one vendor: Boston Consulting Group documents sovereign-cloud
premiums of **up to 30%** industry-wide; Microsoft, Google, and Oracle all operate
higher-cost government clouds (Azure Government, Google Distributed Cloud / Assured
Workloads). ²

## 2. AI-class hardware: cost and power density

The sales-tax exemption is scored against a forecast of equipment purchases.
AI-class hardware changes both terms: each unit costs far more than conventional
servers, and it is replaced on a short cycle. A single high-end GPU server can
exceed half a million dollars, and per-rack power is ~an order of magnitude above
a conventional rack.

**GPU and server hardware costs (purchase)**

| Item | Approx. purchase cost | Notes |
|---|---|---|
| NVIDIA H100 (single GPU) | $25,000–$40,000 | Hopper generation |
| NVIDIA B200 (single GPU) | $30,000–$50,000 | Blackwell generation |
| 8-GPU H100 server | $200,000–$450,000 | Complete system |
| DGX B200 (8-GPU server) | ~$515,000 | Complete system |
| DGX B300 (8-GPU server) | $300,000–$350,000 | Blackwell Ultra (2026) |

*Sources: IntuitionLabs NVIDIA GPU pricing guide (Apr 2026); GMI Cloud H100 analysis (2026); aitooldiscovery Blackwell guide (2026). Purchase implies ~30–40% of hardware cost annually in operating cost and 6–12 month procurement.* ³

**Representative cloud rental rates (per GPU-hour, on-demand)**

| GPU | Hyperscaler on-demand | Neo-cloud / spot |
|---|---|---|
| H100 | $4–$8 / hr | ~$2 / hr (PCIe); ~$1 spot |
| H200 | $3.72–$10.60 / hr | from ~$3.80 / hr |
| B200 | ~$14–$18 / hr | ~$2.12 / hr spot |

*Sources: Spheron GPU pricing comparison (May 2026); GMI Cloud (2026); Jarvislabs H200 guide (2026). Reserved pricing runs 20–40% below on-demand.* ⁴

**Power density: conventional vs. AI racks**

| Rack type | Power per rack | Cooling |
|---|---|---|
| Traditional enterprise rack | 5–15 kW | Air |
| H100-class AI rack | 40–50 kW | Air / liquid |
| B200-class AI rack | 60+ kW | Liquid |
| GB200 NVL72 rack-scale system | 120–140 kW | Liquid (mandatory) |

*Sources: NVIDIA HGX data-center physical-requirements guidance, via IntuitionLabs (2025–2026). A single H100 GPU draws ~700 W; an 8-GPU H100 server ~5.6 kW before cooling/networking. Industry projections reach 250–900 kW per rack by 2027.* ⁵

## 3. Facility power and water economics

At the facility level, the figures translate into a community-scale resource
commitment. **Power capacity is the defining metric** — the same 25-MW line used
in Ohio's utility tariff and the proposed amendment — and cooling water, often
withheld as proprietary, can reach millions of gallons a day depending on the
cooling method.

**Facility power capacity (typical ranges)**

| Facility scale | Power capacity |
|---|---|
| Mid-size enterprise data center | under 5 MW |
| Smaller hyperscale site | 10–30 MW |
| Typical hyperscale facility | 20–40 MW (new builds 50–100 MW) |
| Large hyperscale campus | 100 MW – 1 GW |
| **Ohio tariff / amendment threshold (reference)** | **25 MW** |

*Sources: C&C Technology Group hyperscale power analysis (2025); TechPlusTrends AI data-center power guide (2026). A 50–100 MW facility can use as much electricity in a year as 400,000+ EVs.* ⁶

**Water use and efficiency (cooling)**

| Metric / facility | Value | Basis |
|---|---|---|
| Industry-average water efficiency (WUE) | ~1.8–1.9 L/kWh | The Green Grid |
| Mid-size center, open-loop cooling | ~110M gal/yr | EESI |
| Large hyperscale, evaporative cooling | up to 5M gal/day | EESI / Vertiv |
| Efficient (closed-loop / chip cooling) | ~0.2–0.3 L/kWh | Meta; Microsoft |
| U.S. data-center water use, 2023 | ~17B gal (could double by 2028) | TechTarget |

*Sources: EESI; Vertiv WUE analysis (2025); dgtlinfra / Meta and Microsoft sustainability disclosures (2024–2026); TechTarget. **Cooling-water blowdown discharge is typically 20–40% of cooling-system water use** — the wastewater dimension relevant to municipal treatment capacity.* ⁷

Two caveats keep these honest. Water efficiency varies enormously by cooling
method and climate — the same operator can report 0.2 L/kWh at one site and over
1.5 L/kWh in an arid region — which is why **facility-level disclosure, not a
portfolio average**, is what a host community needs. And **power capacity, not
square footage**, determines a facility's grid and fiscal footprint, which is why
a capacity-based definition is the workable one.

---

## Sources

1. **Government-cloud premium.** AWS GovCloud compute ~20–25% above commercial AWS; GovCloud overall 20–30% higher (EC2 t3.medium $0.0416 vs $0.0520/hr ~25%; S3 $0.024 vs $0.0288/GB-month ~20%). Defense-cloud guide cites 5–25% application-infrastructure range. CapLinked, "GovCloud Pricing in 2026"; AWS EC2 on-demand pricing; Matlock LLC, 2026.
2. **Sovereign-cloud premium, industry-wide.** BCG documents sovereign-cloud premiums up to 30% (isolation, U.S.-persons staffing, compliance). Azure Government, Google Distributed Cloud / Assured Workloads, Oracle comparable. BCG, "Cloud Cover," Aug 2025; vendor docs 2025–2026.
3. **AI GPU/server purchase costs.** H100 ~$25–40k; B200 ~$30–50k; 8-GPU H100 servers ~$200–450k; DGX B200 ~$515k; DGX B300 (shipped Jan 2026) ~$300–350k. ~30–40% of hardware cost annually in opex; 6–12 month procurement. IntuitionLabs; GMI Cloud; aitooldiscovery, 2026.
4. **AI GPU cloud rental (on-demand, per GPU-hour).** H100 ~$4–8 (hyperscaler), ~$2 PCIe / ~$1 spot; H200 ~$3.72–10.60; B200 ~$14–18, ~$2.12 spot. Reserved 20–40% below on-demand. Spheron, May 2026; GMI Cloud; Jarvislabs, 2026.
5. **Rack power density and cooling.** Enterprise ~5–15 kW; H100-class 40–50 kW; B200-class 60+ kW; GB200 NVL72 120–140 kW (liquid mandatory). Single H100 ~700 W; 8-GPU H100 server ~5.6 kW pre-cooling. Projections 250–900 kW/rack by 2027. NVIDIA HGX guidance via IntuitionLabs, 2025–2026.
6. **Facility power capacity.** Mid-size <5 MW; smaller hyperscale 10–30 MW; typical 20–40 MW (new builds 50–100 MW); large campuses >100 MW, AI "gigafactories" ~1 GW. 50–100 MW ≈ 400,000+ EVs/yr. The 25 MW reference matches the AEP Ohio tariff and proposed amendment thresholds. C&C Technology Group, 2025; TechPlusTrends, 2026.
7. **Facility water use and efficiency.** WUE ~1.8–1.9 L/kWh; mid-size open-loop ~110M gal/yr; large evaporative-cooled up to ~5M gal/day; efficient closed-loop / chip-cooled ~0.2–0.3 L/kWh. U.S. data centers ~17B gal in 2023, projected to ~double by 2028; cooling blowdown ~20–40% of cooling-system water use. EESI; Vertiv; dgtlinfra; Meta/Microsoft disclosures; TechTarget, 2024–2026.
