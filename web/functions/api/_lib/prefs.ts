// UserPrefs KV helpers (Epic #921 C1/C2).
// Prefs are stored per-user under key `prefs:{sub}` in the AUTH_PREFS KV namespace.
// The notifications.email_verified field reflects the live Cognito JWT claim and is
// synced on every read — it is not user-patchable.

import type { KVLike } from "./ratelimit";

export const VALID_CATEGORIES = ["tip", "correction", "new_source", "hypothesis"] as const;
export type NotifCategory = (typeof VALID_CATEGORIES)[number];

export const VALID_FREQUENCIES = ["immediate", "daily"] as const;
export type NotifFrequency = (typeof VALID_FREQUENCIES)[number];

export interface UserPrefs {
  display_name?: string;
  notifications: {
    sites: string[];
    categories: NotifCategory[];
    frequency: NotifFrequency;
    /** Reflects the Cognito email_verified claim; set on read, never patchable by the user. */
    email_verified: boolean;
  };
}

const DEFAULT_NOTIFICATIONS: UserPrefs["notifications"] = {
  sites: [],
  categories: [],
  frequency: "immediate",
  email_verified: false,
};

function prefsKey(sub: string): string {
  return `prefs:${sub}`;
}

export async function getPrefs(kv: KVLike, sub: string): Promise<UserPrefs> {
  const raw = await kv.get(prefsKey(sub));
  if (!raw) return { notifications: { ...DEFAULT_NOTIFICATIONS } };
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return { notifications: { ...DEFAULT_NOTIFICATIONS } };
    }
    const p = parsed as Partial<UserPrefs> & { notifications?: Partial<UserPrefs["notifications"]> | null };
    return {
      display_name: typeof p.display_name === "string" ? p.display_name : undefined,
      notifications: {
        ...DEFAULT_NOTIFICATIONS,
        ...(p.notifications && typeof p.notifications === "object" ? p.notifications : {}),
      },
    };
  } catch {
    return { notifications: { ...DEFAULT_NOTIFICATIONS } };
  }
}

export async function putPrefs(kv: KVLike, sub: string, prefs: UserPrefs): Promise<void> {
  await kv.put(prefsKey(sub), JSON.stringify(prefs));
}
