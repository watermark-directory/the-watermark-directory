import { describe, expect, it } from "vitest";
import { type AskUnit, prepare, retrieve, search, tokenize } from "../../functions/api/_lib/retrieval";

// A small corpus standing in for the citation-bearing bundle feeds.
const UNITS: AskUnit[] = [
  {
    id: "records:aedg/roundabouts.summary.opc.yaml",
    feed: "records",
    title: "Roundabouts OPC — summary",
    url: "/network/american-sugar-creek-allen-co/site/records/opc/",
    text: "opinion of probable cost estimate roadway subtotal earthwork drainage roundabout intersection",
    source: "data/documents/aedg/PRR-01-bundle.ocr.pdf",
    page: 318,
    source_kind: "document",
    verified: true,
  },
  {
    id: "timeline:2019-confidentiality",
    feed: "timeline",
    title: "2019-03-01 — Confidentiality agreement signed",
    url: "/network/american-sugar-creek-allen-co/timeline",
    text: "the parties executed a non-disclosure confidentiality agreement covering the project",
    source: "data/extracted/legal/nda.yaml",
    source_kind: "document",
    verified: true,
  },
  {
    id: "entities:AMAZON",
    feed: "entities",
    title: "Amazon.com Services LLC",
    url: "/wiki/entities/amazon-com-services-llc/",
    text: "cloud hyperscaler datacenter operator candidate consumer",
    source: "data/extracted/entities/graph.yaml",
    source_kind: "document",
  },
];

describe("tokenize", () => {
  it("lowercases, drops stopwords/noise, and folds a trailing plural", () => {
    expect(tokenize("The Roundabouts and a COST")).toEqual(["roundabout", "cost"]);
  });
  it("returns no tokens for whitespace or pure stopwords", () => {
    expect(tokenize("the and of to")).toEqual([]);
  });
});

describe("BM25 retrieve", () => {
  it("ranks the on-topic unit first for a corpus question", () => {
    const hits = retrieve(UNITS, "roundabout cost estimate", 3);
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0].unit.id).toBe("records:aedg/roundabouts.summary.opc.yaml");
  });

  it("matches a title term (titles are weighted)", () => {
    const hits = retrieve(UNITS, "confidentiality agreement", 3);
    expect(hits[0].unit.feed).toBe("timeline");
  });

  it("carries each hit's citation through retrieval", () => {
    const [top] = retrieve(UNITS, "roundabout", 1);
    expect(top.unit.source).toBe("data/documents/aedg/PRR-01-bundle.ocr.pdf");
    expect(top.unit.page).toBe(318);
  });

  it("returns nothing for an out-of-corpus question (→ refusal upstream)", () => {
    expect(retrieve(UNITS, "banana bread recipe")).toEqual([]);
  });

  it("returns nothing for an empty query", () => {
    expect(retrieve(UNITS, "   ")).toEqual([]);
  });

  it("respects the top-k cap", () => {
    const prepared = prepare(UNITS);
    expect(search(prepared, "agreement cloud roadway", 2).length).toBeLessThanOrEqual(2);
  });
});
