// Auth-gate check for the submit form (Epic #920 B2).
// Reads the ID token from sessionStorage and unhides the form / hides the sign-in prompt
// when a valid, unexpired token is present.  No-ops when the auth gate isn't in this build
// (i.e. when the auth-prompt element is absent or already visible).

const wrapper = document.getElementById("submit-form-wrapper") as HTMLDivElement | null;
const authPrompt = document.getElementById("submit-auth-prompt") as HTMLDivElement | null;

// If either element is missing, or the form isn't gated (wrapper is already visible),
// there is nothing to do — auth is not enabled in this build.
if (wrapper && authPrompt && wrapper.hidden) {
  const token = sessionStorage.getItem("watermark_id_token");
  if (token) {
    try {
      const [, payloadB64] = token.split(".");
      const payload = JSON.parse(atob(payloadB64.replace(/-/g, "+").replace(/_/g, "/"))) as {
        exp?: unknown;
      };
      const now = Math.floor(Date.now() / 1000);
      if (typeof payload.exp === "number" && payload.exp > now) {
        wrapper.hidden = false;
        authPrompt.hidden = true;
      }
    } catch {
      // malformed token — leave the prompt visible
    }
  }
}
