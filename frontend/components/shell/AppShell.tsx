"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { BookOpen, FileText, LayoutDashboard, LogIn, LogOut, MoreHorizontal, Settings2, Sparkles, Star, UsersRound, X } from "lucide-react";
import { useAuth, useToast } from "@/components/providers";
import { prefetch } from "@/lib/useApi";

export const NAV = [
  { href: "/dashboard", label: "Dashboard", short: "Home", icon: LayoutDashboard, data: ["/api/kundli/history", "/api/profiles"] },
  { href: "/kundli", label: "Kundli", short: "Kundli", icon: Star, data: ["/api/profiles"] },
  { href: "/profiles", label: "Profiles", short: "Profiles", icon: UsersRound, data: ["/api/profiles"] },
  { href: "/reports", label: "Saved Readings", short: "Readings", icon: FileText, data: ["/api/kundli/history"] },
  { href: "/assistant", label: "AI Astrologer", short: "AI", icon: Sparkles, data: ["/api/profiles"] },
  { href: "/learn", label: "Learn", short: "Learn", icon: BookOpen, data: [] },
  { href: "/settings", label: "Settings", short: "Settings", icon: Settings2, data: [] },
];
const MOBILE_MAIN = ["/dashboard", "/kundli", "/reports", "/assistant"];

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link href="/" className="brand" aria-label="Jyotish Studio home">
      <span className="brand-mark" aria-hidden>
        <svg viewBox="0 0 32 32" width="32" height="32"><circle cx="16" cy="16" r="15" fill="none" stroke="currentColor" strokeOpacity=".55" /><path d="M16 4 L18.4 13.6 L28 16 L18.4 18.4 L16 28 L13.6 18.4 L4 16 L13.6 13.6Z" fill="currentColor" /></svg>
      </span>
      {!compact && <span><strong>Jyotish Studio</strong><small>Vedic intelligence</small></span>}
    </Link>
  );
}

export default function AppShell({ children }: { children: ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const { user, signout } = useAuth();
  const toast = useToast();
  const [more, setMore] = useState(false);
  const active = (href: string) => path === href || path.startsWith(`${href}/`);
  const warm = (data: string[]) => { if (user) data.forEach(prefetch); };

  useEffect(() => { setMore(false); }, [path]);
  useEffect(() => {
    if (!more) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMore(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [more]);

  const doSignout = async () => { await signout(); toast("Signed out", "info"); router.push("/"); };

  return (
    <div className="shell">
      <a href="#main" className="skip-link">Skip to content</a>
      <aside className="sidebar" aria-label="Primary">
        <Brand />
        <nav className="nav">
          {NAV.map(({ href, label, icon: Icon, data }) => (
            <Link key={href} href={href} className={`nav-item${active(href) ? " active" : ""}`} aria-current={active(href) ? "page" : undefined} onMouseEnter={() => warm(data)} onFocus={() => warm(data)}>
              {active(href) && <motion.span layoutId="nav-pill" className="nav-pill" transition={{ type: "spring", stiffness: 500, damping: 40 }} />}
              <Icon size={17} aria-hidden /> <span>{label}</span>
            </Link>
          ))}
        </nav>
        <div className="side-foot">
          {user ? (
            <div className="user-chip">
              <span className="avatar" aria-hidden>{user.username.slice(0, 1).toUpperCase()}</span>
              <span className="user-name">{user.username}</span>
              <button className="icon-btn" aria-label="Sign out" onClick={doSignout}><LogOut size={15} /></button>
            </div>
          ) : (
            <Link href={`/signin?next=${encodeURIComponent(path)}`} className="btn btn-gold btn-block"><LogIn size={15} /> Sign in</Link>
          )}
        </div>
      </aside>

      <div className="main-col">
        <header className="mobile-top">
          <Brand />
          {!user && <Link href={`/signin?next=${encodeURIComponent(path)}`} className="btn btn-ghost btn-sm">Sign in</Link>}
        </header>
        <main id="main" className="content" tabIndex={-1}>{children}</main>
      </div>

      <nav className="bottom-nav" aria-label="Mobile">
        {NAV.filter((n) => MOBILE_MAIN.includes(n.href)).map(({ href, short, icon: Icon, data }) => (
          <Link key={href} href={href} className={active(href) ? "active" : ""} aria-current={active(href) ? "page" : undefined} onTouchStart={() => warm(data)}>
            {active(href) && <motion.span layoutId="bnav-pill" className="bnav-pill" transition={{ type: "spring", stiffness: 500, damping: 40 }} />}
            <Icon size={19} aria-hidden /><span>{short}</span>
          </Link>
        ))}
        <button className={more || ["/profiles", "/learn", "/settings"].some(active) ? "active" : ""} aria-expanded={more} aria-controls="more-sheet" onClick={() => setMore(!more)}>
          <MoreHorizontal size={19} aria-hidden /><span>More</span>
        </button>
      </nav>

      <AnimatePresence>
        {more && (
          <>
            <motion.div className="sheet-scrim" onClick={() => setMore(false)} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
            <motion.div id="more-sheet" className="sheet" role="dialog" aria-label="More navigation" initial={{ y: "100%" }} animate={{ y: 0 }} exit={{ y: "100%" }} transition={{ type: "spring", stiffness: 420, damping: 40 }}
              drag="y" dragConstraints={{ top: 0, bottom: 0 }} dragElastic={{ top: 0, bottom: 0.6 }} onDragEnd={(_, i) => { if (i.offset.y > 80 || i.velocity.y > 500) setMore(false); }}>
              <div className="sheet-grip" aria-hidden />
              <div className="row-between"><b className="card-title">Menu</b><button className="icon-btn" aria-label="Close menu" onClick={() => setMore(false)}><X size={16} /></button></div>
              <div className="sheet-grid">
                {NAV.map(({ href, label, icon: Icon }) => (
                  <Link key={href} href={href} className={`sheet-item${active(href) ? " active" : ""}`}><Icon size={20} aria-hidden />{label}</Link>
                ))}
              </div>
              {user ? <button className="btn btn-ghost btn-block" onClick={doSignout}><LogOut size={15} /> Sign out ({user.username})</button>
                : <Link href={`/signin?next=${encodeURIComponent(path)}`} className="btn btn-gold btn-block"><LogIn size={15} /> Sign in</Link>}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
