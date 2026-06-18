import { describe, expect, it } from "vitest";
import {
  assemblePrompt,
  candidateCitations,
  extractCitations,
  isRefusal,
  REFUSAL,
} from "../../functions/api/_lib/ask";
import type { Hit } from "../../functions/api/_lib/retrieval";

const HITS: Hit[] = [
  {
    score: 2,
    unit: {
      id: "records:opc.summary",
      feed: "records",
      title: "Roundabouts OPC — summary",
      url: "/bosc/site/records/opc/",
      text: "opinion of probable cost roadway subtotal",
      source: "data/documents/aedg/PRR-01-bundle.ocr.pdf",
      page: 318,
      source_kind: "document",
    },
  },
  {
    score: 1,
    unit: {
      id: "timeline:nda",
      feed: "timeline",
      title: "2019 — NDA signed",
      url: "/bosc/timeline",
      text: "confidentiality agreement",
      source: "data/extracted/legal/nda.yaml",
      source_kind: "document",
    },
  },
];

describe("assemblePrompt", () => {
  it("numbers each source [n] and embeds its provenance + text", () => {
    const { system, user } = assemblePrompt("How much do the roundabouts cost?", HITS);
    expect(system).toContain(REFUSAL);
    expect(user).toContain("[1] Roundabouts OPC — summary — data/documents/aedg/PRR-01-bundle.ocr.pdf p.318");
    expect(user).toContain("[2] 2019 — NDA signed");
    expect(user).toContain("Question: How much do the roundabouts cost?");
  });
});

describe("extractCitations", () => {
  it("resolves the [n] markers the answer used, in first-appearance order, deduped", () => {
    const cites = extractCitations(
      "The estimate is on the summary sheet [1]. An NDA preceded it [2][1].",
      HITS,
    );
    expect(cites.map((c) => c.marker)).toEqual([1, 2]);
    expect(cites[0]).toMatchObject({
      id: "records:opc.summary",
      url: "/bosc/site/records/opc/",
      source: "data/documents/aedg/PRR-01-bundle.ocr.pdf",
      page: 318,
    });
  });

  it("drops an out-of-range marker rather than fabricating a source", () => {
    expect(extractCitations("Mystery claim [9].", HITS)).toEqual([]);
  });

  it("finds no citations in an uncited answer", () => {
    expect(extractCitations("No markers here.", HITS)).toEqual([]);
  });
});

describe("candidateCitations", () => {
  it("maps every hit to a [n]-numbered citation in prompt order (#331)", () => {
    const cands = candidateCitations(HITS);
    expect(cands.map((c) => c.marker)).toEqual([1, 2]);
    expect(cands[0]).toMatchObject({
      marker: 1,
      id: "records:opc.summary",
      url: "/bosc/site/records/opc/",
      page: 318,
    });
    expect(cands[1]).toMatchObject({ marker: 2, id: "timeline:nda", page: null });
  });

  it("agrees with extractCitations on the markers an answer actually uses", () => {
    const cands = candidateCitations(HITS);
    const used = extractCitations("Cost is on the summary [1].", HITS);
    // The live link (candidate) and the final link (extracted) resolve to the same source.
    expect(cands.find((c) => c.marker === 1)).toEqual(used[0]);
  });

  it("is empty when nothing was retrieved", () => {
    expect(candidateCitations([])).toEqual([]);
  });
});

describe("isRefusal", () => {
  it("recognizes the canonical refusal regardless of trailing whitespace/case", () => {
    expect(isRefusal(`  ${REFUSAL}  `)).toBe(true);
    expect(isRefusal("i don't find that in the record.")).toBe(true);
  });
  it("does not treat a real answer as a refusal", () => {
    expect(isRefusal("The roundabouts cost $1.2M [1].")).toBe(false);
  });
});
