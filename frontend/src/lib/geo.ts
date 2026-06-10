/**
 * Build-time geo feed access (imports the node:fs bundle loader, so this is NOT
 * client-safe — islands use `geoStyle.ts` instead). Reads the typed GeoJSON feeds
 * and merges them for the corridor map endpoint.
 */
import type { FeatureCollection } from "geojson";
import { loadFeed, loadManifest } from "./bundle";
import type { GeoFeature } from "./geoStyle";

/** Manifest names of the geo layer feeds (e.g. "geo/campus"). */
export function geoFeedNames(): string[] {
  return loadManifest()
    .feeds.filter((f) => f.kind === "geojson")
    .map((f) => f.name);
}

/** One geo layer feed as a GeoJSON FeatureCollection. */
export function loadGeo(name: string): FeatureCollection {
  return loadFeed<FeatureCollection>(name);
}

/** All geo feeds merged into one FeatureCollection (the corridor-map source). */
export function mergedGeo(): FeatureCollection {
  const features: GeoFeature[] = [];
  for (const name of geoFeedNames()) {
    const fc = loadGeo(name);
    features.push(...(fc.features as GeoFeature[]));
  }
  return { type: "FeatureCollection", features };
}
