// File attachment pre-upload for the submissions form (#243). Runs alongside submit.ts.
// When the form is submitted and files are selected, this script uploads each file to
// /api/attach before the main payload is sent, then stores the returned keys on the
// form element for submit.ts to read. A per-file status note is shown in #attach-status.
//
// The upload endpoint shares the SUBMISSIONS_ENABLED kill switch — a 503 response means
// attachments aren't configured yet; we surface that and let the user decide whether to
// proceed without the file.

const ATTACH_ENDPOINT = "/api/attach";
const MAX_FILES = 3;

const form = document.getElementById("submit-form") as
  | (HTMLFormElement & { _attachmentKeys?: string[] })
  | null;
const attachInput = document.getElementById("f-attach") as HTMLInputElement | null;
const attachStatus = document.getElementById("attach-status");

if (form && attachInput && attachStatus) {
  // Listen in the capture phase, before submit.ts's bubble-phase handler fires,
  // so we can async pre-upload files and populate form._attachmentKeys first.
  form.addEventListener(
    "submit",
    async (e) => {
      const files = Array.from(attachInput.files ?? []).slice(0, MAX_FILES);
      if (files.length === 0) return; // nothing to upload — let the event proceed normally

      // Prevent submit.ts from seeing this event until uploads finish.
      e.stopImmediatePropagation();
      e.preventDefault();

      attachStatus.textContent = `Uploading ${files.length} file${files.length > 1 ? "s" : ""}…`;

      const keys: string[] = [];
      const failed: string[] = [];

      for (const file of files) {
        const fd = new FormData();
        fd.append("file", file);
        try {
          const res = await fetch(ATTACH_ENDPOINT, { method: "POST", body: fd });
          if (res.ok) {
            const data = (await res.json()) as { key?: string };
            if (data.key) {
              keys.push(data.key);
            } else {
              failed.push(file.name);
            }
          } else {
            const data = (await res.json().catch(() => ({}))) as { error?: string };
            failed.push(`${file.name}${data.error ? ` (${data.error})` : ""}`);
          }
        } catch {
          failed.push(`${file.name} (network error)`);
        }
      }

      form._attachmentKeys = keys;

      if (failed.length > 0) {
        attachStatus.textContent = `Could not upload: ${failed.join(", ")}. Proceed anyway or remove the file.`;
        // Re-submit without the failed files so the user can decide; the keys that did
        // upload are stored. The submit button is re-enabled via the re-dispatch below.
      } else {
        attachStatus.textContent = `${keys.length} file${keys.length > 1 ? "s" : ""} ready.`;
      }

      // Re-dispatch a plain submit event so submit.ts's handler fires next.
      form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    },
    true, // capture phase — runs before submit.ts's bubble-phase listener
  );

  // Client-side validation: warn when too many files are selected (max enforced server-side too).
  attachInput.addEventListener("change", () => {
    const count = attachInput.files?.length ?? 0;
    attachStatus.textContent =
      count > MAX_FILES ? `Select up to ${MAX_FILES} files (${count} selected).` : "";
  });
}

export {};
