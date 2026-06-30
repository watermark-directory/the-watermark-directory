// Unsubscribe token generation + verification for CAN-SPAM / GDPR one-click opt-out (#939 E2).
// Token format (dot-separated, all base64url-encoded components):
//   <sub>.<category>.<exp>.<sig>
// where:
//   sub      — the Cognito sub of the user to unsubscribe
//   category — the notification category to remove
//   exp      — Unix timestamp (seconds) when the token expires (30-day TTL)
//   sig      — HMAC-SHA-256 over "<sub>|<category>|<exp>" keyed by UNSUB_SECRET
//
// No login required — the signed token is the credential.
// The same UNSUB_SECRET is shared between the Lambda (email sender) and the
// Pages Function (verifier) via separate environment variables on each side.

const TOKEN_TTL_SEC = 30 * 24 * 60 * 60; // 30 days

function base64urlEncode(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  let s = "";
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

function base64urlDecode(s: string): Uint8Array<ArrayBuffer> {
  const padded = s.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(padded);
  const out = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) out[i] = binary.charCodeAt(i);
  return out;
}

async function signMessage(secret: string, message: string): Promise<string> {
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret).buffer as ArrayBuffer,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", keyMaterial, new TextEncoder().encode(message));
  return base64urlEncode(sig);
}

async function verifyMessage(secret: string, message: string, sig: string): Promise<boolean> {
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret).buffer as ArrayBuffer,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"],
  );
  try {
    const sigBytes = base64urlDecode(sig);
    return crypto.subtle.verify("HMAC", keyMaterial, sigBytes.buffer, new TextEncoder().encode(message));
  } catch {
    return false;
  }
}

/** Generate a signed unsubscribe token (30-day TTL). */
export async function signUnsubToken(
  sub: string,
  category: string,
  secret: string,
  nowSec = Math.floor(Date.now() / 1000),
): Promise<string> {
  const exp = nowSec + TOKEN_TTL_SEC;
  const message = `${sub}|${category}|${exp}`;
  const sig = await signMessage(secret, message);
  return [
    base64urlEncode(new TextEncoder().encode(sub).buffer as ArrayBuffer),
    base64urlEncode(new TextEncoder().encode(category).buffer as ArrayBuffer),
    String(exp),
    sig,
  ].join(".");
}

/** Verify a token and return `{sub, category}` or `null` when invalid/expired. */
export async function verifyUnsubToken(
  token: string,
  secret: string,
  nowSec = Math.floor(Date.now() / 1000),
): Promise<{ sub: string; category: string } | null> {
  try {
    const parts = token.split(".");
    if (parts.length !== 4) return null;
    const [subB64, catB64, expStr, sig] = parts;

    const sub = new TextDecoder().decode(base64urlDecode(subB64));
    const category = new TextDecoder().decode(base64urlDecode(catB64));
    const exp = Number(expStr);

    if (!sub || !category || !Number.isFinite(exp)) return null;
    if (exp < nowSec) return null; // expired

    const message = `${sub}|${category}|${exp}`;
    const valid = await verifyMessage(secret, message, sig);
    if (!valid) return null;

    return { sub, category };
  } catch {
    return null;
  }
}
