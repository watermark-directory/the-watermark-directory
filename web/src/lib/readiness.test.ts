import { describe, expect, it } from "vitest";
import {
  isAvailable,
  isReferenceSite,
  lockedSections,
  SECTION_META,
  type ReadinessSection,
  sectionStatus,
  siteReadiness,
} from "./readiness";

// Pinned against the committed full-vs-partial fixture pair: `sample-bundle/lima` (the live
// reference build, every feed) vs `sample-bundle/fort-wayne` (a real partial peer — the Project
// Zodiac campus + rsei/econ/network, but no timeline / people / exhibits). The readiness model is
// what keeps a thin peer navigable without ever borrowing Lima's record.

describe("isReferenceSite", () => {
  it("is the live reference build alone", () => {
    expect(isReferenceSite("lima")).toBe(true);
    expect(isReferenceSite("fort-wayne")).toBe(false);
    expect(isReferenceSite("urbana")).toBe(false);
  });
});

describe("the reference build", () => {
  it("has every section available regardless of counts — it hosts the network-global content", () => {
    const readiness = siteReadiness("lima");
    for (const section of Object.keys(SECTION_META) as ReadinessSection[]) {
      expect(readiness[section]).toBe("available");
    }
    expect(lockedSections("lima")).toEqual([]);
  });
});

describe("a partial peer (Fort Wayne)", () => {
  it("opens the sections it has real data for", () => {
    // records / places / geo+rsei / econ+network are all present in the FW bundle.
    expect(isAvailable("fort-wayne", "record")).toBe(true);
    expect(isAvailable("fort-wayne", "places")).toBe(true);
    expect(isAvailable("fort-wayne", "watershed")).toBe(true);
    expect(isAvailable("fort-wayne", "economy")).toBe(true);
  });

  it("locks the sections whose feeds are empty — not fabricated from Lima", () => {
    // timeline:0 / people:0 / exhibits:0 in the FW bundle.
    expect(sectionStatus("fort-wayne", "timeline")).toBe("locked");
    expect(sectionStatus("fort-wayne", "people")).toBe("locked");
    expect(sectionStatus("fort-wayne", "exhibits")).toBe("locked");
  });

  it("opens the story when one is registered, even on a thin peer", () => {
    // FW carries the Project Zodiac StoryRef in the registry — the on-ramp works day one.
    expect(sectionStatus("fort-wayne", "story")).toBe("available");
  });

  it("locks the network-global sections (reports/leads) for any peer", () => {
    // reports + leads read the Lima-global narrative/audit — reference-only until a per-site feed.
    expect(sectionStatus("fort-wayne", "reports")).toBe("locked");
    expect(sectionStatus("fort-wayne", "leads")).toBe("locked");
  });

  it("reports the full locked set", () => {
    expect(lockedSections("fort-wayne").sort()).toEqual(
      ["exhibits", "leads", "people", "reports", "timeline"].sort(),
    );
  });
});

describe("SECTION_META", () => {
  it("carries a label + a 'what lands here' line for every gateable section", () => {
    for (const meta of Object.values(SECTION_META)) {
      expect(meta.label.length).toBeGreaterThan(0);
      expect(meta.holds.length).toBeGreaterThan(0);
    }
  });
});
