"use client";

import { useEffect, useId, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { useAuth } from "@/components/providers";

export function PageHeader({ eyebrow, title, sub, actions }: { eyebrow?: string; title: ReactNode; sub?: ReactNode; actions?: ReactNode }) {
  return (
    <header className="page-head">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1 className="display">{title}</h1>
        {sub && <p className="lede">{sub}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  );
}

export function Card({ children, className = "", title, sub, action }: { children: ReactNode; className?: string; title?: ReactNode; sub?: ReactNode; action?: ReactNode }) {
  return (
    <section className={`glass ${className}`}>
      {(title || action) && (
        <div className="card-head">
          <div>{title && <h2 className="card-title">{title}</h2>}{sub && <p className="card-sub">{sub}</p>}</div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function Skeleton({ h = 16, w = "100%", r = 8, className = "" }: { h?: number | string; w?: number | string; r?: number; className?: string }) {
  return <span className={`skeleton ${className}`} style={{ height: h, width: w, borderRadius: r }} aria-hidden />;
}

export function SkeletonBlock({ lines = 4 }: { lines?: number }) {
  return <div className="stack-sm" aria-busy="true" aria-label="Loading">{Array.from({ length: lines }, (_, i) => <Skeleton key={i} w={`${90 - i * 12}%`} />)}</div>;
}

export function Empty({ icon, title, children }: { icon?: ReactNode; title: string; children?: ReactNode }) {
  return <div className="empty">{icon}<strong>{title}</strong>{children}</div>;
}

export function Tabs<T extends string>({ tabs, value, onChange, label }: { tabs: { id: T; label: ReactNode }[]; value: T; onChange: (v: T) => void; label: string }) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  const bar = useRef<HTMLDivElement>(null);
  const idx = tabs.findIndex((t) => t.id === value);
  const [edges, setEdges] = useState({ l: false, r: false });
  const measure = () => { const b = bar.current; if (b) setEdges({ l: b.scrollLeft > 4, r: b.scrollLeft + b.clientWidth < b.scrollWidth - 4 }); };
  useEffect(() => {
    const b = bar.current, el = refs.current[idx];
    if (b && el) b.scrollTo({ left: el.offsetLeft - b.clientWidth / 2 + el.offsetWidth / 2, behavior: "smooth" });
  }, [idx]);
  useEffect(() => { measure(); window.addEventListener("resize", measure); return () => window.removeEventListener("resize", measure); }, []);
  const onKey = (e: KeyboardEvent) => {
    const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
    if (!d) return;
    e.preventDefault();
    const n = (idx + d + tabs.length) % tabs.length;
    onChange(tabs[n].id);
    refs.current[n]?.focus();
  };
  return (
    <div className={`tabs-wrap${edges.l ? " fade-l" : ""}${edges.r ? " fade-r" : ""}`}>
    <div ref={bar} className="tabs" role="tablist" aria-label={label} onKeyDown={onKey} onScroll={measure}>
      {tabs.map((t, i) => (
        <button key={t.id} ref={(el) => { refs.current[i] = el; }} role="tab" aria-selected={t.id === value} tabIndex={t.id === value ? 0 : -1} className={`tab${t.id === value ? " active" : ""}`} onClick={() => onChange(t.id)}>
          {t.label}
          {t.id === value && <motion.span layoutId={`tab-ink-${label}`} className="tab-ink" transition={{ type: "spring", stiffness: 520, damping: 42 }} />}
        </button>
      ))}
    </div>
    </div>
  );
}

export function Accordion({ title, meta, children, defaultOpen = false, highlight = false }: { title: ReactNode; meta?: ReactNode; children: ReactNode; defaultOpen?: boolean; highlight?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const id = useId();
  return (
    <div className={`acc${open ? " open" : ""}${highlight ? " hl" : ""}`}>
      <button className="acc-head" aria-expanded={open} aria-controls={id} onClick={() => setOpen(!open)}>
        <span className="acc-title">{title}</span>
        {meta && <span className="acc-meta">{meta}</span>}
        <ChevronDown size={16} className="acc-chev" aria-hidden />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div id={id} className="acc-body" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}>
            <div className="acc-inner">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function ScoreRing({ value, size = 84, label }: { value: number; size?: number; label?: string }) {
  const r = size / 2 - 7;
  const c = 2 * Math.PI * r;
  const tone = value >= 70 ? "var(--good)" : value >= 50 ? "var(--gold)" : "var(--warn)";
  return (
    <div className="score-ring" style={{ width: size, height: size }} role="img" aria-label={`${label ?? "Score"} ${value} out of 100`}>
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={r} stroke="var(--line)" strokeWidth="5" fill="none" />
        <motion.circle cx={size / 2} cy={size / 2} r={r} stroke={tone} strokeWidth="5" fill="none" strokeLinecap="round" strokeDasharray={c}
          initial={{ strokeDashoffset: c }} animate={{ strokeDashoffset: c * (1 - value / 100) }} transition={{ duration: 1.1, ease: "easeOut" }} transform={`rotate(-90 ${size / 2} ${size / 2})`} />
      </svg>
      <span>{value}</span>
    </div>
  );
}

export function Bar({ value, max = 100, label, tone }: { value: number; max?: number; label?: string; tone?: string }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div className="bar" role="meter" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max} aria-label={label}>
      <motion.i style={{ background: tone }} initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 0.9, ease: "easeOut" }} />
    </div>
  );
}

export function Pill({ children, tone = "default" }: { children: ReactNode; tone?: "default" | "good" | "warn" | "bad" | "gold" }) {
  return <span className={`pill pill-${tone}`}>{children}</span>;
}

/** Client guard: redirect to sign-in when no session. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const path = usePathname();
  useEffect(() => {
    if (!loading && !user) router.replace(`/signin?next=${encodeURIComponent(path)}`);
  }, [loading, user, router, path]);
  if (loading || !user) return <div className="stack" style={{ paddingTop: 20 }}><Skeleton h={44} w="45%" /><Skeleton h={160} /><Skeleton h={160} /></div>;
  return <>{children}</>;
}
