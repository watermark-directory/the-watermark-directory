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
