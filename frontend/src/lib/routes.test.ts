import { describe, expect, it } from "vitest";
import { SITE_BASE, STORY_BASE } from "./routes";
import { withSite, withStory } from "./site";

describe("routes", () => {
  it("SITE_BASE is the network-rooted live site path (was /bosc)", () => {
    expect(SITE_BASE).toBe("/network/american-sugar-creek-allen-co");
  });

  it("STORY_BASE nests the project-bosc story under the site", () => {
    expect(STORY_BASE).toBe(`${SITE_BASE}/stories/project-bosc`);
  });

  it("withSite prefixes the site root (deploy base '/')", () => {
    expect(withSite()).toBe(SITE_BASE);
    expect(withSite("")).toBe(SITE_BASE);
    expect(withSite("/leads")).toBe(`${SITE_BASE}/leads`);
    expect(withSite("/site/")).toBe(`${SITE_BASE}/site/`);
  });

  it("withStory prefixes the story root", () => {
    expect(withStory()).toBe(STORY_BASE);
    expect(withStory("/water")).toBe(`${STORY_BASE}/water`);
  });
});
