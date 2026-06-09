"""Typed models for the facility compute-capacity derivation.

Like :mod:`bosc.hydrology.model`, these are computed by our own code, so they use
``extra="forbid"``. Every numeric field is a :class:`ProvenancedValue` (reused from
hydrology) so a derived capacity is self-auditing. The cornerstone is
:class:`ComputeCapacity`, mirroring :class:`bosc.hydrology.model.CoolingBasis`: it
captures the per-method IT-load estimates that bracket the answer, the modeling
levers (accelerator-power fraction, MFU), and a list of accelerator **scenarios** —
because the facility's actual accelerator type, count, and utilization are
undisclosed.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from bosc.hydrology.model import ProvenancedValue


class AcceleratorSpec(BaseModel):
    """A published per-accelerator vendor spec (from data/reference/compute).

    ``reference``-tagged figures (chip TDP, peak FLOPS) with ``assumption``-tagged
    all-in power. NOT a fact about the facility — one of several candidate chips.
    """

    model_config = ConfigDict(extra="forbid")

    name: str  # "H100-SXM5"
    label: str  # "H100-class (Hopper)"
    vendor: str  # NVIDIA | Google
    generation: str  # Hopper | Blackwell | v5p | ...
    tdp_w: ProvenancedValue  # chip thermal design power (reference)
    all_in_w: ProvenancedValue  # per-accelerator rack power incl. host share (derived)
    bf16_dense_tflops: ProvenancedValue  # peak dense BF16/FP16 (the training rate)
    bf16_sparse_tflops: ProvenancedValue | None = None  # 2:4 structured sparsity
    fp8_dense_tflops: ProvenancedValue | None = None
    fp8_sparse_tflops: ProvenancedValue | None = None
    fp4_dense_tflops: ProvenancedValue | None = None
    fp4_sparse_tflops: ProvenancedValue | None = None
    int8_tops: ProvenancedValue | None = None
    gpus_per_server: int = 8
    cooling: str = ""


class AcceleratorScenario(BaseModel):
    """One labeled "if the chip is X" scenario over the bracketed IT load.

    The count and aggregate FLOPS are ``derived`` ranges (low/high) from the IT-load
    bracket and the accelerator-power fraction — *conditional* on this chip. Never
    "the facility has N of these"; always "if X-class, then ~N1-N2".
    """

    model_config = ConfigDict(extra="forbid")

    spec: AcceleratorSpec
    count_low: ProvenancedValue  # accelerators if IT-load low / fraction low
    count_high: ProvenancedValue  # accelerators if IT-load high / fraction high
    count_central: ProvenancedValue  # central estimate
    # Aggregate PEAK throughput (nameplate, not delivered) across the count range.
    bf16_dense_eflops_low: ProvenancedValue  # EFLOP/s = count x per-chip / 1e6
    bf16_dense_eflops_high: ProvenancedValue
    bf16_sparse_eflops_high: ProvenancedValue | None = None
    fp8_dense_eflops_high: ProvenancedValue | None = None
    fp8_sparse_eflops_high: ProvenancedValue | None = None
    # Delivered training throughput at the labeled MFU (derated; clearly separate).
    bf16_delivered_eflops_central: ProvenancedValue | None = None


class ComputeCapacity(BaseModel):
    """The bracketed facility compute / AI capacity, derived by three methods.

    Mirrors :class:`bosc.hydrology.model.CoolingBasis`: a self-auditing bundle of
    provenance-tagged inputs and derived ranges. The three IT-load estimates
    (``it_load_power`` / ``it_load_water`` / ``it_load_footprint``) should bracket a
    similar value; the accelerator scenarios then turn the central IT load into
    per-chip count and FLOPS ranges. Nothing here is a measured fact about the
    facility — accelerator type/count/utilization are undisclosed.
    """

    model_config = ConfigDict(extra="forbid")

    # --- The three independent IT-load estimates (MW) ------------------------
    it_load_power: ProvenancedValue  # method 1: air-permit gensets (PRIMARY)
    it_load_water_low: ProvenancedValue  # method 2: cooling-water back-solve (low)
    it_load_water_high: ProvenancedValue  # method 2: cooling-water back-solve (high)
    it_load_footprint_low: ProvenancedValue  # method 3: footprint (WEAKEST)
    it_load_footprint_high: ProvenancedValue  # method 3 (high)

    # The cross-method bracket on IT load (the headline robustness statement).
    it_load_bracket_low: ProvenancedValue  # min across methods (derived)
    it_load_bracket_high: ProvenancedValue  # max across methods (derived)

    # --- The shared modeling levers ------------------------------------------
    accelerator_power_fraction_low: ProvenancedValue  # share of IT power to accelerators
    accelerator_power_fraction_high: ProvenancedValue
    mfu: ProvenancedValue  # model-FLOPS-utilization for delivered throughput

    # --- The conditional accelerator scenarios -------------------------------
    scenarios: list[AcceleratorScenario]

    # An apples-to-apples cross-scenario figure: equivalent H100-class GPUs at the
    # central IT load (so a TPU/B200 deployment is comparable to a familiar unit).
    equivalent_h100_low: ProvenancedValue
    equivalent_h100_high: ProvenancedValue

    method: str = (
        "power (air-permit gensets, primary); cooling-water back-solve (cross-check); "
        "footprint (weakest) -> accelerator count -> aggregate peak FLOPS by scenario"
    )

    def scenario(self, name: str) -> AcceleratorScenario | None:
        return next((s for s in self.scenarios if s.spec.name == name), None)
