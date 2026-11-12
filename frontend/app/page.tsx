"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BookOpen, CalendarDays, Gem, Hand, HeartHandshake, Orbit, ScrollText, Sparkles, Star } from "lucide-react";
import { Brand } from "@/components/shell/AppShell";
import ChartSVG from "@/components/chart/ChartSVG";
import { useAuth } from "@/components/providers";

const FEATURES: { icon: typeof Star; title: string; text: string; href: string; soon?: boolean }[] = [
  { icon: Star, title: "Kundli engine", text: "Swiss Ephemeris precision. Lagna to the arc-second, 16 divisional charts, Bhava Chalit, five ayanamsas.", href: "/kundli" },
  { icon: Orbit, title: "Vimshottari dasha", text: "Mahadasha to Sookshma, the running period highlighted, interpretations tied to your chart.", href: "/kundli" },
  { icon: Sparkles, title: "Yogas & doshas", text: "44 classical yoga rules, Manglik, Kaal Sarp, Pitra and Sade Sati with cancellations and remedies.", href: "/kundli" },
  { icon: Gem, title: "Strength & remedies", text: "Shadbala, Bhinna- and Sarvashtakavarga, functional-benefic-aware gemstone guidance.", href: "/kundli" },
  { icon: HeartHandshake, title: "Kundli matching", text: "36-point Ashtakoota with Nadi and Bhakoot cancellations and Manglik compatibility.", href: "", soon: true },
  { icon: CalendarDays, title: "Panchang & Muhurta", text: "Tithi, nakshatra, yoga, karana, Rahu Kaal and auspicious windows for any city.", href: "", soon: true },
  { icon: Hand, title: "Palm reading", text: "Camera-guided capture with hand-landmark analysis of lines, mounts and finger ratios.", href: "", soon: true },
  { icon: BookOpen, title: "AI astrologer", text: "Ask questions grounded in your verified chart — never invented positions.", href: "/assistant" },
];

const DEMO = [
  { name: "Sun", sign_index: 3 }, { name: "Moon", sign_index: 1 }, { name: "Mars", sign_index: 0 }, { name: "Mercury", sign_index: 4 },
  { name: "Jupiter", sign_index: 3 }, { name: "Venus", sign_index: 3 }, { name: "Saturn", sign_index: 8 }, { name: "Rahu", sign_index: 9 }, { name: "Ketu", sign_index: 3 },
];

export default function Landing() {
  const { user } = useAuth();
  return (
    <div className="landing">
      <header className="land-nav">
        <Brand />
        <nav aria-label="Main">
          <Link href="/learn">Learn</Link>
          <Link href="/kundli">Free Kundli</Link>
          {user ? <Link href="/dashboard" className="btn btn-gold btn-sm">Dashboard</Link> : <Link href="/signin" className="btn btn-ghost btn-sm">Sign in</Link>}
        </nav>
      </header>

      <section className="hero">
        <motion.div className="hero-copy" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}>
          <p className="eyebrow">Jyotish · Sidereal · Swiss Ephemeris</p>
          <h1 className="hero-title">The sky at your first breath, <em>read with precision.</em></h1>
          <p className="lede">A complete Vedic astrology studio — birth charts, dashas, yogas, strengths, transits and matching — calculated, not guessed.</p>
          <div className="hero-cta">
            <Link href="/kundli" className="btn btn-gold btn-lg">Create your Kundli <ArrowRight size={17} /></Link>
            {!user && <Link href="/signin?mode=signup" className="btn btn-ghost btn-lg">Create free account</Link>}
          </div>
          <ul className="hero-proof" aria-label="Highlights">
            <li><b>16</b> divisional charts</li><li><b>44</b> yoga rules</li><li><b>4</b> dasha levels</li>
          </ul>
        </motion.div>
        <motion.div className="hero-chart" initial={{ opacity: 0, scale: 0.92, rotate: -3 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} transition={{ duration: 1.1, delay: 0.2 }}>
          <div className="halo" aria-hidden />
          <ChartSVG style="north" ascSign={6} bodies={DEMO} title="Sample chart" />
        </motion.div>
      </section>

      <section className="feature-wrap" aria-labelledby="features">
        <p className="eyebrow">Everything in one observatory</p>
        <h2 id="features" className="section-title">Built like an instrument, <em>not a horoscope column.</em></h2>
        <div className="feature-grid">
          {FEATURES.map(({ icon: Icon, title, text, href, soon }, i) => (
            <motion.div key={title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-60px" }} transition={{ delay: (i % 4) * 0.07 }}>
              {soon ? (
                <div className="glass feature soon"><span className="feature-icon"><Icon size={20} aria-hidden /></span><h3>{title} <span className="pill pill-gold">Soon</span></h3><p>{text}</p></div>
              ) : (
                <Link href={href} className="glass feature"><span className="feature-icon"><Icon size={20} aria-hidden /></span><h3>{title}</h3><p>{text}</p></Link>
              )}
            </motion.div>
          ))}
        </div>
      </section>

      <section className="cta-band glass">
        <ScrollText size={26} aria-hidden />
        <h2 className="section-title">Your chart is waiting.</h2>
        <p className="lede">Free to calculate. Sign in to save profiles, keep reading history and chat with the AI astrologer.</p>
        <Link href="/kundli" className="btn btn-gold btn-lg">Begin <ArrowRight size={17} /></Link>
      </section>

      <footer className="land-foot">© {new Date().getFullYear()} Jyotish Studio · Calculations by Swiss Ephemeris · For guidance and reflection, not certainty.</footer>
    </div>
  );
}
