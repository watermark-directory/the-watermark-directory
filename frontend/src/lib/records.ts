/** Helpers for rendering the records feed (per-kind pages, #66). */
import type { RecordItem } from "./feeds";

/** Human labels for the contractor-agnostic record groups (mirrors nav.yaml). */
export const RECORD_GROUP_LABELS: Record<string, string> = {
  deeds: "Deeds",
  "permits-epa": "Permits — Ohio EPA / USACE",
  "permits-npdes": "Permits — NPDES",
  "permits-sos": "Business filings — Secretary of State",
  plans: "Plans",
  opc: "Cost estimates (OPC)",
};

export function groupLabel(group: string): string {
  return RECORD_GROUP_LABELS[group] ?? group;
}

/** Distinct groups present in the feed, in the canonical order above. */
export function groupsOf(records: RecordItem[]): string[] {
  const present = new Set(records.map((r) => r.group));
  const ordered = Object.keys(RECORD_GROUP_LABELS).filter((g) => present.has(g));
  // Any unknown groups (forward-compat) appended in first-seen order.
  for (const g of present) if (!ordered.includes(g)) ordered.push(g);
  return ordered;
}

/** Flatten one raw field value to a display string. */
export function fieldToString(value: unknown): string {
  if (value == null) return "—";
  if (Array.isArray(value)) return value.map(fieldToString).join("; ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

/** Whether a top-level field carried the `~` approximate marker. */
export function isApproximate(record: RecordItem, key: string): boolean {
  return record.approximate_paths.some((p) => p === key || p.startsWith(`${key}.`));
}
