"use client";

import { useMemo } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowUpRight, BookOpen, CalendarDays, Clock, FileText, Moon, Orbit, Sparkles, Star, Sun, UsersRound } from "lucide-react";
import { Card, Empty, Pill, RequireAuth, ScoreRing, Skeleton } from "@/components/ui";
import { useAuth } from "@/components/providers";
import { useApi } from "@/lib/useApi";
import { PLANET_GLYPH, SIGNS, fmtDate, type Chart, type Profile, type SavedChart, type Transits } from "@/lib/types";

type Panchang = { vara: string; sunrise: string; sunset: string; tithi: { name: string; paksha: string; ends: string }; nakshatra: { name: string; ends: string }; yoga: { name: string }; karana: { name: string }; rahu_kaal: { start: string; end: string }; abhijit_muhurta: { start: string; end: string } | null; lunar_month_amanta: string; moon_sign: string };

function greeting() {
  const h = new Date().getHours();
  return h < 5 ? "Good night" : h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
}

function Dash() {
  const { user } = useAuth();
  const { data: history } = useApi<SavedChart[]>("/api/kundli/history");
  const { data: profiles = [] } = useApi<Profile[]>("/api/profiles");
  const { data: panchang } = useApi<Panchang>("/api/panchang?lat=22.5726&lon=88.3639&tz=Asia%2FKolkata");
  const latest = useMemo(() => history?.find((h) => (h.calculation as { full?: boolean }).full) ?? null, [history]);
  const { data: chart } = useApi<Chart>(latest ? `/api/kundli/records/${latest.record_id}` : null);
  const moonSign = chart?.planets.find((p) => p.name === "Moon")?.sign_index;
  const { data: transits } = useApi<Transits>(chart && moonSign !== undefined ? `/api/transits?moon_sign=${moonSign}&ayanamsa=${chart.settings.ayanamsa}` : null);
  const histLoading = history === undefined;

  const cur = chart?.dasha.current ?? [];
  const md = cur[0], ad = cur[1];
  const progress = md ? Math.min(100, Math.max(0, ((Date.now() - +new Date(md.start)) / (+new Date(md.end) - +new Date(md.start))) * 100)) : 0;

  const MODULES = [
    { href: "/kundli", icon: Star, title: "New Kundli", text: "Calculate a full chart" },
    { href: "/profiles", icon: UsersRound, title: "Profiles", text: `${profiles.length} saved` },
    { href: "/reports", icon: FileText, title: "Readings", text: `${history?.length ?? "…"} saved` },
    { href: "/assistant", icon: Sparkles, title: "AI Astrologer", text: "Ask about your chart" },
    { href: "/learn", icon: BookOpen, title: "Learn", text: "Concepts & glossary" },
  ];

  return (
    <div className="stack-lg">
      <header className="dash-hero">
        <div>
          <p className="eyebrow">{new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}</p>
          <h1 className="display">{greeting()}, <em>{user?.username}</em></h1>
          {chart && <p className="lede">{chart.ascendant.sign} rising · Moon in {chart.moon_sign} · {chart.birth_nakshatra.name} nakshatra{latest ? ` — ${latest.profile_name}` : ""}</p>}
        </div>
        <Link href="/kundli" className="btn btn-gold"><Star size={16} /> New chart</Link>
      </header>

      <div className="dash-grid">
        <Card className="dasha-card span-2" title={<><Orbit size={18} aria-hidden /> Current dasha</>} sub={latest ? `For ${latest.profile_name}` : undefined}>
          {histLoading || (latest && !chart) ? <Skeleton h={110} /> : md ? (
            <div className="dasha-now">
              <div className="dasha-big"><span className="glyph xl">{PLANET_GLYPH[md.lord]}</span><div><strong>{md.lord} Mahadasha</strong><small>{fmtDate(md.start)} → {fmtDate(md.end)}</small></div></div>
              <div className="bar" aria-label={`Mahadasha ${Math.round(progress)}% elapsed`}><motion.i initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ duration: 1.2 }} /></div>
              <div className="chips">{cur.slice(1).map((c, i) => <span key={i} className="chip on">{["Antar", "Pratyantar", "Sookshma"][i]}: {c.lord} · to {fmtDate(c.end)}</span>)}</div>
              {ad && <p className="body-sm">{chart?.dasha.mahadashas.find((m) => m.current)?.children?.find((c) => c.current)?.interpretation}</p>}
            </div>
          ) : <Empty icon={<Orbit />} title="No chart yet"><Link href="/kundli" className="btn btn-ghost btn-sm">Calculate your Kundli</Link></Empty>}
        </Card>

        <Card title={<><CalendarDays size={18} aria-hidden /> Today&apos;s Panchang</>} sub="Kolkata reference">
          {panchang ? (
            <dl className="kv kv-tight">
              <dt>Vara</dt><dd>{panchang.vara}</dd>
              <dt>Tithi</dt><dd>{panchang.tithi.paksha} {panchang.tithi.name} <small className="muted">till {panchang.tithi.ends}</small></dd>
              <dt>Nakshatra</dt><dd>{panchang.nakshatra.name} <small className="muted">till {panchang.nakshatra.ends}</small></dd>
              <dt>Yoga · Karana</dt><dd>{panchang.yoga.name} · {panchang.karana.name}</dd>
              <dt><Sun size={13} /> Sun</dt><dd>{panchang.sunrise} – {panchang.sunset}</dd>
              <dt>Rahu Kaal</dt><dd className="warn-text">{panchang.rahu_kaal.start} – {panchang.rahu_kaal.end}</dd>
              {panchang.abhijit_muhurta && <><dt>Abhijit</dt><dd className="good-text">{panchang.abhijit_muhurta.start} – {panchang.abhijit_muhurta.end}</dd></>}
            </dl>
          ) : <SkeletonLines />}
        </Card>

        <Card className="span-2" title={<><Moon size={18} aria-hidden /> Transit snapshot</>} sub={transits ? `From natal Moon in ${transits.reference_moon_sign}` : "Needs a saved chart"} action={transits && <ScoreRing value={transits.score} size={56} label="Transit score" />}>
          {transits ? (
            <div className="transit-strip">
              {transits.planets.map((p) => (
                <div key={p.name} className={`tchip ${p.favourable ? "fav" : "unfav"}`} title={p.effect}>
                  <span className="glyph">{PLANET_GLYPH[p.name]}</span><b>{p.name}</b><small>{p.sign.slice(0, 3)} · H{p.house_from_moon}{p.retrograde ? " ℞" : ""}</small>
                </div>
              ))}
            </div>
          ) : chart ? <SkeletonLines /> : <p className="muted">Calculate and save a chart to see live transits against it.</p>}
        </Card>

        <Card title={<><Clock size={18} aria-hidden /> Recent readings</>} action={<Link href="/reports" className="link-sm">All <ArrowUpRight size={13} /></Link>}>
          {!history ? <SkeletonLines /> : history.length === 0 ? <p className="muted">No saved readings yet.</p> : (
            <ul className="recent">
              {history.slice(0, 5).map((h) => (
                <li key={h.record_id}><Link href={`/kundli/analysis?record=${h.record_id}`}><b>{h.profile_name}</b><small>{h.calculation.ascendant?.sign} Lagna · {fmtDate(h.created_at)}</small></Link></li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <section aria-labelledby="mods">
        <h2 id="mods" className="section-title sm">Quick access</h2>
        <div className="module-grid">
          {MODULES.map(({ href, icon: Icon, title, text }, i) => (
            <motion.div key={href} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.05 }}>
              <Link href={href} className="glass module"><Icon size={20} aria-hidden /><b>{title}</b><small>{text}</small><ArrowUpRight size={15} className="mod-arrow" aria-hidden /></Link>
            </motion.div>
          ))}
        </div>
      </section>
      {chart && <p className="fine">Lagna {SIGNS[chart.ascendant.sign_index]} · {chart.yogas.filter((y) => y.present).length} yogas · {chart.doshas.filter((d) => d.present).map((d) => <Pill key={d.name} tone="warn">{d.name}</Pill>)}</p>}
    </div>
  );
}

function SkeletonLines() {
  return <div className="stack-sm">{[80, 65, 90, 55].map((w) => <Skeleton key={w} w={`${w}%`} />)}</div>;
}

export default function DashboardPage() {
  return <RequireAuth><Dash /></RequireAuth>;
}
