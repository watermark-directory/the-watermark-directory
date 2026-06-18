/// <reference types="astro/client" />

interface ImportMetaEnv {
  /**
   * Cloudflare Turnstile site key (public). Set in the host/CI build env once the
   * submissions endpoint is bootstrapped (docs/submissions-api.md). When unset, the
   * `/bosc/submit` form renders as a disabled placeholder — so the form's enabled state
   * tracks whether the endpoint is actually live.
   */
  readonly PUBLIC_TURNSTILE_SITE_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
