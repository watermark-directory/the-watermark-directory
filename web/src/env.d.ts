/// <reference types="astro/client" />

interface ImportMetaEnv {
  /**
   * Cloudflare Turnstile site key (public). Set in the host/CI build env once the
   * submissions endpoint is bootstrapped (docs/submissions-api.md). When unset, the
   * submit form (the shared SubmitForm, served at both /submit and /network/american-sugar-creek-allen-co/submit) renders
   * as a disabled placeholder — so the form's enabled state tracks whether the endpoint
   * is actually live.
   */
  readonly PUBLIC_TURNSTILE_SITE_KEY?: string;
  /**
   * Cognito Hosted UI domain (public — not a secret). Set in the CI build env when
   * AUTH_ENABLED="true". e.g. "auth.watermarkdirectory.org" or the Cognito-provided
   * "{prefix}.auth.{region}.amazoncognito.com". Unset → account pages degrade to a
   * disabled placeholder (same pattern as Turnstile above).
   */
  readonly PUBLIC_COGNITO_DOMAIN?: string;
  /**
   * Cognito app client ID (public). Identifies the app client in PKCE authorize requests.
   */
  readonly PUBLIC_COGNITO_CLIENT_ID?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare namespace App {
  /**
   * Per-request locals. `site` is the active network site's registry slug — the seam the
   * multi-site build (#724) routes on. Set by `src/middleware.ts`; today always `"lima"`
   * (the only rendered site), later resolved from the `[site]` route param (#734). Pages
   * that render a known site pass it explicitly to `siteHref(slug, …)`.
   */
  interface Locals {
    site: string;
  }
}
