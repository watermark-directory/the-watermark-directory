// Unit tests for the KV audit log (#937 D3).

import { describe, expect, it } from "vitest";
import {
  writeAuditEntry,
  listAuditEntries,
  type AuditEntry,
  type KVListable,
} from "@fn/api/_lib/audit";

function fakeKV(seed: Record<string, string> = {}): KVListable {
  const store = new Map(Object.entries(seed));
  return {
    get: (k) => Promise.resolve(store.get(k) ?? null),
    put: (k, v) => {
      store.set(k, v);
      return Promise.resolve();
    },
    list: ({ prefix = "", limit = 1000 } = {}) => {
      const keys = Array.from(store.keys())
        .filter((k) => k.startsWith(prefix))
        .sort()
        .slice(0, limit)
        .map((name) => ({ name }));
      return Promise.resolve({ keys, list_complete: true });
    },
  };
}

const BASE_ENTRY: AuditEntry = {
  actor: "actor-sub",
  target: "target-sub",
  action: "set-groups",
  before: ["standard"],
  after: ["admin"],
  at: "2026-06-29T12:00:00.000Z",
};

describe("writeAuditEntry", () => {
  it("stores the entry under audit:role:<target>:<at>", async () => {
    const kv = fakeKV();
    await writeAuditEntry(kv, BASE_ENTRY);
    const raw = await kv.get(`audit:role:${BASE_ENTRY.target}:${BASE_ENTRY.at}`);
    expect(raw).not.toBeNull();
    expect(JSON.parse(raw!)).toMatchObject(BASE_ENTRY);
  });

  it("does not throw when KV.put fails (best-effort)", async () => {
    const kv = fakeKV();
    kv.put = () => Promise.reject(new Error("KV unavailable"));
    await expect(writeAuditEntry(kv, BASE_ENTRY)).resolves.toBeUndefined();
  });
});

describe("listAuditEntries", () => {
  it("returns entries in reverse-chronological order", async () => {
    const kv = fakeKV();
    const a: AuditEntry = { ...BASE_ENTRY, at: "2026-06-29T10:00:00.000Z" };
    const b: AuditEntry = { ...BASE_ENTRY, at: "2026-06-29T12:00:00.000Z" };
    await writeAuditEntry(kv, a);
    await writeAuditEntry(kv, b);

    const entries = await listAuditEntries(kv, "target-sub");
    expect(entries).toHaveLength(2);
    // Reverse-chronological: newest first.
    expect(entries[0].at).toBe("2026-06-29T12:00:00.000Z");
    expect(entries[1].at).toBe("2026-06-29T10:00:00.000Z");
  });

  it("returns empty array when no entries exist", async () => {
    const kv = fakeKV();
    const entries = await listAuditEntries(kv, "no-such-sub");
    expect(entries).toEqual([]);
  });

  it("isolates entries by target sub", async () => {
    const kv = fakeKV();
    await writeAuditEntry(kv, { ...BASE_ENTRY, target: "sub-a" });
    await writeAuditEntry(kv, { ...BASE_ENTRY, target: "sub-b" });

    const forA = await listAuditEntries(kv, "sub-a");
    expect(forA).toHaveLength(1);
    expect(forA[0].target).toBe("sub-a");
  });

  it("skips malformed KV values without throwing", async () => {
    const kv = fakeKV({
      "audit:role:target-sub:2026-06-29T12:00:00.000Z": "{invalid json{{",
    });
    const entries = await listAuditEntries(kv, "target-sub");
    expect(entries).toEqual([]);
  });
});
