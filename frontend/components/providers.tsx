"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Info, TriangleAlert, X } from "lucide-react";
import { api } from "@/lib/api";
import { clearCache } from "@/lib/useApi";
import { SmoothScroll } from "@/components/SmoothScroll";
import type { Account, ChartStyle } from "@/lib/types";

/* ---------------- Auth ---------------- */
type AuthCtx = {
  user: Account | null;
  loading: boolean;
  signin: (username: string, password: string) => Promise<Account>;
  signup: (username: string, password: string) => Promise<Account>;
  signout: () => Promise<void>;
  refresh: () => Promise<void>;
};
const Auth = createContext<AuthCtx | null>(null);

export function useAuth() {
  const ctx = useContext(Auth);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
}

const USER_CACHE_KEY = "jyotish_cached_user";

function getCachedUser(): Account | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function setCachedUser(u: Account | null) {
  if (typeof window === "undefined") return;
  try {
    if (u && u.username) {
      localStorage.setItem(USER_CACHE_KEY, JSON.stringify(u));
    } else {
      localStorage.removeItem(USER_CACHE_KEY);
    }
  } catch {}
}

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Account | null>(getCachedUser);
  const [loading, setLoading] = useState<boolean>(() => !getCachedUser());

  const refresh = useCallback(async () => {
    try {
      const res = await api<{ user?: Account | null } | Account | null>("/api/auth/me", { retries: 1 });
      const u = res && "user" in res ? res.user ?? null : (res as Account | null);
      const validUser = u && (u as Account).username ? (u as Account) : null;
      setUser(validUser);
      setCachedUser(validUser);
    } catch {
      setUser(null);
      setCachedUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const auth = useCallback(async (kind: "signin" | "signup", username: string, password: string) => {
    const res = await api<{ user?: Account } | Account>(`/api/auth/${kind}`, { method: "POST", body: { username, password } });
    const u = (res && "user" in res ? res.user : res) as Account;
    setUser(u);
    setCachedUser(u);
    return u;
  }, []);

  const signout = useCallback(async () => {
    try { await api("/api/auth/signout", { method: "POST" }); } finally { setUser(null); setCachedUser(null); clearCache(); }
  }, []);

  const value = useMemo<AuthCtx>(() => ({
    user, loading, refresh, signout,
    signin: (u, p) => auth("signin", u, p),
    signup: (u, p) => auth("signup", u, p),
  }), [user, loading, refresh, signout, auth]);

  return <Auth.Provider value={value}>{children}</Auth.Provider>;
}

/* ---------------- Toast ---------------- */
type ToastKind = "success" | "error" | "info";
type ToastItem = { id: number; message: string; kind: ToastKind };
const Toast = createContext<(message: string, kind?: ToastKind) => void>(() => {});
export const useToast = () => useContext(Toast);

function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const seq = useRef(0);
  const push = useCallback((message: string, kind: ToastKind = "info") => {
    const id = ++seq.current;
    setItems((x) => [...x.slice(-3), { id, message, kind }]);
    setTimeout(() => setItems((x) => x.filter((t) => t.id !== id)), kind === "error" ? 7000 : 4200);
  }, []);
  const Icon = { success: CheckCircle2, error: TriangleAlert, info: Info };
  return (
    <Toast.Provider value={push}>
      {children}
      <div className="toast-stack" role="status" aria-live="polite">
        <AnimatePresence>
          {items.map((t) => {
            const I = Icon[t.kind];
            return (
              <motion.div key={t.id} className={`toast toast-${t.kind}`} initial={{ opacity: 0, y: 16, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, x: 40 }}>
                <I size={16} aria-hidden />
                <span>{t.message}</span>
                <button aria-label="Dismiss notification" onClick={() => setItems((x) => x.filter((y) => y.id !== t.id))}><X size={14} /></button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </Toast.Provider>
  );
}

/* ---------------- Preferences (local) ---------------- */
export type Prefs = { chartStyle: ChartStyle; ayanamsa: string; houseSystem: string; nodeType: string; reduceMotion: boolean };
const DEFAULT_PREFS: Prefs = { chartStyle: "north", ayanamsa: "lahiri", houseSystem: "whole_sign", nodeType: "true", reduceMotion: false };
const PrefCtx = createContext<{ prefs: Prefs; ready: boolean; setPrefs: (p: Partial<Prefs>) => void }>({ prefs: DEFAULT_PREFS, ready: false, setPrefs: () => {} });
export const usePrefs = () => useContext(PrefCtx);

function PrefsProvider({ children }: { children: ReactNode }) {
  const [prefs, set] = useState<Prefs>(DEFAULT_PREFS);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try {
      const raw = localStorage.getItem("jyotish_prefs");
      if (raw) set({ ...DEFAULT_PREFS, ...JSON.parse(raw) });
    } catch {}
    setReady(true);
  }, []);
  const setPrefs = useCallback((p: Partial<Prefs>) => {
    set((cur) => {
      const next = { ...cur, ...p };
      try { localStorage.setItem("jyotish_prefs", JSON.stringify(next)); } catch {}
      return next;
    });
  }, []);
  useEffect(() => { document.documentElement.dataset.reduceMotion = String(prefs.reduceMotion); }, [prefs.reduceMotion]);
  const value = useMemo(() => ({ prefs, ready, setPrefs }), [prefs, ready, setPrefs]);
  return <PrefCtx.Provider value={value}>{children}</PrefCtx.Provider>;
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <PrefsProvider>
      <SmoothScroll>
        <ToastProvider>
          <AuthProvider>{children}</AuthProvider>
        </ToastProvider>
      </SmoothScroll>
    </PrefsProvider>
  );
}
