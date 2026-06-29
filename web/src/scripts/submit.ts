// Client for the submissions form (/submit). Framework-free, in the style of
// search.ts. Takes the Turnstile token the widget injects and POSTs JSON to the
// endpoint. The optional record target comes from the ref-context banner
// (submitRef.ts owns the query-string → banner wiring); reading it from the live
// banner state here means the banner's "clear" button cleanly drops the target.

const form = document.getElementById("submit-form") as HTMLFormElement | null;
const statusEl = document.getElementById("submit-status");

if (form && statusEl) {
  const endpoint = form.dataset.endpoint || "/api/submit";

  const setStatus = (msg: string, kind: "ok" | "err" | "info"): void => {
    statusEl.textContent = msg;
    statusEl.dataset.kind = kind;
  };

  const turnstile = (): { reset: () => void } | undefined =>
    (window as unknown as { turnstile?: { reset: () => void } }).turnstile;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(form);

    const token = String(data.get("cf-turnstile-response") || "");
    if (!token) {
      setStatus("Please complete the verification challenge.", "err");
      return;
    }
    const body = String(data.get("body") || "").trim();
    if (!body) {
      setStatus("Please describe the tip or correction.", "err");
      return;
    }

    const payload: Record<string, unknown> = {
      kind: String(data.get("kind") || "tip"),
      body,
      turnstile_token: token,
      page_url: location.href,
    };
    const evidence = String(data.get("evidence_url") || "").trim();
    if (evidence) payload.evidence_url = evidence;

    // Optional contact (#242) — sent only when filled; routed to a private store, never
    // the public issue (see docs/submissions-api.md).
    const contact = String(data.get("contact") || "").trim();
    if (contact) payload.contact = contact;

    // Record target — read from the live banner (submitRef.ts), so a "cleared"
    // banner means no target is attached.
    const banner = document.getElementById("submit-ref");
    const refKind = banner && !banner.hidden ? banner.dataset.refKind : undefined;
    if (refKind) {
      payload.target = {
        ref_kind: refKind,
        ...(banner?.dataset.refId ? { ref_id: banner.dataset.refId } : {}),
        ...(banner?.dataset.refLabel ? { ref_label: banner.dataset.refLabel } : {}),
      };
    }

    const submitBtn = form.querySelector<HTMLButtonElement>("button[type=submit]");
    if (submitBtn) submitBtn.disabled = true;
    setStatus("Sending…", "info");

    const fetchHeaders: Record<string, string> = { "Content-Type": "application/json" };
    const idToken = sessionStorage.getItem("watermark_id_token");
    if (idToken) fetchHeaders["Authorization"] = `Bearer ${idToken}`;

    void fetch(endpoint, {
      method: "POST",
      headers: fetchHeaders,
      body: JSON.stringify(payload),
    })
      .then(async (r) => {
        const out = (await r.json().catch(() => ({}))) as {
          issue_url?: string;
          error?: string;
          deduped?: boolean;
        };
        if (r.ok && out.issue_url) {
          form.reset();
          const safe = out.issue_url.replace(/"/g, "%22");
          const verb = out.deduped ? "already tracked as" : "filed as";
          statusEl.innerHTML = `Thank you — ${verb} <a href="${safe}">${safe}</a> for review.`;
          statusEl.dataset.kind = "ok";
          return;
        }
        setStatus(out.error ? `Couldn't send: ${out.error}` : "Couldn't send your submission.", "err");
        if (submitBtn) submitBtn.disabled = false;
        turnstile()?.reset(); // a Turnstile token is single-use; reset for a retry
      })
      .catch(() => {
        setStatus("Network error — please try again.", "err");
        if (submitBtn) submitBtn.disabled = false;
        turnstile()?.reset();
      });
  });
}
