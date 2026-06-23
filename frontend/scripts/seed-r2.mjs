#!/usr/bin/env node
// Seed the LOCAL miniflare R2 bucket that `wrangler pages dev` reads, so /api/doc serves real
// document bytes in the fully-offline dev stack (no Cloudflare creds, no remote bucket).
//
// `wrangler pages dev`'s local R2 can't be filled with `wrangler r2 object put` reliably, but
// wrangler's own getPlatformProxy() opens the SAME miniflare persistence + bucket id (verified:
// it writes the same .wrangler/state/v3/r2 store pages dev uses). So we put objects through it.
// Run this BEFORE pages dev starts — an already-running server won't see new writes (the
// dev-stack orchestrator seeds pre-launch).
//
// What it seeds (in order of precedence):
//   • explicit rels passed as args            → `node scripts/seed-r2.mjs permits/x/y.pdf …`
//   • a whole collection (`--collection <slug>`) → everything under data/documents/<slug>/**
//   • otherwise the PUBLISHED allowlist        → dist/published-documents.json (needs a build)
// Incremental (skips objects already current by size) and LFS-aware (skips unresolved pointers).

import { execSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REPO = resolve(FRONTEND, "..");
const DOCS_DIR = resolve(REPO, "data/documents");
const ALLOWLIST = resolve(FRONTEND, "dist/published-documents.json");

// Content-Type by extension — enough for the corpus; /api/doc reads this off the object so the
// viewer (PDF.js / image / iframe) gets the right type without re-sniffing.
const CONTENT_TYPE = {
  ".pdf": "application/pdf",
  ".html": "text/html",
  ".htm": "text/html",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".tif": "image/tiff",
  ".tiff": "image/tiff",
  ".gif": "image/gif",
  ".txt": "text/plain",
  ".csv": "text/csv",
  ".json": "application/json",
};
const contentType = (rel) => CONTENT_TYPE[extname(rel).toLowerCase()] || "application/octet-stream";

/** LFS pointer files are tiny text blobs starting with this header. */
function isLfsPointer(path) {
  if (statSync(path).size > 1024) return false; // real docs are far larger than a pointer
  return readFileSync(path).subarray(0, 64).toString("utf8").startsWith("version https://git-lfs");
}

/** Every file under a collection dir, as data/documents-relative rels. */
function walkCollection(slug) {
  const rootDir = resolve(DOCS_DIR, slug);
  if (!existsSync(rootDir)) return [];
  const out = [];
  const walk = (dir) => {
    for (const ent of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, ent.name);
      if (ent.isDirectory()) walk(full);
      else if (ent.isFile()) out.push(relative(DOCS_DIR, full));
    }
  };
  walk(rootDir);
  return out;
}

/** Resolve the rel list from argv / --collection / the published allowlist. */
function targetRels() {
  const args = process.argv.slice(2);
  const ci = args.indexOf("--collection");
  if (ci !== -1 && args[ci + 1]) return walkCollection(args[ci + 1]);
  const explicit = args.filter((a) => !a.startsWith("--"));
  if (explicit.length) return explicit;
  if (!existsSync(ALLOWLIST)) {
    console.error(`[seed-r2] ${relative(REPO, ALLOWLIST)} not found — run the build first.`);
    process.exit(1);
  }
  const data = JSON.parse(readFileSync(ALLOWLIST, "utf8"));
  return Array.isArray(data.rels) ? data.rels : [];
}

/** Load getPlatformProxy from the mise-managed wrangler (it's not in node_modules). */
function loadGetPlatformProxy() {
  const root = execSync("mise where npm:wrangler", { cwd: FRONTEND }).toString().trim();
  const entry = `${root}/lib/node_modules/wrangler/wrangler-dist/cli.js`;
  return createRequire(import.meta.url)(entry).getPlatformProxy;
}

const rels = targetRels();
if (rels.length === 0) {
  console.log("[seed-r2] nothing to seed (empty allowlist / collection). Skipping.");
  process.exit(0);
}

const getPlatformProxy = loadGetPlatformProxy();
process.chdir(FRONTEND); // getPlatformProxy reads ./wrangler.toml + ./.wrangler/state
const proxy = await getPlatformProxy();
const bucket = proxy.env.DOCS;
if (!bucket) {
  console.error("[seed-r2] no DOCS R2 binding — is it in wrangler.toml?");
  await proxy.dispose();
  process.exit(1);
}

let put = 0;
let skipped = 0;
let missing = 0;
for (const rel of rels) {
  const path = resolve(DOCS_DIR, rel);
  if (!existsSync(path)) {
    console.warn(`[seed-r2] missing on disk, skipped: ${rel}`);
    missing++;
    continue;
  }
  if (isLfsPointer(path)) {
    console.warn(`[seed-r2] unresolved LFS pointer (run \`git lfs pull\`), skipped: ${rel}`);
    missing++;
    continue;
  }
  const size = statSync(path).size;
  const head = await bucket.head(rel);
  if (head && head.size === size) {
    skipped++;
    continue; // already current
  }
  const ct = contentType(rel);
  await bucket.put(rel, readFileSync(path), {
    httpMetadata: { contentType: ct },
    customMetadata: { "media-type": ct },
  });
  console.log(`[seed-r2] ${rel}  (${(size / 1e6).toFixed(1)} MB, ${ct})`);
  put++;
}
await proxy.dispose();
console.log(`[seed-r2] done — ${put} uploaded, ${skipped} already current, ${missing} missing/LFS.`);
