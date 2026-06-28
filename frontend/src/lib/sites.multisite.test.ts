import { describe, expect, it } from "vitest";
import { siteBase } from "./routes";
import {
  ACTIVE_SITE_SLUG,
  type NetworkSite,
  SITES,
  comingSoonFrom,
  currentSiteForPath,
  selectablePathsFrom,
  siteForPathIn,
} from "./sites";
import { storyFor } from "./walk";

// Two-selectable-site chrome parity (#746, closing #740's Done-when). The framework shipped with
// Lima as the sole `selectable` site, so "two selectable sites switchable in one build, each its
// own sections + story, Lima byte-identical" was never exercised. This drives the multi-site
// routing/registry seam (`*From(sites)`) with a TEST-ONLY second selectable site and asserts both
// render their own chrome while Lima's output is invariant to the second site's presence.
//
// The full astro-build HTML diff is the stronger proof; it's gated on a committed Fort Wayne
// sample-bundle fixture (the real `selectable` promotion / "second live build" cutover) and stays
// a follow-up. This locks the per-site *logic* now.

/** The real registry with Fort Wayne promoted to a second selectable (live) site — fixture only. */
const TWO_SELECTABLE: NetworkSite[] = SITES.map((s) =>
  s.slug === "fort-wayne" ? { ...s, selectable: true, status: "live" } : s,
);

describe("multi-site chrome parity (#746)", () => {
  const single = selectablePathsFrom(SITES); // today's one-selectable build (Lima alone)
  const dual = selectablePathsFrom(TWO_SELECTABLE); // two selectable sites

  it("today's build has exactly one selectable site (Lima)", () => {
    expect(single.map((p) => p.props.slug)).toEqual([ACTIVE_SITE_SLUG]);
  });

  it("a second selectable site adds its own route, keyed by its own siteBase", () => {
    expect(dual.map((p) => p.props.slug).sort()).toEqual(["fort-wayne", "lima"]);
    const fw = dual.find((p) => p.props.slug === "fort-wayne");
    expect(fw?.params.site).toBe(siteBase("fort-wayne").replace("/network/", ""));
  });

  it("leaves Lima's path+props byte-identical (the discipline held through every #724 merge)", () => {
    const limaSingle = single.find((p) => p.props.slug === "lima");
    const limaDual = dual.find((p) => p.props.slug === "lima");
    expect(limaDual).toEqual(limaSingle);
  });

  it("routes each selectable site to its own chrome tier; promotion flips the tier", () => {
    // A Fort Wayne path is network chrome today (not selectable) and site chrome once promoted.
    expect(siteForPathIn(SITES, "/network/fort-wayne/watershed")).toBeNull();
    expect(siteForPathIn(TWO_SELECTABLE, "/network/fort-wayne/watershed")?.slug).toBe("fort-wayne");
    // Lima still routes to Lima, unaffected by Fort Wayne's promotion — no cross-bleed either way.
    expect(siteForPathIn(TWO_SELECTABLE, "/network/american-sugar-creek-allen-co/timeline")?.slug).toBe(
      "lima",
    );
    expect(siteForPathIn(TWO_SELECTABLE, "/network/fort-wayne")?.slug).toBe("fort-wayne");
  });

  it("each selectable site resolves its OWN story (#733 made this real)", () => {
    const lima = storyFor("lima", "project-bosc");
    const fw = storyFor("fort-wayne", "project-zodiac");
    expect(lima?.chapters.map((c) => c.slug)).toEqual([
      "who",
      "assembly",
      "scale",
      "water",
      "cost",
      "opacity",
    ]);
    expect(fw?.chapters.map((c) => c.slug)).toEqual(["who", "power", "water"]);
    expect(lima?.codename).not.toBe(fw?.codename);
  });

  it("the switcher's current state reacts to a coming-soon site, where the tab tier does not (#793)", () => {
    // The tab-tier resolver (`siteForPath`) is null on a non-selectable site's watch page...
    expect(siteForPathIn(SITES, "/network/fort-wayne")).toBeNull();
    // ...but the switcher resolver names the current site regardless of `selectable`.
    expect(currentSiteForPath("/network/fort-wayne")?.slug).toBe("fort-wayne");
    expect(currentSiteForPath("/network/american-sugar-creek-allen-co/timeline")?.slug).toBe("lima");
    // Off the network (the directory + cross-cutting globals) → no current site.
    expect(currentSiteForPath("/")).toBeNull();
    expect(currentSiteForPath("/about")).toBeNull();
  });

  it("promoting a site removes it from the coming-soon set", () => {
    expect(comingSoonFrom(SITES).map((s) => s.slug)).toContain("fort-wayne");
    expect(comingSoonFrom(TWO_SELECTABLE).map((s) => s.slug)).not.toContain("fort-wayne");
    // Lima is never coming-soon in either world.
    expect(comingSoonFrom(TWO_SELECTABLE).map((s) => s.slug)).not.toContain("lima");
  });
});
