// Client for the Ask portal (/ask). Framework-free, in the style of search.ts/submit.ts.
// Takes the Turnstile token the widget injects, POSTs the question to /api/ask, and
// renders the grounded answer with inline citation links + a sources list (#212, #213).
// The answer HTML is built by the pure, escaped renderer in lib/askRender.ts.

import { drainSse } from "../../functions/api/_lib/sse";
import { type AskCitation, renderAnswer, renderSources } from "../lib/askRender";

interface AskResponse {
  answer?: string;
  citations?: AskCitation[];
  refused?: boolean;
  error?: string;
}

interface AskDone {
  citations?: AskCitation[];
  refused?: boolean;
}

const form = document.getElementById("ask-form") as HTMLFormElement | null;
const input = document.getElementById("ask-question") as HTMLTextAreaElement | null;
const statusEl = document.getElementById("ask-status");
const answerEl = document.getElementById("ask-answer");
const sourcesEl = document.getElementById("ask-sources");

if (form && input && statusEl && answerEl && sourcesEl) {
  const endpoint = form.dataset.endpoint || "/api/ask";
  const base = form.dataset.base || "/";

  const setStatus = (msg: string, kind: "ok" | "err" | "info" | ""): void => {
    statusEl.textContent = msg;
    statusEl.dataset.kind = kind;
  };

  const turnstile = (): { reset: () => void } | undefined =>
    (window as unknown as { turnstile?: { reset: () => void } }).turnstile;

  // Example-question chips seed the input and submit immediately.
  for (const chip of document.querySelectorAll<HTMLButtonElement>(".ask-example")) {
    chip.addEventListener("click", () => {
      input.value = chip.dataset.q || chip.textContent || "";
      form.requestSubmit();
    });
  }

  const showEmpty = (): void => {
    // Announce the outcome in the live status region too — the answer area isn't a live
    // region, so a screen reader that heard "Searching…" needs this to learn it resolved.
    setStatus("No answer found in the record.", "info");
    sourcesEl.innerHTML = "";
    answerEl.innerHTML =
      '<p class="ask-empty">The record doesn\'t answer that. ' +
      "Try rephrasing, or browse the corpus and timeline directly.</p>";
    answerEl.hidden = false;
  };

  // Final render once the whole answer is in: reconcile [n] markers into links + sources.
  const renderFinal = (answer: string, citations: AskCitation[], refused?: boolean): void => {
    const a = answer.trim();
    if (refused || !a) {
      showEmpty();
      return;
    }
    // Announce completion (same a11y reason as showEmpty) and nudge toward verification.
    setStatus("Answer ready — verify each citation.", "ok");
    answerEl.innerHTML = renderAnswer(a, citations, base);
    sourcesEl.innerHTML = renderSources(citations, base);
    answerEl.hidden = false;
  };

  // Consume the Worker's SSE stream: append text deltas live, reconcile at `done`.
  const consumeStream = async (body: ReadableStream<Uint8Array>): Promise<void> => {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let full = "";
    let started = false; // first delta seen — keep "Searching…" up until tokens flow
    let terminal = false; // a `done` or `error` event was handled
    answerEl.hidden = false;
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const { events, rest } = drainSse(buffer);
      buffer = rest;
      for (const ev of events) {
        if (ev.event === "delta") {
          try {
            full += (JSON.parse(ev.data) as { text?: string }).text ?? "";
          } catch {}
          if (!started) {
            started = true;
            setStatus("", ""); // clear the progress note only once an answer is arriving
          }
          answerEl.textContent = full; // escaped + live; re-rendered with citations at done
        } else if (ev.event === "done") {
          terminal = true;
          let d: AskDone = {};
          try {
            d = JSON.parse(ev.data) as AskDone;
          } catch {}
          renderFinal(full, d.citations ?? [], d.refused);
        } else if (ev.event === "error") {
          terminal = true;
          let msg = "Couldn't answer your question.";
          try {
            msg = (JSON.parse(ev.data) as { error?: string }).error ?? msg;
          } catch {}
          setStatus(`Couldn't answer: ${msg}`, "err");
        }
      }
    }
    // The stream closed without a terminal event (e.g. the connection dropped). Don't leave
    // a half-rendered answer with raw [n] markers: format what arrived and flag it incomplete.
    if (!terminal) {
      const a = full.trim();
      if (a) {
        answerEl.innerHTML = renderAnswer(a, [], base);
        sourcesEl.innerHTML = "";
        answerEl.hidden = false;
        setStatus("The connection ended before the answer finished — it may be incomplete.", "err");
      } else {
        setStatus("The connection ended before any answer arrived. Please try again.", "err");
      }
    }
  };

  const ask = async (question: string, token: string): Promise<void> => {
    let r: Response;
    try {
      r = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify({ question, turnstile_token: token }),
      });
    } catch {
      setStatus("Network error — please try again.", "err");
      return;
    }

    const ct = r.headers.get("content-type") ?? "";
    if (r.ok && ct.includes("text/event-stream") && r.body) {
      await consumeStream(r.body);
      return;
    }
    // JSON path — error responses (gating/rate-limit/turnstile) and the non-stream fallback.
    const out = (await r.json().catch(() => ({}))) as AskResponse;
    if (!r.ok) {
      setStatus(out.error ? `Couldn't answer: ${out.error}` : "Couldn't answer your question.", "err");
      return;
    }
    renderFinal(out.answer ?? "", out.citations ?? [], out.refused);
  };

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (question.length < 3) {
      setStatus("Type a question about the record.", "err");
      return;
    }
    const token = String(new FormData(form).get("cf-turnstile-response") || "");
    if (!token) {
      setStatus("Please complete the verification challenge.", "err");
      return;
    }

    const submitBtn = form.querySelector<HTMLButtonElement>("button[type=submit]");
    if (submitBtn) submitBtn.disabled = true;
    answerEl.hidden = true;
    answerEl.innerHTML = "";
    sourcesEl.innerHTML = "";
    setStatus("Searching the record…", "info");

    void ask(question, token).finally(() => {
      if (submitBtn) submitBtn.disabled = false;
      turnstile()?.reset(); // a Turnstile token is single-use; reset for the next ask
    });
  });
}
