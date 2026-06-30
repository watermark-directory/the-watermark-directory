// Browser RUM — Core Web Vitals + JS errors → /api/rum beacon (Epic #961).
//
// import.meta.env.PUBLIC_RUM_ENABLED is replaced at build time by Vite.
// When not "true", this module body is dead code and web-vitals is not bundled.

import type { Metric } from "web-vitals";

if (import.meta.env.PUBLIC_RUM_ENABLED === "true") {
  const { onLCP, onINP, onCLS, onTTFB, onFCP } = await import("web-vitals");

  function send(data: Record<string, unknown>): void {
    navigator.sendBeacon("/api/rum", new Blob([JSON.stringify(data)], { type: "application/json" }));
  }

  function onMetric(metric: Metric): void {
    const conn = (navigator as Navigator & { connection?: { effectiveType?: string } }).connection;
    send({
      metric: metric.name,
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
      id: metric.id,
      "navigation.type": metric.navigationType,
      "connection.type": conn?.effectiveType ?? "unknown",
      "page.path": location.pathname,
    });
  }

  onLCP(onMetric, { reportAllChanges: false });
  onINP(onMetric, { reportAllChanges: false });
  onCLS(onMetric, { reportAllChanges: false });
  onTTFB(onMetric);
  onFCP(onMetric);

  // JS error capture — cap at 5 per page-load to absorb cascade errors.
  let errorCount = 0;
  const MAX_ERRORS = 5;

  function onError(type: string, event: ErrorEvent | PromiseRejectionEvent): void {
    if (++errorCount > MAX_ERRORS) return;
    const src = (event as ErrorEvent).filename ?? "";
    if (src.startsWith("chrome-extension:") || src.startsWith("moz-extension:")) return;
    const err = ((event as ErrorEvent).error ?? (event as PromiseRejectionEvent).reason) as Error | undefined;
    send({
      metric: "error",
      "error.type": type,
      "error.message": String(err?.message ?? (event as ErrorEvent).message ?? "").slice(0, 500),
      "error.stack": (err?.stack ?? "").slice(0, 2000),
      "error.filename": src.replace(location.origin, ""),
      "error.lineno": (event as ErrorEvent).lineno ?? null,
      "page.path": location.pathname,
    });
  }

  window.addEventListener("error", (e) => onError("uncaught", e));
  window.addEventListener("unhandledrejection", (e) => onError("unhandledrejection", e));
}
