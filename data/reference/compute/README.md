# Compute / AI-capacity reference parameters

Committed reference inputs for `bosc.facility` — the subsystem that derives the
data-center facility's **compute / AI capacity** from disclosed power, water, and
footprint figures (see [`docs/COMPUTE.md`](../../../docs/COMPUTE.md)). These are
**published vendor specifications and standing modeling assumptions**, not
facility-specific disclosures. The facility's actual accelerator type, count, and
utilization are **undisclosed**; the end user is Google (corpus-verified, PAAC
minutes), so both NVIDIA GPU and Google TPU options are carried and presented as
labeled **scenarios**, never as asserted facts about this facility.

Each value is consumed as a tagged input (`reference` / `assumption`) and every
output of the derivation is `derived`. Nothing here is a measurement of the facility.

## Files

| File | What | Source |
|---|---|---|
| `accelerators.yaml` | Per-accelerator specs — chip TDP, peak FLOPS by dtype (BF16/FP8/FP4 dense & 2:4 sparse; INT8 for TPU), HBM, reference server packaging — for NVIDIA H100 / H200 / B200 / GB200 NVL72 and Google TPU v5e / v5p / v6e (Trillium). `all_in_w` is derived from `tdp_w x host_overhead_factor` (the **default** chip-level overhead; per-deployment overhead is profile-keyed in `rack-density.yaml`). | Vendor datasheets + reporting, **as of June 2026** (see "Accelerator sources" below). TPU per-chip power is not officially published — tagged `assumption`. |
| `rack-density.yaml` | AI rack power-density bands (kW/rack) by accelerator class; datacenter PUE band; the accelerator-power fraction; the **`datacenter_profiles`** (per-deployment chip-level overhead, host + network split — issue #89); the **`rack_profile`** (32U+ height, 1 IB + 1 NIC, non-standard depth → derived floor area per rack — issue #88); and the footprint-method assumptions (building-coverage, white-space, rack-area fallback). | Rack-density bands reproduced from the **in-corpus relator data appendix** (cites NVIDIA HGX guidance via IntuitionLabs); PUE / fraction / footprint / **profile + rack-geometry** figures are stated `assumption`s — the profile and rack-geometry figures from the **2026-06-10 facility-design call**. |

## Accelerator sources (as of June 2026)

Specs are vendor "peak" figures. Sparse rates are 2:4 structured sparsity (≈2× dense);
TPU MXU rates are dense-only (no published sparsity rate), so INT8 TOPS is recorded.

- **NVIDIA H100 SXM5** — 700 W TDP; BF16/FP16 989 TFLOPS dense / 1,979 sparse; FP8
  1,979 dense / 3,958 sparse. NVIDIA H100 Tensor Core GPU datasheet
  (resources.nvidia.com / nvidia.com/en-us/data-center/h100); corroborated by
  Spheron "NVIDIA H100 Specs" (2026).
- **NVIDIA H200 SXM** — 700 W; same GH100 compute die as H100 (989 BF16 dense,
  3,958 FP8 sparse), 141 GB HBM3e, 4.8 TB/s. NVIDIA H200 datasheet
  (nvidia.com/en-us/data-center/h200); Spheron "NVIDIA H200 Specs" (2026).
- **NVIDIA B200** — 1,000 W (HGX B200); BF16 2,250 dense / 4,500 sparse; FP8 4,500
  dense / 9,000 sparse; FP4 9,000 dense / 18,000 sparse; 192 GB HBM3e. NVIDIA
  Blackwell B200 datasheet; Spheron "NVIDIA B200" guide (2026); Exxact Blackwell vs
  Hopper (2026).
- **NVIDIA GB200 NVL72** — rack-scale 72-GPU NVLink domain, 120–140 kW/rack, liquid
  mandatory; aggregate 720 PFLOPS FP8 dense / 1,440 PFLOPS FP4 dense per rack. Per-GPU
  figures here are the rack aggregate ÷ 72 (≈1.2 kW/GPU). NVIDIA GB200 NVL72 page
  (nvidia.com/en-us/data-center/gb200-nvl72).
- **Google TPU v5e** — ~197 BF16 TFLOPS, 394 INT8 TOPS, 16 GB HBM. Google Cloud TPU
  docs; Introl "Google TPU Architecture: 7 Generations" (2026). Per-chip power band
  ~120–200 W (assumption; midpoint 175 W).
- **Google TPU v5p** — ~459 BF16 TFLOPS, ~918 INT8 TOPS, 95 GB HBM. Same sources.
  Per-chip power band ~250–300 W (assumption; midpoint 275 W).
- **Google TPU v6e (Trillium)** — 918 BF16 TFLOPS, 1,836 INT8 TOPS, 32 GB HBM.
  Google Cloud TPU v6e documentation (docs.cloud.google.com/tpu/docs/v6e); Introl
  (2026). Per-chip power not officially published — ~300 W assumption from the stated
  ~2× v5e efficiency.

The raw search/fetch responses behind these figures are not cached (small, stable
vendor specs transcribed by hand with the citations above), unlike the live-API
connectors whose responses cache under `data/cache/`.

## In-corpus figures (cited directly, not external)

Rack-density bands, the 700 W per-H100 chip / ~5.6 kW per 8-GPU server figures, the
WUE/PUE context, and the facility power scales come from the **in-corpus relator
data appendix**:
`data/extracted/legal/select-committee-2026/relator-testimony/bosc-data-appendix-2026-06-01.md`
(itself citing NVIDIA HGX guidance via IntuitionLabs, The Green Grid, EESI/Vertiv).
The air-permit IT-load chain (114 gensets × 2.75 ekW ≈ 313 MW backup → ~275 MW IT)
in `bosc.facility.power` / `bosc.hydrology.cooling` traces to OEPA Air PTI **P0138965**
(Facility 0302022054) — but the permit **is not committed** to the corpus; the figure
currently enters via a *secondhand citation*. Ingesting the permit (and the
**three-hall footprint** in its emission-unit layout, which would re-ground the
footprint method) is a tracked gap — see the
[completeness audit §4](../../extracted/legal/corpus-completeness-audit.md).

## Caveats

These are **inputs, not measurements of the facility**. Accelerator choice, count,
and utilization are undisclosed and presented as scenarios. Peak FLOPS are nameplate
— distinct from delivered throughput, which `bosc.facility.compute` derates by a
labeled MFU (model-FLOPS-utilization) assumption for any "training capacity" figure.
The footprint method is the weakest of the three (land area is not floor area; no
building footprint is documented in the plans) and is flagged as such throughout.

<!-- catalog:begin (generated by `bosc catalog render`; do not edit inside) -->

**Cataloged datasets** — generated from `data/catalog/reference/`; run `bosc catalog render --apply` after editing an entry.

### `compute` — AI Accelerator & Rack-Density Compute Reference

Source: Vendor datasheets (NVIDIA H100/H200/B200/GB200; Google TPU v5e/v5p/v6e) + in-corpus relator data appendix · License: Third-party vendor datasheets + in-corpus appendix (reference use) · Access: public · Site scope: basin-shared · Refresh: on-demand, last 2026-06-11

| file | type | lfs |
| --- | --- | --- |
| `reference/compute/accelerators.yaml` | application/x-yaml | no |
| `reference/compute/rack-density.yaml` | application/x-yaml | no |

<!-- catalog:end -->
