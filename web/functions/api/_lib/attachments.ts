// MIME validation, magic-byte sniffing, filename sanitization, and R2 helper types
// for the submission file-attach endpoint (#243). Pure and dependency-free so these
// helpers are testable without a Workers runtime.

/** Minimal slice of the Workers R2 API we use. */
export interface R2Like {
  put(
    key: string,
    value: ArrayBuffer | ArrayBufferView | ReadableStream | string,
    options?: { httpMetadata?: { contentType?: string; contentDisposition?: string } },
  ): Promise<unknown>;
  head(key: string): Promise<{ size?: number } | null>;
}

export const ATTACH_MIME_ALLOWLIST = [
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp",
  "application/pdf",
  "text/plain",
] as const satisfies readonly string[];

export const ATTACH_MAX_BYTES = 10 * 1024 * 1024; // 10 MB per file
export const ATTACH_MAX_COUNT = 3; // max files per submission

/**
 * Detect MIME type from magic bytes (first ≤ 12 bytes of the file body).
 * Returns null when the signature is unknown — not an error; callers treat
 * null specially for text/plain (no magic bytes).
 */
export function detectMime(bytes: Uint8Array): string | null {
  if (bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return "image/jpeg";
  if (bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47) return "image/png";
  if (bytes[0] === 0x47 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x38) return "image/gif";
  // WebP: RIFF....WEBP
  if (
    bytes[0] === 0x52 &&
    bytes[1] === 0x49 &&
    bytes[2] === 0x46 &&
    bytes[3] === 0x46 &&
    bytes[8] === 0x57 &&
    bytes[9] === 0x45 &&
    bytes[10] === 0x42 &&
    bytes[11] === 0x50
  )
    return "image/webp";
  // %PDF
  if (bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46)
    return "application/pdf";
  return null;
}

/**
 * Strip path separators, null bytes, parent-directory sequences; replace leading
 * dots (hidden-file names) and whitespace with underscores; cap length.
 * Never returns an empty string.
 */
export function sanitizeFilename(name: string): string {
  const safe = name
    .replace(/[/\\]/g, "_") // path separators → _
    .replace(/\.\./g, "_") // parent-dir sequences → _
    .replace(/\0/g, "") // null bytes
    .replace(/^\./g, "_") // leading dot (hidden file) → _
    .replace(/\s+/g, "_") // whitespace → _
    .replace(/_+/g, "_") // collapse consecutive underscores
    .slice(0, 100);
  // If everything collapsed to underscores (e.g. all-whitespace input), use fallback.
  return safe.replace(/_/g, "").length > 0 ? safe : "attachment";
}

/** R2 key for a submission attachment: `submissions/{date}/{uuid}/{safe-filename}`. */
export function attachmentKey(isoDate: string, uuid: string, filename: string): string {
  return `submissions/${isoDate}/${uuid}/${sanitizeFilename(filename)}`;
}
