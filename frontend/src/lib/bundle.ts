/**
 * Build-time reader for the BOSC content bundle (Epic #53 — the data tier).
 *
 * The bundle is a directory of typed JSON feeds indexed by a `manifest.json`
 * (see `data/site/bundle/README.md`). This module resolves which bundle to read
 * and pulls feeds off disk at build time — Astro page frontmatter runs in Node
 * during `astro build`, so plain `node:fs` is the right tool, not `fetch`.
 *
 * Bundle resolution order (first that has a `manifest.json` wins):
 *   1. $BOSC_BUNDLE_DIR        — explicit override (absolute, or relative to CWD)
 *   2. ../data/site/bundle     — the real bundle, present after `bosc export`
 *   3. ./sample-bundle         — the committed minimal fixture (offline/CI default)
 *
 * The feeds under (2) are git-ignored and only exist once you run `bosc export`;
 * the fixture under (3) is committed so `npm run build` works with zero Python.
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { cwd, env } from "node:process";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = resolve(HERE, "..", "..");

/** A feed's storage shape, mirroring `bosc.site.feeds.FeedKind`. */
export type FeedKind = "collection" | "object" | "geojson";

/** One feed's entry in the manifest index (`bosc.site.feeds.FeedRef`). */
export interface FeedRef {
  name: string;
  path: string;
  media_type: string;
  schema: string;
  kind: FeedKind;
  count: number;
}

/** The bundle index (`bosc.site.feeds.Manifest`). Read this first. */
export interface Manifest {
  bundle_version: string;
  contract_version: string;
  generated_at: string;
  feed_count: number;
  row_total: number;
  feeds: FeedRef[];
}

function candidateDirs(): string[] {
  const dirs: string[] = [];
  const override = env.BOSC_BUNDLE_DIR;
  if (override) dirs.push(isAbsolute(override) ? override : resolve(cwd(), override));
  dirs.push(resolve(FRONTEND_ROOT, "..", "data", "site", "bundle"));
  dirs.push(resolve(FRONTEND_ROOT, "sample-bundle"));
  return dirs;
}

let cachedDir: string | undefined;

/** The resolved bundle root — the first candidate that holds a `manifest.json`. */
export function bundleDir(): string {
  if (cachedDir) return cachedDir;
  for (const dir of candidateDirs()) {
    if (existsSync(join(dir, "manifest.json"))) {
      cachedDir = dir;
      return dir;
    }
  }
  throw new Error(
    `No content bundle found. Set BOSC_BUNDLE_DIR, run \`bosc export\`, or restore ` +
      `frontend/sample-bundle/. Looked in:\n  ${candidateDirs().join("\n  ")}`,
  );
}

let cachedManifest: Manifest | undefined;

/**
 * The bundle `contract_version` major this frontend is built against. A bundle
 * with a different major has breaking schema changes (the `CONTRACT_VERSION`
 * major in `bosc.site.feeds`), so we fail the build fast with a clear message
 * rather than render against an incompatible shape. Bump when adapting the
 * frontend to a new contract major.
 */
export const EXPECTED_CONTRACT_MAJOR = 1;

/** Parse and return the bundle manifest (cached for the build). */
export function loadManifest(): Manifest {
  if (cachedManifest) return cachedManifest;
  const raw = readFileSync(join(bundleDir(), "manifest.json"), "utf-8");
  const manifest = JSON.parse(raw) as Manifest;
  const major = Number.parseInt(String(manifest.contract_version).split(".")[0], 10);
  if (!Number.isFinite(major) || major !== EXPECTED_CONTRACT_MAJOR) {
    throw new Error(
      `Bundle contract_version "${manifest.contract_version}" is incompatible with this ` +
        `frontend (expected major ${EXPECTED_CONTRACT_MAJOR}). Regenerate with a matching ` +
        `\`bosc export\`, or bump EXPECTED_CONTRACT_MAJOR in src/lib/bundle.ts.`,
    );
  }
  cachedManifest = manifest;
  return cachedManifest;
}

/** Whether the resolved bundle exposes a feed by this name. Section pages and the
 * search index guard on this because the committed sample bundle ships a subset. */
export function hasFeed(name: string): boolean {
  return loadManifest().feeds.some((f) => f.name === name);
}

function feedRef(name: string): FeedRef {
  const ref = loadManifest().feeds.find((f) => f.name === name);
  if (!ref) {
    const known = loadManifest()
      .feeds.map((f) => f.name)
      .join(", ");
    throw new Error(`Feed "${name}" is not in the bundle manifest. Available: ${known}`);
  }
  return ref;
}

/**
 * Read one feed by manifest name. `collection`/`geojson` feeds return the parsed
 * array or FeatureCollection; `object` feeds return the single object. NDJSON
 * collections (large feeds, one row per line) are parsed line-by-line. The shape
 * is the caller's responsibility — pass the matching feed type as `T`.
 */
export function loadFeed<T = unknown>(name: string): T {
  const ref = feedRef(name);
  const raw = readFileSync(join(bundleDir(), ref.path), "utf-8");
  if (ref.path.endsWith(".ndjson")) {
    const rows = raw
      .split("\n")
      .filter((line) => line.trim().length > 0)
      .map((line) => JSON.parse(line));
    return rows as T;
  }
  return JSON.parse(raw) as T;
}
