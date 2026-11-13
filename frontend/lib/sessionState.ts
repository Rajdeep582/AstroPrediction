"use client";

import { useCallback, useRef, useState, type SetStateAction } from "react";

/**
 * Page state that survives navigating between pages in one visit (in-memory),
 * but resets on a full page refresh — like a native app session.
 */
const store = new Map<string, unknown>();

export function useSessionState<T>(key: string, init: T | (() => T)) {
  const [value, setValue] = useState<T>(() => {
    if (store.has(key)) return store.get(key) as T;
    const v = typeof init === "function" ? (init as () => T)() : init;
    store.set(key, v);
    return v;
  });
  const keyRef = useRef(key);
  keyRef.current = key;
  const set = useCallback((next: SetStateAction<T>) => {
    setValue((cur) => {
      const v = typeof next === "function" ? (next as (c: T) => T)(cur) : next;
      store.set(keyRef.current, v);
      return v;
    });
  }, []);
  return [value, set] as const;
}

export const hasSessionState = (key: string) => store.has(key);
export function clearSessionState() { store.clear(); }
