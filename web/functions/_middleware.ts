/**
 * Global Pages Function middleware — pre-launch gate (deploy/features.yaml `preLaunch`).
 *
 * When PRE_LAUNCH_ENABLED=true:
 *   GET /                      → rewrite to /pre-launch (URL stays /; no redirect)
 *   GET /<any non-asset route> → 302 redirect to /
 *   /api/* and static assets   → pass through unchanged
 *
 * All other requests pass straight through to the static Astro output or the
 * api/* Pages Functions.
 */

interface Env {
    /** Written by `pulumi up` from deploy/features.yaml `preLaunch`. */
    PRE_LAUNCH_ENABLED?: string;
    /** Cloudflare Pages asset-serving binding — always available in Pages Functions. */
    ASSETS: { fetch(req: Request | string, init?: RequestInit): Promise<Response> };
}

type PagesFunction = (context: {
    request: Request;
    env: Env;
    next: () => Promise<Response>;
}) => Promise<Response>;

export const onRequest: PagesFunction = async ({ request, env, next }) => {
    if (env.PRE_LAUNCH_ENABLED !== "true") {
        return next();
    }

    const url = new URL(request.url);
    const { pathname } = url;

    // Pass through: API routes and anything with a file extension (assets, fonts, etc.)
    if (pathname.startsWith("/api/") || /\.[a-zA-Z0-9]+$/.test(pathname)) {
        return next();
    }

    // / → serve the pre-launch page content (rewrite; URL stays /)
    if (pathname === "/" || pathname === "") {
        return env.ASSETS.fetch(new URL("/pre-launch", request.url).toString());
    }

    // Every other non-asset route → redirect to / so the pre-launch page is the only exit
    return Response.redirect(new URL("/", request.url).toString(), 302);
};
