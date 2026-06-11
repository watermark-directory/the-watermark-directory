// Server-side Cloudflare Turnstile verification.
// https://developers.cloudflare.com/turnstile/get-started/server-side-validation/

const VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";

export async function verifyTurnstile(
  token: string,
  secret: string,
  remoteip?: string,
): Promise<boolean> {
  const form = new FormData();
  form.append("secret", secret);
  form.append("response", token);
  if (remoteip) form.append("remoteip", remoteip);

  let res: Response;
  try {
    res = await fetch(VERIFY_URL, { method: "POST", body: form });
  } catch {
    return false;
  }
  if (!res.ok) return false;
  const data = (await res.json().catch(() => null)) as { success?: boolean } | null;
  return data?.success === true;
}
