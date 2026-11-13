"use client";

import { createContext, Suspense, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import Lenis from "lenis";
import { usePrefs } from "@/components/providers";

const LenisCtx = createContext<Lenis | null>(null);
export const useLenis = () => useContext(LenisCtx);

/** Scroll to element/offset via Lenis when active, native otherwise. */
export function useScrollTo() {
  const lenis = useLenis();
  return useCallback((target: HTMLElement | number, offset = -24) => {
    if (lenis) lenis.scrollTo(target, { offset, duration: 0.45, easing: (t) => 1 - Math.pow(1 - t, 4) });
    else if (typeof target === "number") window.scrollTo({ top: target, behavior: "smooth" });
    else target.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [lenis]);
}

export function SmoothScroll({ children }: { children: ReactNode }) {
  const { prefs } = usePrefs();
  const [lenis, setLenis] = useState<Lenis | null>(null);

  useEffect(() => {
    // native scrolling is smoother than JS smoothing on low-end devices
    const reduce = prefs.reduceMotion || document.documentElement.dataset.perf === "low" || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    // lerp-based smoothing responds instantly and settles fast; touch stays native (best on phones)
    const l = new Lenis({ lerp: 0.2, smoothWheel: true, wheelMultiplier: 1, syncTouch: false, touchMultiplier: 1 });
    let raf = 0;
    const loop = (t: number) => { l.raf(t); raf = requestAnimationFrame(loop); };
    raf = requestAnimationFrame(loop);
    setLenis(l);
    // keep Lenis' idea of the page height in sync with real content (route changes, expanding cards, images)
    const ro = new ResizeObserver(() => l.resize());
    ro.observe(document.body);
    return () => { ro.disconnect(); cancelAnimationFrame(raf); l.destroy(); setLenis(null); };
  }, [prefs.reduceMotion]);

  // Cheap scrolling flag (a JS variable, not a class: toggling a root class restyles the whole page).
  useEffect(() => {
    const w = window as Window & { __scrolling?: boolean };
    let t: ReturnType<typeof setTimeout> | undefined;
    const on = () => { w.__scrolling = true; clearTimeout(t); t = setTimeout(() => { w.__scrolling = false; }, 140); };
    window.addEventListener("scroll", on, { passive: true });
    return () => { window.removeEventListener("scroll", on); clearTimeout(t); w.__scrolling = false; };
  }, []);

  return <LenisCtx.Provider value={lenis}>{children}<Suspense fallback={null}><RouteEffects lenis={lenis} /></Suspense></LenisCtx.Provider>;
}

/** Scroll reset + top progress bar on navigation. */
function RouteEffects({ lenis }: { lenis: Lenis | null }) {
  const path = usePathname();
  const search = useSearchParams();
  const [state, setState] = useState<"idle" | "loading" | "done">("idle");
  const first = useRef(true);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  // start bar on internal link click
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const a = (e.target as HTMLElement).closest("a");
      if (!a || a.target === "_blank" || a.hasAttribute("download")) return;
      const url = new URL(a.href, location.href);
      if (url.origin !== location.origin) return;
      if (url.pathname === location.pathname && url.search === location.search) return;
      setState("loading");
    };
    document.addEventListener("click", onClick, true);
    return () => document.removeEventListener("click", onClick, true);
  }, []);

  // Remember scroll position per page. Going back to the previous page restores it; new pages start at the top.
  const positions = useRef(new Map<string, number>());
  const stack = useRef<string[]>([]);
  const lastKey = useRef("");
  const navigating = useRef(false);
  useEffect(() => {
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
    // a Map write per scroll event is negligible; no frame-throttling needed
    const onScroll = () => { if (lastKey.current && !navigating.current) positions.current.set(lastKey.current, window.scrollY); };
    // while a page swap is in progress the browser emits scroll events for the outgoing page — ignore them
    const freeze = (e: Event) => {
      if (e.type === "click") {
        if (!(e.target as HTMLElement).closest?.("a[href]")) return;
        if (lastKey.current) positions.current.set(lastKey.current, window.scrollY); // exact spot at the moment of leaving
      }
      navigating.current = true;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    document.addEventListener("click", freeze, true);
    window.addEventListener("popstate", freeze, true);
    return () => { window.removeEventListener("scroll", onScroll); document.removeEventListener("click", freeze, true); window.removeEventListener("popstate", freeze, true); };
  }, []);

  useEffect(() => {
    const key = path + "?" + search.toString();
    const prev = lastKey.current;
    lastKey.current = key;
    const st = stack.current;
    const isBack = st.length >= 2 && st[st.length - 2] === key;
    if (isBack) st.pop(); else if (st[st.length - 1] !== key) st.push(key);
    if (st.length > 50) st.shift();
    const unfreeze = () => setTimeout(() => { navigating.current = false; }, 700);
    if (first.current) { first.current = false; unfreeze(); return; }
    if (prev === key) { unfreeze(); return; }
    unfreeze();
    const target = isBack ? positions.current.get(key) ?? 0 : 0;
    const go = (y: number) => { if (lenis) { lenis.resize(); lenis.scrollTo(y, { immediate: true, force: true }); } else window.scrollTo(0, y); };
    go(target);
    if (target > 0) {
      // the page may still be rendering: retry briefly until it is tall enough to reach the saved spot
      let tries = 0;
      const again = () => { if (Math.abs(window.scrollY - target) > 4 && tries++ < 15) { go(target); setTimeout(again, 40); } };
      setTimeout(again, 30);
    }
    setState("done");
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setState("idle"), 380);
    document.getElementById("main")?.focus({ preventScroll: true });
  }, [path, search, lenis]);

  return <div className={`route-bar ${state}`} aria-hidden />;
}
