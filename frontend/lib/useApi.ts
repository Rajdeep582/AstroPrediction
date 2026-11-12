"use client";

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import { api } from "@/lib/api";

/** Tiny stale-while-revalidate cache: instant re-navigation, background refresh, dedupe. */
type Entry = { data?: unknown; error?: string; ts: number; inflight?: Promise<unknown> };
const store = new Map<string, Entry>();
const subs = new Map<string, Set<() => void>>();
const STALE_MS = 30_000;

function emit(key: string) {
  subs.get(key)?.forEach((fn) => fn());
}

export function fetchKey<T>(key: string, force = false): Promise<T> {
  const e = store.get(key);
  if (e?.inflight) return e.inflight as Promise<T>;
  if (!force && e?.data !== undefined && Date.now() - e.ts < STALE_MS) return Promise.resolve(e.data as T);
  const p = api<T>(key)
    .then((data) => { store.set(key, { data, ts: Date.now() }); emit(key); return data; })
    .catch((err: Error) => { store.set(key, { ...store.get(key), error: err.message, ts: Date.now(), inflight: undefined }); emit(key); throw err; });
  store.set(key, { ...e, ts: e?.ts ?? 0, inflight: p });
  return p;
}

/** Replace cached value (optimistic updates) or drop it. */
export function mutateKey<T>(key: string, update?: T | ((cur: T | undefined) => T)) {
  if (update === undefined) { store.delete(key); emit(key); return; }
  const cur = store.get(key)?.data as T | undefined;
  const data = typeof update === "function" ? (update as (c: T | undefined) => T)(cur) : update;
  store.set(key, { data, ts: Date.now() });
  emit(key);
}

export function invalidate(prefix: string) {
  for (const k of [...store.keys()]) if (k.startsWith(prefix)) { store.set(k, { ...store.get(k)!, ts: 0 }); void fetchKey(k, true).catch(() => {}); }
}

export function prefetch(key: string) { void fetchKey(key).catch(() => {}); }

export function useApi<T>(key: string | null) {
  const subscribe = useCallback((cb: () => void) => {
    if (!key) return () => {};
    if (!subs.has(key)) subs.set(key, new Set());
    subs.get(key)!.add(cb);
    return () => { subs.get(key)?.delete(cb); };
  }, [key]);
  const snap = useSyncExternalStore(subscribe, () => (key ? store.get(key) : undefined), () => undefined);
  const [, force] = useState(0);

  useEffect(() => {
    if (!key) return;
    fetchKey<T>(key).catch(() => {});
    const onFocus = () => { const e = store.get(key); if (!e || Date.now() - e.ts > STALE_MS) fetchKey(key, true).catch(() => {}); };
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [key]);

  return {
    data: snap?.data as T | undefined,
    error: snap?.data === undefined ? snap?.error : undefined,
    loading: !!key && snap?.data === undefined && !snap?.error,
    refreshing: !!snap?.inflight,
    refresh: useCallback(() => { if (key) fetchKey(key, true).catch(() => {}); force((n) => n + 1); }, [key]),
  };
}

export function clearCache() {
  store.clear();
  for (const k of subs.keys()) emit(k);
}
