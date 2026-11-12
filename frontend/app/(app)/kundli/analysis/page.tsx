"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { AlertTriangle, ArrowLeft, Calendar, ChevronDown, Clock, Compass, MapPin, Sparkles } from "lucide-react";
import KundliResult from "@/components/kundli/KundliResult";
import { Details, Hl, MoreList, ReadMore } from "@/components/kundli/Readable";
import { Card, Empty, ScoreRing, SkeletonBlock } from "@/components/ui";
import { useAuth, useToast } from "@/components/providers";
import { useScrollTo } from "@/components/SmoothScroll";
import { api } from "@/lib/api";
import { PLANET_GLYPH, fmtDate, type Analysis, type Chart, type ChartStyle, type DashaReading, type LifeEffect } from "@/lib/types";

type Rec = Chart & { profile?: { name?: string; birthplace?: string }; record_id?: string };

const SECTIONS = [
  ["summary", "Summary"], ["chart", "Birth chart"], ["profile", "Lagna & Moon"], ["avakhada", "Birth details"],
  ["planets", "Planets"], ["dasha", "Dasha periods"], ["houses", "Houses"], ["yogas", "Yogas & doshas"], ["remedies", "Remedies"], ["method", "Method"],
] as const;

const ToneTag = ({ tone }: { tone: string }) => <span className={`tone t-${tone}`}>{tone}</span>;
const toneOf = (s: number) => (s >= 75 ? "excellent" : s >= 60 ? "favourable" : s >= 45 ? "mixed" : "challenging");
function Score({ value, label }: { value: number; label?: string }) {
  const t = toneOf(value);
  return (
    <div className={`score t-${t}`}>
      {label && <div className="row-between small"><span className="muted">{label}</span><b style={{ color: "var(--t)" }}>{value}/100</b></div>}
      <div className="score-bar" role="meter" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100} aria-label={label ?? "Score"}><i style={{ width: `${value}%` }} /></div>
    </div>
  );
}
const ord = (n: number) => (n === 1 ? "1st" : n === 2 ? "2nd" : n === 3 ? "3rd" : `${n}th`);

function useActiveSection() {
  const [active, setActive] = useState<string>("summary");
  useEffect(() => {
    let raf = 0;
    const update = () => {
      raf = 0;
      const line = window.innerHeight * 0.3;
      let cur: string = SECTIONS[0][0];
      for (const [id] of SECTIONS) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top <= line) cur = id;
      }
      setActive((a) => (a === cur ? a : cur));
    };
    const onScroll = () => { if (!raf) raf = requestAnimationFrame(update); };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => { window.removeEventListener("scroll", onScroll); cancelAnimationFrame(raf); };
  }, []);
  return active;
}

function Section({ id, n, title, lead, children }: { id: string; n: number; title: string; lead?: string; children: React.ReactNode }) {
  return (
    <section id={id} className="an-sec">
      <header><p className="eyebrow">{String(n).padStart(2, "0")} · {SECTIONS[n - 1][1]}</p><h2>{title}</h2>{lead && <p className="an-lead">{lead}</p>}</header>
      {children}
    </section>
  );
}

function DashaTimeline({ dashas, profiles }: { dashas: DashaReading[]; profiles?: Record<string, { label: string; value: string }[]> }) {
  const cur = dashas.findIndex((d) => d.current);
  const [sel, setSel] = useState(cur >= 0 ? cur : 0);
  const total = dashas.reduce((s, d) => s + (d.age_to - d.age_from), 0);
  const d = dashas[sel];
  return (
    <>
      <div className="dt" role="tablist" aria-label="Mahadasha timeline">
        {dashas.map((x, i) => (
          <button key={x.lord + x.start} role="tab" aria-selected={i === sel} className={`t-${x.tone}${i === sel ? " sel" : ""}${x.current ? " cur" : ""}`}
            style={{ flex: `${Math.max(x.age_to - x.age_from, 1.5) / total}` }} onClick={() => setSel(i)} title={`${x.lord}: age ${x.age_from}–${x.age_to}`}>
            <span>{PLANET_GLYPH[x.lord]} {x.age_to - x.age_from > 6 ? x.lord : ""}</span>
          </button>
        ))}
      </div>
      <div className="dt-axis"><span>Birth</span><span>Age {Math.round(dashas[dashas.length - 1].age_to)}</span></div>
      <motion.div key={sel} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}
        className={`an-card t-${d.tone}${d.current ? " cur" : ""}`}>
        <div className="an-card-head">
          <div>
            <h3 style={{ fontSize: 20, fontFamily: "var(--serif)" }}>{PLANET_GLYPH[d.lord]} {d.lord} Mahadasha {d.current && <span className="an-chip" style={{ marginLeft: 8 }}>Running now</span>}</h3>
            <small>{fmtDate(d.start)} → {fmtDate(d.end)} · age {d.age_from}–{d.age_to} · {d.years} years</small>
          </div>
          <ToneTag tone={d.tone} />
        </div>
        <Score value={d.score} label="Period strength" />
        <ReadMore text={d.summary} keep={2} />
        <p className="small"><b style={{ color: "var(--gold-hi)" }}>Role for this lagna:</b> {d.functional}</p>
        <div className="an-grid two" style={{ marginTop: 12 }}>
          <div><h3 className="small">Supportive themes</h3><ul className="bullets t-excellent">{d.highlights.map((h) => <li key={h}>{h}</li>)}</ul></div>
          {d.cautions.length > 0 && <div><h3 className="small">Handle with care</h3><ul className="bullets t-challenging">{d.cautions.map((h) => <li key={h}>{h}</li>)}</ul></div>}
        </div>
        {d.more && (
          <KnowMore label={`Know more about ${d.lord} Mahadasha`}>
            <div className="km-grid">
              <div>
                <h4>Effects on life areas</h4>
                <Effects list={d.more.effects} />
              </div>
              <div>
                <h4>{d.lord} in your chart</h4>
                <dl className="facts">{(profiles?.[d.lord] ?? []).map((f) => <div key={f.label}><dt>{f.label}</dt><dd>{f.value}</dd></div>)}</dl>
              </div>
            </div>
            <h4>Houses activated</h4>
            <div className="an-chips" style={{ marginTop: 6 }}>
              {d.more.houses.map((h) => <span key={h.house} className="an-chip" title={h.theme}>{ord(h.house)} · {h.why} — {h.theme.split(",")[0]}</span>)}
            </div>
            {(d.more.best_sub || d.more.hard_sub) && (
              <p className="small" style={{ marginTop: 12 }}>
                {d.more.best_sub && <>Strongest sub-period: <b className="good-text">{d.lord}–{d.more.best_sub}</b>. </>}
                {d.more.hard_sub && d.more.hard_sub !== d.more.best_sub && <>Most demanding: <b className="warn-text">{d.lord}–{d.more.hard_sub}</b>.</>}
              </p>
            )}
            <h4>Remedy for this period</h4>
            <p className="small"><b>Mantra:</b> {d.more.remedy.mantra} — {d.more.remedy.count.toLocaleString()} times, begin on a {d.more.remedy.day}. <b>Deity:</b> {d.more.remedy.deity}.</p>
            <p className="small"><b>Charity:</b> {d.more.remedy.charity}. <b>Practice:</b> {d.more.remedy.practice}.</p>
          </KnowMore>
        )}
        <h3 style={{ marginTop: 18 }}>Antardasha (sub-periods)</h3>
        <div className="ad-list">
          {d.antardashas.map((a) => (
            <div key={a.lord + a.start} className={`ad-wrap${a.current ? " cur" : ""}`}>
              <div className={`ad t-${a.tone}${a.current ? " cur" : ""}`}>
                <div><b>{PLANET_GLYPH[a.lord]} {d.lord}–{a.lord}</b><small>{fmtDate(a.start)} – {fmtDate(a.end)}</small></div>
                <div className="small"><Hl text={a.summary} /></div>
                <ToneTag tone={a.tone} />
              </div>
              {a.more && (
                <KnowMore label="Know more" compact defaultOpen={a.current}>
                  <p className="small">{a.more.relationship}</p>
                  <Effects list={a.more.effects} />
                  <p className="small" style={{ marginTop: 8 }}><b style={{ color: "var(--gold-hi)" }}>Guidance:</b> {a.more.advice}</p>
                  {a.more.pratyantar.length > 0 && (
                    <>
                      <h4>Pratyantar dasha (sub-sub periods)</h4>
                      <div className="pd-row">
                        {a.more.pratyantar.map((p) => (
                          <span key={p.lord + p.start} className={`pd t-${p.tone}${p.current ? " cur" : ""}`} title={`${p.start} → ${p.end} · ${p.tone}`}>
                            <b>{PLANET_GLYPH[p.lord]} {p.lord}</b><small>{fmtDate(p.start)}</small>
                          </span>
                        ))}
                      </div>
                    </>
                  )}
                </KnowMore>
              )}
            </div>
          ))}
        </div>
      </motion.div>
    </>
  );
}

function KnowMore({ label, children, compact = false, defaultOpen = false }: { label: string; children: React.ReactNode; compact?: boolean; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={`km${open ? " open" : ""}${compact ? " compact" : ""}`}>
      <button type="button" className="km-btn" aria-expanded={open} onClick={() => setOpen((o) => !o)}>
        {open ? "Show less" : label} <ChevronDown size={15} className="km-chev" />
      </button>
      <div className="km-body" inert={!open}><div className="km-inner">{open && children}</div></div>
    </div>
  );
}

function Effects({ list }: { list: LifeEffect[] }) {
  if (!list.length) return <p className="small muted">No direct life-area triggers; effects are mostly internal.</p>;
  return (
    <ul className="effects">
      {list.map((e) => <li key={e.area} className={`t-${e.tone}`}><span className="tone">{e.area}</span><span className="small">{e.text}</span></li>)}
    </ul>
  );
}

function AnalysisView({ chart }: { chart: Rec }) {
  const a = chart.analysis as Analysis;
  const active = useActiveSection();
  const scrollTo = useScrollTo();
  const [style, setStyle] = useState<ChartStyle>(chart.settings.chart_style ?? "north");
  const birth = new Date(chart.birth.local_datetime);
  const cur = a.dashas.find((d) => d.current);
  const curAd = cur?.antardashas.find((x) => x.current);
  const presentYogas = chart.yogas.filter((y) => y.present);
  const go = (id: string) => (e: React.MouseEvent) => { e.preventDefault(); const el = document.getElementById(id); if (el) scrollTo(el); };

  return (
    <div className="an">
      <nav className="an-nav" aria-label="Analysis sections">
        {SECTIONS.map(([id, label], i) => (
          <a key={id} href={`#${id}`} onClick={go(id)} className={active === id ? "on" : ""} aria-current={active === id ? "true" : undefined}><span className="num">{i + 1}</span>{label}</a>
        ))}
      </nav>

      <div className="an-body">
        <Section id="summary" n={1} title="Your Kundli at a glance" lead="Core signatures and the predictions they point to, each scored from the calculated chart.">
          <Card className="featured">
            <div className="an-hero">
              <div>
                <p className="eyebrow">Janma Kundli analysis</p>
                <h1 className="display" style={{ margin: "4px 0 8px" }}>{chart.profile?.name ?? "Birth chart"}</h1>
                <div className="an-meta">
                  <span><Calendar size={14} /> {birth.toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })}</span>
                  <span><Clock size={14} /> {chart.birth.local_datetime.slice(11, 19)} ({chart.birth.timezone})</span>
                  <span><MapPin size={14} /> {chart.profile?.birthplace || `${chart.birth.latitude.toFixed(3)}, ${chart.birth.longitude.toFixed(3)}`}</span>
                </div>
                <div className="an-chips">
                  <span className="an-chip">Lagna: {chart.ascendant.sign} {chart.ascendant.dms}</span>
                  <span className="an-chip">Rashi: {chart.moon_sign}</span>
                  <span className="an-chip">Nakshatra: {chart.birth_nakshatra.name} – {chart.birth_nakshatra.pada}</span>
                  {cur && <span className="an-chip v">Dasha: {cur.lord}{curAd ? ` / ${curAd.lord}` : ""}</span>}
                  {a.overview.yogakaraka.length > 0 && <span className="an-chip v">Yogakaraka: {a.overview.yogakaraka.join(", ")}</span>}
                </div>
              </div>
              <ScoreRing value={a.overview.overall} size={112} label="Overall" />
            </div>
          </Card>
          <div style={{ marginTop: 14 }}>
            <MoreList className="an-grid" items={a.predictions} show={4} label="More predictions" render={(p) => (
              <div key={p.area} className={`an-card t-${toneOf(p.score)}`}>
                <div className="an-card-head"><h3>{p.area}</h3><ToneTag tone={toneOf(p.score)} /></div>
                <Score value={p.score} />
                <ReadMore text={p.text} keep={2} />
              </div>
            )} />
          </div>
        </Section>

        <Section id="chart" n={2} title="Birth chart & technical data" lead="Rashi, Bhava Chalit and Navamsa charts with every calculated table. Tap a house or planet for details.">
          <KundliResult chart={chart} style={style} setStyle={setStyle} />
        </Section>

        <Section id="profile" n={3} title="Ascendant, Moon sign & Nakshatra" lead="The Lagna shapes body and outlook; the Moon sign shapes mind and emotions; the birth Nakshatra fine-tunes temperament and drives the dasha sequence.">
          <div className="an-grid">
            {([["Ascendant (Lagna)", a.ascendant], ["Moon sign (Rashi)", a.moon]] as const).map(([title, s]) => (
              <div key={title} className="an-card">
                <div className="an-card-head"><h3>{title}</h3><span className="an-chip">{s.sign}</span></div>
                <p className="rd">A <b>{s.element.toLowerCase()}</b>, <b>{s.modality.toLowerCase()}</b> sign ruled by <mark className="kw">{s.lord}</mark>: {s.nature}.</p>
                <Details>
                  <ul className="rd-more">
                    <li><b className="good-text">Strengths:</b> {s.strengths}.</li>
                    <li><b className="warn-text">Growth areas:</b> {s.challenges}.</li>
                    <li><b>Favourable:</b> {s.lucky.gemstone} · {s.lucky.day} · {s.lucky.colour} · number {s.lucky.number}</li>
                  </ul>
                </Details>
              </div>
            ))}
            <div className="an-card">
              <div className="an-card-head"><h3>Birth Nakshatra</h3><span className="an-chip v">{a.nakshatra.name} – {a.nakshatra.pada}</span></div>
              <p className="rd">Natives tend to be <b>{a.nakshatra.nature}</b>. Ruled by <mark className="kw">{a.nakshatra.lord}</mark>.</p>
              <Details>
                <ul className="rd-more">
                  <li><b>Deity:</b> {a.nakshatra.deity} · <b>Symbol:</b> {a.nakshatra.symbol}</li>
                  <li><b>Gana:</b> {a.nakshatra.gana} · <b>Yoni:</b> {a.nakshatra.yoni} · <b>Nadi:</b> {a.nakshatra.nadi}</li>
                </ul>
              </Details>
            </div>
          </div>
        </Section>

        <Section id="avakhada" n={4} title="Avakhada & birth Panchang" lead="Traditional birth attributes used in naming, matching (Ashtakoota) and muhurta.">
          <MoreList className="kv" items={[
            ...a.avakhada,
            { label: "Tithi", value: a.panchang.tithi, hint: "Lunar day at birth" },
            { label: "Yoga", value: a.panchang.yoga, hint: "Sun + Moon combination" },
            { label: "Karana", value: a.panchang.karana, hint: "Half lunar day" },
            { label: "Weekday", value: a.panchang.vara, hint: a.panchang.note },
          ]} show={8} label="All birth details" render={(x) => <div key={x.label}><dt>{x.label}</dt><dd>{x.value}</dd><small>{x.hint}</small></div>} />
        </Section>

        <Section id="planets" n={5} title="Planet-by-planet interpretation" lead="Each graha's sign, house, dignity and functional role for your lagna, combined with Shadbala into a strength score.">
          <MoreList className="an-grid two" items={a.planets} show={4} label="More planets" render={(p) => (
              <div key={p.planet} className={`an-card t-${p.tone}`}>
                <div className="an-card-head">
                  <h3><span className="glyph">{PLANET_GLYPH[p.planet]}</span>{p.planet} <small style={{ fontWeight: 400 }}>· {ord(p.house)} house, {p.sign}</small></h3>
                  <ToneTag tone={p.tone} />
                </div>
                <Score value={p.score} />
                <p className="role-line">{p.functional.label.split(" — ")[0]}</p>
                <ReadMore text={p.interpretation} keep={2} />
                {(p.conditions.length > 0 || p.functional.label.includes(" — ")) && (
                  <Details label="Condition details">
                    <ul className="rd-more">
                      {p.functional.label.includes(" — ") && <li>{p.functional.label}</li>}
                      {p.conditions.map((c) => <li key={c}>{c}</li>)}
                    </ul>
                  </Details>
                )}
              </div>
            )} />
        </Section>

        <Section id="dasha" n={6} title="Vimshottari Dasha — period by period" lead={`Life unfolds through planetary periods starting from your Moon's nakshatra lord (${chart.birth_nakshatra.lord}). Select a period on the timeline to read it.`}>
          <DashaTimeline dashas={a.dashas} profiles={a.lord_profiles} />
        </Section>

        <Section id="houses" n={7} title="Twelve houses (Bhavas)" lead="Strength of each life area from its lord, occupants, aspects and Sarvashtakavarga points.">
          <MoreList className="an-grid" items={chart.house_analysis} show={6} label="More houses" render={(h) => (
              <div key={h.house} className={`an-card t-${toneOf(h.score)}`}>
                <div className="an-card-head"><h3>{ord(h.house)} · {h.name}</h3><span className="an-chip">{h.sign}</span></div>
                <Score value={h.score} />
                <p className="role-line">{h.significations}</p>
                <ReadMore text={h.interpretation} keep={2} />
              </div>
            )} />
        </Section>

        <Section id="yogas" n={8} title="Yogas & doshas" lead={`${presentYogas.length} classical yogas are formed. Doshas are listed with severity and any cancellation factors.`}>
          <h3 className="sub-h">Yogas formed</h3>
          <MoreList className="an-grid two" items={presentYogas} show={4} label="More yogas" render={(y) => (
              <div key={y.name} className="an-card t-excellent">
                <div className="an-card-head"><h3><Sparkles size={14} style={{ color: "var(--gold)" }} /> {y.name}</h3><span className="small muted">{y.category}</span></div>
                <ReadMore text={y.description} keep={1} />
              </div>
            )} />
          <h3 className="sub-h">Doshas</h3>
          <div className="an-grid two">
            {chart.doshas.map((d) => (
              <div key={d.name} className={`an-card t-${d.present ? (d.severity === "high" ? "challenging" : "mixed") : "excellent"}`}>
                <div className="an-card-head"><h3>{d.present ? <AlertTriangle size={14} className="warn-text" /> : "✓"} {d.name}</h3><ToneTag tone={d.present ? d.severity : "absent"} /></div>
                <ReadMore text={d.details} keep={1} />
                {(d.cancellations.length > 0 || d.remedies.length > 0) && (
                  <Details>
                    <ul className="rd-more">
                      {d.cancellations.length > 0 && <li className="good-text">Mitigated by: {d.cancellations.join("; ")}</li>}
                      {d.remedies.map((r) => <li key={r}>{r}</li>)}
                    </ul>
                  </Details>
                )}
              </div>
            ))}
          </div>
        </Section>

        <Section id="remedies" n={9} title="Remedies" lead="Suggested only for planets that need support. Gemstones are recommended only for functional benefics.">
          {chart.remedies.length ? (
            <MoreList className="an-grid two" items={chart.remedies} show={2} label="More remedies" render={(r) => (
                <div key={r.planet} className="an-card">
                  <div className="an-card-head"><h3>{PLANET_GLYPH[r.planet]} {r.planet}</h3><span className="an-chip">{r.day}</span></div>
                  <p className="role-line">Needs support: {r.reasons.join(", ")}</p>
                  <p className="rd"><b>Mantra:</b> <span className="mantra">{r.mantra}</span> — {r.mantra_count.toLocaleString()} times.</p>
                  <Details>
                    <ul className="rd-more">
                      <li><b>Charity:</b> {r.charity}</li>
                      <li><b>Practice:</b> {r.ritual}</li>
                      <li><b>Gemstone:</b> {r.gemstone ?? "Not advised"} — {r.gem_note}</li>
                    </ul>
                  </Details>
                </div>
            )} />
          ) : <Card><Empty icon={<Sparkles />} title="No remedies needed">All planets are reasonably placed.</Empty></Card>}
        </Section>

        <Section id="method" n={10} title="How this was calculated">
          <div className="an-card"><ReadMore text={a.methodology.join(" ")} keep={2} /></div>
        </Section>
      </div>
    </div>
  );
}

function AnalysisLoader() {
  const params = useSearchParams();
  const { user, loading } = useAuth();
  const toast = useToast();
  const rid = params.get("record");
  const [chart, setChart] = useState<Rec | null>(null);
  const [checked, setChecked] = useState(false);
  const [err, setErr] = useState("");

  // sessionStorage only exists in the browser: read it after mount so server and client HTML match.
  useEffect(() => {
    let c: Rec | null = null;
    try { c = JSON.parse(sessionStorage.getItem("kundli:last") || "null") as Rec | null; } catch {}
    if (c && (params.get("preview") || (rid && c.record_id === rid))) setChart(c);
    setChecked(true);
  }, [params, rid]);

  useEffect(() => {
    if (!checked || !rid || loading || !user || chart?.analysis) return;
    api<Rec>(`/api/kundli/records/${encodeURIComponent(rid)}`).then(setChart).catch((e) => { setErr(e.message); toast(e.message, "error"); });
  }, [checked, rid, user, loading, chart, toast]);

  if (err) return <Card><Empty icon={<AlertTriangle />} title="Could not open this reading">{err}</Empty></Card>;
  if (!chart) return !checked || rid || loading ? <Card><SkeletonBlock lines={6} /></Card> : (
    <Card><Empty icon={<Compass />} title="No chart to analyse">Create a Kundli first. <Link href="/kundli">Go to the Kundli studio →</Link></Empty></Card>
  );
  if (!chart.analysis) return <Card><Empty icon={<AlertTriangle />} title="Older calculation">Recalculate this chart from the Kundli studio to generate the full analysis.</Empty></Card>;
  return <AnalysisView chart={chart} />;
}

export default function AnalysisPage() {
  return (
    <>
      <Link href="/kundli" className="btn btn-ghost btn-sm" style={{ marginBottom: 18 }}><ArrowLeft size={15} /> Kundli studio</Link>
      <Suspense fallback={<Card><SkeletonBlock lines={6} /></Card>}><AnalysisLoader /></Suspense>
    </>
  );
}
