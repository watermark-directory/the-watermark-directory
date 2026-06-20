import { describe, expect, it } from "vitest";
import { ACTIVE_SITE_SLUG, activeSite, comingSoonSites, SITES, siteBadge, siteForPath } from "./sites";

describe("sites registry — the Watermark network (#304)", () => {
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
    expect(ftw?.status).toBe("building"); // a live facility with its site build underway
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
    expect(soon.map((s) => s.slug)).toEqual([
      "fort-wayne",
      "defiance",
      "findlay",
      "toledo",
      "van-wert",
      "bryan",
      "ottawa",
    ]);
    for (const s of soon) expect(s.issue).toBeTruthy();
  });

  it("badges a site by codename, falling back to its mono", () => {
    expect(siteBadge({ ...SITES[0] })).toBe("BOSC");
    const defiance = SITES.find((s) => s.slug === "defiance")!;
    expect(siteBadge(defiance)).toBe("DEF"); // no codename → mono
  });
});

describe("promotion gate — the onboarding review invariant (#326)", () => {
  // `bosc onboard` proposes; promotion to a live build is a manual, parity-gated edit here.
  // These encode the gate: flipping `selectable` without `status: "live"` (or vice-versa)
  // fails CI, so a site can't slip live without the deliberate two-field change.
  it("every selectable site has status 'live'", () => {
    for (const s of SITES) if (s.selectable) expect(s.status).toBe("live");
  });

  it("no building/queued site is selectable before explicit promotion", () => {
    for (const s of SITES) if (s.status !== "live") expect(s.selectable).toBe(false);
  });
});

describe("siteForPath — the switcher's current-site resolution (#316)", () => {
  it("resolves the live Lima build for /bosc and any page beneath it", () => {
    for (const p of ["/bosc", "/bosc/", "/bosc/site/", "/bosc/watershed/map", "/bosc/timeline"]) {
      expect(siteForPath(p)?.slug).toBe("lima");
    }
  });

  it("resolves a coming-soon site (incl. not-yet-built) from its /network/<slug> route", () => {
    expect(siteForPath("/network/fort-wayne")?.slug).toBe("fort-wayne");
    expect(siteForPath("/network/defiance/")?.slug).toBe("defiance");
    expect(siteForPath("/network/toledo")?.codename).toBeNull();
  });

  it("returns null for the network hub and the cross-cutting globals (neutral state)", () => {
    for (const p of ["/network", "/network/", "/about", "/about-me", "/wiki/entities/", "/ask", "/"]) {
      expect(siteForPath(p)).toBeNull();
    }
  });

  it("does not mistake an unknown /network/<slug> for a real site", () => {
    expect(siteForPath("/network/columbus")).toBeNull();
  });

  it("strips a non-root Astro base before matching", () => {
    expect(siteForPath("/app/bosc/site/", "/app")?.slug).toBe("lima");
    expect(siteForPath("/app/network/findlay", "/app")?.slug).toBe("findlay");
    expect(siteForPath("/bosc/site/", "/")?.slug).toBe("lima"); // base "/" is a no-op
  });
});
