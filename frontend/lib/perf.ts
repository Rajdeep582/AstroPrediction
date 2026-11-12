/** Device capability tier, decided once on the client. "low" disables heavy effects. */
export type PerfTier = "high" | "low";

export function detectPerfTier(): PerfTier {
  if (typeof window === "undefined") return "high";
  try {
    const forced = localStorage.getItem("jyotish_perf");
    if (forced === "low" || forced === "high") return forced;
  } catch {}
  const nav = navigator as Navigator & { deviceMemory?: number; connection?: { saveData?: boolean } };
  const cores = nav.hardwareConcurrency || 4;
  const mem = nav.deviceMemory ?? 8;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const small = window.innerWidth < 768 && cores <= 6;
  return reduce || nav.connection?.saveData || cores <= 4 || mem <= 4 || small ? "low" : "high";
}

/** Inline script run before paint so the first frame already uses the right tier (no flash/jank). */
export const PERF_BOOT_SCRIPT = `(function(){try{var f=localStorage.getItem("jyotish_perf");var n=navigator,c=n.hardwareConcurrency||4,m=n.deviceMemory||8,r=matchMedia("(prefers-reduced-motion: reduce)").matches,s=n.connection&&n.connection.saveData,sm=innerWidth<768&&c<=6;document.documentElement.dataset.perf=f||((r||s||c<=4||m<=4||sm)?"low":"high")}catch(e){document.documentElement.dataset.perf="high"}})();`;
