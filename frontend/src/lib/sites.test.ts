import { describe, expect, it } from "vitest";
import { ACTIVE_SITE_SLUG, activeSite, comingSoonSites, SITES, siteBadge } from "./sites";

describe("sites registry — the BOSC network (#304)", () => {
  it("has unique slugs and exactly one selectable (live) site — the active build", () => {
    const slugs = SITES.map((s) => s.slug);
    expect(new Set(slugs).size).toBe(slugs.length);
    const selectable = SITES.filter((s) => s.selectable);
    expect(selectable.map((s) => s.slug)).toEqual([ACTIVE_SITE_SLUG]);
    expect(selectable[0].status).toBe("live");
    expect(activeSite().slug).toBe(ACTIVE_SITE_SLUG);
  });

  it("keeps Fort Wayne onboard-fast but NOT selectable (the locked decision)", () => {
    const ftw = SITES.find((s) => s.slug === "fort-wayne");
    expect(ftw).toBeDefined();
    expect(ftw?.selectable).toBe(false);
    expect(ftw?.status).toBe("onboarding"); // a live facility, but the build is queued
    expect(ftw?.codename).toBe("GCP");
  });

  it("routes the live site to the root and everything else to its coming-soon page", () => {
    for (const s of SITES) {
      if (s.selectable) expect(s.href).toBe("/bosc");
      else expect(s.href).toBe(`/network/${s.slug}`);
    }
  });

  it("comingSoonSites() is every non-selectable site, each carrying a tracking issue", () => {
    const soon = comingSoonSites();
    expect(soon.some((s) => s.slug === ACTIVE_SITE_SLUG)).toBe(false);
    expect(soon.map((s) => s.slug)).toEqual(["fort-wayne", "defiance", "findlay", "toledo"]);
    for (const s of soon) expect(s.issue).toBeTruthy();
  });

  it("badges a site by codename, falling back to its mono", () => {
    expect(siteBadge({ ...SITES[0] })).toBe("BOSC");
    const defiance = SITES.find((s) => s.slug === "defiance")!;
    expect(siteBadge(defiance)).toBe("DEF"); // no codename → mono
  });
});
