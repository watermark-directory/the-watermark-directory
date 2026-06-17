import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

const tmpDirs: string[] = [];

function manifestWith(feeds: object[], contractVersion = "1.4"): object {
  return {
    bundle_version: "test",
    contract_version: contractVersion,
    generated_at: "2026-01-01T00:00:00Z",
    feed_count: feeds.length,
    row_total: 0,
    feeds,
  };
}

function makeBundle(manifest: object, files: Record<string, string>): string {
  const dir = mkdtempSync(join(tmpdir(), "bosc-bundle-"));
  tmpDirs.push(dir);
  writeFileSync(join(dir, "manifest.json"), JSON.stringify(manifest));
  for (const [name, body] of Object.entries(files)) writeFileSync(join(dir, name), body);
  return dir;
}

// bundle.ts memoizes the resolved dir + manifest at module scope, so each case
// points BOSC_BUNDLE_DIR at a fresh fixture and re-imports with a clean registry.
async function loadBundleModule(dir: string): Promise<typeof import("./bundle")> {
  process.env.BOSC_BUNDLE_DIR = dir;
  vi.resetModules();
  return import("./bundle");
}

afterEach(() => {
  delete process.env.BOSC_BUNDLE_DIR;
});
afterAll(() => {
  for (const d of tmpDirs) rmSync(d, { recursive: true, force: true });
});

describe("bundle resolution + JSON feeds", () => {
  it("resolves the explicit BOSC_BUNDLE_DIR override and reads its feeds", async () => {
    const dir = makeBundle(
      manifestWith([
        {
          name: "things",
          path: "things.json",
          media_type: "application/json",
          schema: "s",
          kind: "collection",
          count: 2,
        },
      ]),
      { "things.json": JSON.stringify([{ a: 1 }, { a: 2 }]) },
    );
    const m = await loadBundleModule(dir);

    expect(m.bundleDir()).toBe(dir);
    expect(m.loadManifest().contract_version).toBe("1.4");
    expect(m.hasFeed("things")).toBe(true);
    expect(m.hasFeed("absent")).toBe(false);
    expect(m.loadFeed("things")).toEqual([{ a: 1 }, { a: 2 }]);
  });

  it("throws a helpful error for a feed not in the manifest", async () => {
    const dir = makeBundle(manifestWith([]), {});
    const m = await loadBundleModule(dir);
    expect(() => m.loadFeed("missing")).toThrow(/not in the bundle manifest/);
  });
});

describe("NDJSON feeds", () => {
  it("parses an .ndjson feed line-by-line, skipping blank lines", async () => {
    const dir = makeBundle(
      manifestWith([
        {
          name: "rows",
          path: "rows.ndjson",
          media_type: "application/x-ndjson",
          schema: "s",
          kind: "collection",
          count: 2,
        },
      ]),
      { "rows.ndjson": '{"a":1}\n{"a":2}\n\n' },
    );
    const m = await loadBundleModule(dir);
    expect(m.loadFeed("rows")).toEqual([{ a: 1 }, { a: 2 }]);
  });
});

describe("contract-version guard", () => {
  it("fails fast when the bundle's contract major differs", async () => {
    const dir = makeBundle(manifestWith([], "2.0"), {});
    const m = await loadBundleModule(dir);
    expect(() => m.loadManifest()).toThrow(/incompatible/);
  });

  it("accepts a matching major with a different minor", async () => {
    const dir = makeBundle(manifestWith([], "1.9"), {});
    const m = await loadBundleModule(dir);
    expect(m.loadManifest().contract_version).toBe("1.9");
  });
});
