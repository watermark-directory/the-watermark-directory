/**
 * Build-time model for the End-use & workloads explorer (#233 / #251 interactive
 * layer). The report's [verified] spine, made selectable: "data center" names
 * businesses that answer the public's two plain questions — *who benefits* and
 * *who can use it* — completely differently. The reader picks a type and sees
 * what the Select-Committee record establishes about it, and what the Lima record
 * does (and does not) say.
 *
 * Curated, dependency-free (no bundle loader) — the content is read from the
 * committee record, not a feed, so this is client-safe and the island imports the
 * type directly. Every cell traces to docs/end-use-and-workloads.md.
 */

export type DcKey = "bitcoin" | "hyperscale" | "colocation" | "enclave";

/** What the Lima record establishes about whether the campus is this type. */
export type LimaStatus = "ruled-out" | "open";

/** How open access to the compute is — the "who can use it" axis that narrows. */
export type AccessLevel = "self" | "commercial" | "private-tenants" | "authorized-only";

export interface DcType {
  key: DcKey;
  label: string;
  tagline: string;
  ownsCompute: string;
  whoBenefits: string;
  whoCanUse: string;
  access: AccessLevel;
  localEconomy: string;
  /** The committee-record anchor that establishes this type — register one. */
  evidence: string;
  limaStatus: LimaStatus;
  limaNote: string;
}

export interface EndUseData {
  types: DcType[];
  /** What the corpus confirms about Lima (the [verified] anchor). */
  verified: string;
  /** The single question the confirmed facts can't answer (the [open] gap). */
  openQuestion: string;
}

const TYPES: DcType[] = [
  {
    key: "bitcoin",
    label: "Bitcoin mining",
    tagline: "a mine is its own customer",
    ownsCompute: "the operator — it mines on its own account",
    whoBenefits: "the operator; the machines have no external customer",
    whoCanUse: "no one else — “we don’t have customers in Bitcoin”",
    access: "self",
    localEconomy: "behind-the-meter load, minimal permanent jobs",
    evidence: "MARA Holdings volunteered the distinction itself (closing session, 2026-06-04)",
    limaStatus: "ruled-out",
    limaNote:
      "Not the Lima campus: the developer is Google, a hyperscaler, not a miner. The one type the record lets us cross off.",
  },
  {
    key: "hyperscale",
    label: "Hyperscale",
    tagline: "the owner runs the compute",
    ownsCompute: "the operator runs its own workloads (Google, Meta, AWS, Microsoft)",
    whoBenefits: "the hyperscaler; the company you can name is the company using the machines",
    whoCanUse: "the owner’s own services and its global cloud customers",
    access: "commercial",
    localEconomy: "anchors a cloud-region footprint, but lean permanent headcount",
    evidence: "the 2026-06-04 morning panel — Google/Meta/AWS/Microsoft",
    limaStatus: "open",
    limaNote:
      "Google is the [verified] developer (#234) — but the deed fixes the builder, not the occupant. Whether Google self-runs the Lima halls is open.",
  },
  {
    key: "colocation",
    label: "Colocation",
    tagline: "a landlord; tenants own the compute",
    ownsCompute: "the tenants — the operator builds and powers the hall, others run the racks",
    whoBenefits: "unknown — Vantage “cannot say” whether it or its tenants capture the abatement",
    whoCanUse: "the operator’s tenants, who need not be named on any public record",
    access: "private-tenants",
    localEconomy: "a landlord; the local benefit turns on tenants the public can’t see",
    evidence: "Vantage: “I do not know … passed through … or taken advantage by the tenants themselves”",
    limaStatus: "open",
    limaNote:
      "Hyperscale developers do lease capacity. Whether the Lima campus hosts colocation tenants — and who — is open.",
  },
  {
    key: "enclave",
    label: "Federal enclave",
    tagline: "authorized users only",
    ownsCompute: "a wholly dedicated, U.S.-citizen-staffed environment",
    whoBenefits: "the federal government / defense; the supply chain is federal and sealed",
    whoCanUse: "only authorized federal users — FedRAMP, then DoD impact levels IL4–IL6",
    access: "authorized-only",
    localEconomy: "a sealed island: capacity never reaches the open market or the local tech cluster",
    evidence:
      "AWS named the Department of War and the CIA before the committee; the DoD CC SRG; Google’s air-gapped appliance holds IL5",
    limaStatus: "open",
    limaNote:
      "The sharpest [open] facet. The PRR for County ⇄ DoD/GDLS comms returned “no records”; Google’s own testimony omits Lima. An absence is not a finding.",
  },
];

export function buildEndUse(): EndUseData {
  return {
    types: TYPES,
    verified:
      "The developer is Google ([verified], #234), and the campus is real and large. The industry’s own testimony establishes the taxonomy above.",
    openQuestion:
      "Which of these the Lima campus is — and who can use it. Confirming the customer did not resolve the use.",
  };
}

/** The access axis, ordered broad → sealed (drives the “who can use it” meter). */
export const ACCESS_ORDER: AccessLevel[] = ["commercial", "private-tenants", "authorized-only"];

export const ACCESS_LABEL: Record<AccessLevel, string> = {
  self: "no external users",
  commercial: "the owner’s commercial cloud",
  "private-tenants": "private, unnamed tenants",
  "authorized-only": "authorized federal users only",
};
