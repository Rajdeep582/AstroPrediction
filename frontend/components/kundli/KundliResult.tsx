"use client";

import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, Gem, Orbit, X } from "lucide-react";
import ChartSVG, { type ChartSelection } from "@/components/chart/ChartSVG";
import { Accordion, Bar, Card, Empty, Pill, ScoreRing, Tabs } from "@/components/ui";
import { PLANET_GLYPH, SIGNS, VARGA_LIST, fmtDate, type Chart, type ChartStyle, type DashaPeriod } from "@/lib/types";

type Tab = "chart" | "planets" | "vargas" | "dasha" | "yogas" | "strength" | "houses" | "life" | "transits";
const TABS: { id: Tab; label: string }[] = [
  { id: "chart", label: "Chart" }, { id: "planets", label: "Planets" }, { id: "vargas", label: "Divisional" }, { id: "dasha", label: "Dasha" },
  { id: "yogas", label: "Yogas & Doshas" }, { id: "strength", label: "Strength" }, { id: "houses", label: "Houses" }, { id: "life", label: "Life & Remedies" }, { id: "transits", label: "Transits" },
];
const DIG_TONE: Record<string, "good" | "gold" | "default" | "warn" | "bad"> = { exalted: "good", moolatrikona: "good", own: "gold", friendly: "default", neutral: "default", enemy: "warn", debilitated: "bad" };
const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

export default function KundliResult({ chart, style, setStyle }: { chart: Chart; style: ChartStyle; setStyle: (s: ChartStyle) => void }) {
  const [tab, setTab] = useState<Tab>("chart");
  const [sel, setSel] = useState<ChartSelection | null>(null);
  const [view, setView] = useState<"rashi" | "chalit" | "navamsa">("rashi");
  const missing = !chart.dasha || !chart.vargas;

  if (missing) {
    return <Card><Empty icon={<AlertTriangle />} title="Older calculation">This reading was saved before the full engine. Recalculate from the form to get dashas, vargas, yogas and strengths.</Empty></Card>;
  }

  return (
    <div className="stack">
      <SummaryStrip chart={chart} />
      <Tabs tabs={TABS} value={tab} onChange={setTab} label="Kundli sections" />
      <AnimatePresence mode="wait">
        <motion.div key={tab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.16 }}>
          {tab === "chart" && (
            <div className="chart-layout">
              <Card className="chart-card" action={
                <div className="seg" role="group" aria-label="Chart style">
                  {(["north", "south", "east"] as ChartStyle[]).map((s) => <button key={s} aria-pressed={style === s} onClick={() => setStyle(s)}>{cap(s)}</button>)}
                </div>}>
                <div className="seg seg-sm" role="group" aria-label="Chart view" style={{ marginBottom: 12 }}>
                  {([["rashi", "Rashi (D1)"], ["chalit", "Bhava Chalit"], ["navamsa", "Navamsa (D9)"]] as const).map(([v, l]) => <button key={v} aria-pressed={view === v} onClick={() => setView(v)}>{l}</button>)}
                </div>
                {view === "navamsa" ? (
                  <ChartSVG style={style} ascSign={chart.vargas.D9.ascendant_sign} title="Navamsa (D9)" selected={sel} onSelect={setSel}
                    bodies={chart.vargas.D9.placements.map((p) => ({ name: p.name, sign_index: p.sign_index }))} />
                ) : (
                  <ChartSVG style={view === "chalit" ? "north" : style} ascSign={chart.ascendant.sign_index} title={view === "chalit" ? `Bhava Chalit (${chart.settings.house_system.replace("_", " ")})` : "Rashi (D1)"}
                    useBodyHouses={view === "chalit"} selected={sel} onSelect={setSel}
                    bodies={chart.planets.map((p) => ({ name: p.name, sign_index: p.sign_index, house: view === "chalit" ? p.bhava : p.house, retrograde: p.retrograde, combust: p.combust, dignity: p.dignity, degree: `${Math.floor(p.longitude)}°` }))} />
                )}
                {view === "chalit" && <p className="fine">Chalit view is drawn North-style because houses, not signs, are being shifted.</p>}
              </Card>
              <DetailPanel chart={chart} sel={sel} onClose={() => setSel(null)} />
            </div>
          )}
          {tab === "planets" && <PlanetTable chart={chart} />}
          {tab === "vargas" && <Vargas chart={chart} style={style} />}
          {tab === "dasha" && <Dasha chart={chart} />}
          {tab === "yogas" && <YogasDoshas chart={chart} />}
          {tab === "strength" && <Strength chart={chart} />}
          {tab === "houses" && <Houses chart={chart} />}
          {tab === "life" && <Life chart={chart} />}
          {tab === "transits" && <TransitsView chart={chart} />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

function SummaryStrip({ chart }: { chart: Chart }) {
  const cur = chart.dasha.current;
  const items = [
    ["Lagna", `${chart.ascendant.sign} ${chart.ascendant.dms}`, `${chart.ascendant.nakshatra} · pada ${chart.ascendant.pada}`],
    ["Moon sign", chart.moon_sign, `${chart.birth_nakshatra.name} · pada ${chart.birth_nakshatra.pada}`],
    ["Running dasha", cur.slice(0, 2).map((d) => d.lord).join(" › ") || "—", cur[1] ? `until ${fmtDate(cur[1].end)}` : ""],
    ["Yogas found", String(chart.yogas.filter((y) => y.present && y.strength !== "adverse").length), `${chart.doshas.filter((d) => d.present).length} dosha(s)`],
  ];
  return (
    <div className="summary">
      {items.map(([k, v, s]) => (
        <div key={k} className="glass summary-item"><span className="eyebrow">{k}</span><strong>{v}</strong><small>{s}</small></div>
      ))}
    </div>
  );
}

function DetailPanel({ chart, sel, onClose }: { chart: Chart; sel: ChartSelection | null; onClose: () => void }) {
  if (!sel) {
    return (
      <Card className="detail" title="Explore the chart" sub="Select any planet or house — tap, click, or Tab + Enter.">
        <div className="mini-list">
          {chart.planets.map((p) => (
            <div key={p.name} className="mini-row"><span className="glyph">{PLANET_GLYPH[p.name]}</span><b>{p.name}</b><span>{p.sign} {p.dms}</span><Pill tone={DIG_TONE[p.dignity]}>{p.dignity}</Pill></div>
          ))}
        </div>
        <p className="fine">Engine: {chart.engine} · Ayanamsa {chart.settings.ayanamsa} {chart.ayanamsa_degrees.toFixed(4)}°</p>
      </Card>
    );
  }
  if (sel.kind === "planet") {
    const p = chart.planets.find((x) => x.name === sel.name);
    if (!p) return null;
    const sb = chart.shadbala.planets[p.name];
    const ha = chart.house_analysis.find((h) => h.house === p.house);
    const rules = chart.houses.filter((h) => h.lord === p.name).map((h) => h.house);
    return (
      <Card className="detail" title={<><span className="glyph lg">{PLANET_GLYPH[p.name]}</span> {p.name}</>} action={<button className="icon-btn" aria-label="Close details" onClick={onClose}><X size={15} /></button>}>
        <dl className="kv">
          <dt>Position</dt><dd>{p.sign} {p.dms}{p.retrograde && !["Rahu", "Ketu"].includes(p.name) ? " ℞" : ""}</dd>
          <dt>House / Bhava</dt><dd>{p.house} / {p.bhava}</dd>
          <dt>Nakshatra</dt><dd>{p.nakshatra} · pada {p.pada} (lord {p.nakshatra_lord})</dd>
          <dt>Sign lord</dt><dd>{p.sign_lord}</dd>
          <dt>Dignity</dt><dd><Pill tone={DIG_TONE[p.dignity]}>{p.dignity}</Pill>{p.combust && <Pill tone="warn">combust</Pill>}</dd>
          {rules.length > 0 && <><dt>Rules houses</dt><dd>{rules.join(", ")}</dd></>}
          <dt>Navamsa</dt><dd>{chart.vargas.D9.placements.find((x) => x.name === p.name)?.sign}</dd>
          {sb && <><dt>Shadbala</dt><dd>{sb.rupas} / {sb.required} rupas {sb.strong ? <Pill tone="good">strong</Pill> : <Pill tone="warn">weak</Pill>}</dd></>}
        </dl>
        {ha && <p className="body-sm">{ha.interpretation}</p>}
      </Card>
    );
  }
  const ha = chart.house_analysis.find((h) => h.house === sel.house);
  if (!ha) return null;
  return (
    <Card className="detail" title={`House ${ha.house} · ${ha.name}`} sub={ha.significations} action={<button className="icon-btn" aria-label="Close details" onClick={onClose}><X size={15} /></button>}>
      <div className="row-between"><ScoreRing value={ha.score} label={`House ${ha.house} strength`} /><dl className="kv"><dt>Sign</dt><dd>{ha.sign}</dd><dt>Lord</dt><dd>{ha.lord} in {ha.lord_house}</dd><dt>SAV</dt><dd>{ha.sav}</dd></dl></div>
      <p className="body-sm">{ha.interpretation}</p>
    </Card>
  );
}

function PlanetTable({ chart }: { chart: Chart }) {
  return (
    <Card title="Planetary positions" sub={`Sidereal · ${chart.settings.ayanamsa} · ${chart.settings.node_type} node`}>
      <div className="table-wrap">
        <table className="tbl">
          <thead><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>Nakshatra</th><th>Pada</th><th>Nak. lord</th><th>Sign lord</th><th>House</th><th>Bhava</th><th>Dignity</th><th>State</th></tr></thead>
          <tbody>
            <tr className="asc-row"><td>Ascendant</td><td>{chart.ascendant.sign}</td><td className="mono">{chart.ascendant.dms}</td><td>{chart.ascendant.nakshatra}</td><td>{chart.ascendant.pada}</td><td>{chart.ascendant.nakshatra_lord}</td><td>{chart.ascendant.sign_lord}</td><td>1</td><td>1</td><td>—</td><td>—</td></tr>
            {chart.planets.map((p) => (
              <tr key={p.name}>
                <td><span className="glyph">{PLANET_GLYPH[p.name]}</span> {p.name}</td><td>{p.sign}</td><td className="mono">{p.dms}</td><td>{p.nakshatra}</td><td>{p.pada}</td><td>{p.nakshatra_lord}</td><td>{p.sign_lord}</td><td>{p.house}</td><td>{p.bhava}</td>
                <td><Pill tone={DIG_TONE[p.dignity]}>{p.dignity}</Pill></td>
                <td>{[p.retrograde && !["Rahu", "Ketu"].includes(p.name) && "Retrograde", p.combust && "Combust"].filter(Boolean).join(", ") || "Direct"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function Vargas({ chart, style }: { chart: Chart; style: ChartStyle }) {
  const [d, setD] = useState("D9");
  const v = chart.vargas[d];
  return (
    <div className="stack">
      <div className="chips" role="group" aria-label="Divisional chart">
        {VARGA_LIST.map((k) => <button key={k} className={`chip${k === d ? " on" : ""}`} aria-pressed={k === d} onClick={() => setD(k)}>{k}</button>)}
      </div>
      <div className="chart-layout">
        <Card title={`${d} · ${v.name}`} sub={v.signifies}>
          <ChartSVG style={style} ascSign={v.ascendant_sign} bodies={v.placements.map((p) => ({ name: p.name, sign_index: p.sign_index }))} title={`${v.name} — ascendant ${SIGNS[v.ascendant_sign]}`} />
        </Card>
        <Card title="Placements">
          <table className="tbl tbl-compact"><thead><tr><th>Planet</th><th>Sign</th><th>House</th><th>D1 sign</th></tr></thead>
            <tbody>{v.placements.map((p) => <tr key={p.name}><td>{p.name}</td><td>{p.sign}</td><td>{p.house}</td><td>{chart.planets.find((x) => x.name === p.name)?.sign}</td></tr>)}</tbody>
          </table>
          <p className="fine">Vargottama: {v.placements.filter((p) => chart.planets.find((x) => x.name === p.name)?.sign_index === p.sign_index).map((p) => p.name).join(", ") || "none"} (same sign in D1 and {d}).</p>
        </Card>
      </div>
    </div>
  );
}

function DashaNode({ p, depth }: { p: DashaPeriod; depth: number }) {
  const names = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma"];
  return (
    <Accordion highlight={p.current} defaultOpen={p.current && depth < 2}
      title={<><span className="glyph">{PLANET_GLYPH[p.lord]}</span> {p.lord} <small className="muted">{names[p.level - 1]}</small>{p.current && <Pill tone="gold">running</Pill>}</>}
      meta={`${fmtDate(p.start)} → ${fmtDate(p.end)}`}>
      {p.interpretation && <p className="body-sm">{p.interpretation}</p>}
      {p.children?.length ? <div className="acc-nest">{p.children.map((c) => <DashaNode key={c.start} p={c} depth={depth + 1} />)}</div> : depth < 3 ? <p className="fine">Expand the running period to see finer sub-periods.</p> : null}
    </Accordion>
  );
}

function Dasha({ chart }: { chart: Chart }) {
  const mds = chart.dasha.mahadashas;
  const t0 = new Date(mds[0].start).getTime(), t1 = new Date(mds[mds.length - 1].end).getTime();
  const now = Date.now();
  return (
    <div className="stack">
      <Card title="Vimshottari timeline" sub={`Balance at birth: ${chart.dasha.balance_at_birth.lord} ${chart.dasha.balance_at_birth.years.toFixed(2)} years`}>
        <div className="timeline" role="list">
          {mds.map((m) => {
            const s = new Date(m.start).getTime(), e = new Date(m.end).getTime();
            return (
              <div key={m.start} role="listitem" className={`tl-seg${m.current ? " cur" : ""}`} style={{ left: `${((s - t0) / (t1 - t0)) * 100}%`, width: `${((e - s) / (t1 - t0)) * 100}%` }} title={`${m.lord}: ${fmtDate(m.start)} – ${fmtDate(m.end)}`}>
                <span>{m.lord.slice(0, 2)}</span>
              </div>
            );
          })}
          {now > t0 && now < t1 && <div className="tl-now" style={{ left: `${((now - t0) / (t1 - t0)) * 100}%` }} aria-label="Today" />}
        </div>
        <div className="row-between fine"><span>{new Date(t0).getFullYear()}</span><span>{new Date(t1).getFullYear()}</span></div>
      </Card>
      <Card title="Periods" sub="Mahadasha › Antardasha › Pratyantardasha › Sookshma">
        <div className="acc-list">{mds.map((m) => <DashaNode key={m.start} p={m} depth={0} />)}</div>
      </Card>
    </div>
  );
}

function YogasDoshas({ chart }: { chart: Chart }) {
  const [all, setAll] = useState(false);
  const yogas = chart.yogas.filter((y) => all || y.present);
  return (
    <div className="two-col">
      <Card title="Doshas" sub="Severity with cancellations and remedies">
        <div className="acc-list">
          {chart.doshas.map((d) => (
            <Accordion key={d.name} defaultOpen={d.present && d.severity !== "low"} title={<>{d.present ? <AlertTriangle size={15} className={`sev-${d.severity}`} /> : <CheckCircle2 size={15} className="ok" />} {d.name}{d.type ? ` · ${d.type}` : ""}</>}
              meta={<Pill tone={d.severity === "high" ? "bad" : d.severity === "medium" ? "warn" : d.present ? "gold" : "good"}>{d.present ? d.severity : "absent"}</Pill>}>
              <p className="body-sm">{d.details}</p>
              {d.present && <Bar value={d.score} label={`${d.name} severity`} tone={d.severity === "high" ? "var(--bad)" : "var(--warn)"} />}
              {d.cancellations.length > 0 && <p className="body-sm"><b>Cancellations:</b> {d.cancellations.join("; ")}</p>}
              {d.remedies.length > 0 && <ul className="bullets">{d.remedies.map((r) => <li key={r}>{r}</li>)}</ul>}
            </Accordion>
          ))}
        </div>
      </Card>
      <Card title="Yogas" sub={`${chart.yogas.filter((y) => y.present).length} of ${chart.yogas.length} rules satisfied`} action={<button className="btn btn-ghost btn-sm" onClick={() => setAll(!all)}>{all ? "Present only" : "Show all rules"}</button>}>
        <div className="yoga-grid" data-lenis-prevent>
          {yogas.map((y) => (
            <div key={y.name} className={`yoga${y.present ? "" : " off"}${y.strength === "adverse" ? " adverse" : ""}`}>
              <div className="row-between"><b>{y.name}</b>{y.present && <Pill tone={y.strength === "adverse" ? "bad" : y.strength === "strong" ? "good" : "gold"}>{y.strength}</Pill>}</div>
              <small className="muted">{y.category}</small>
              <p>{y.description}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function Strength({ chart }: { chart: Chart }) {
  const sb = chart.shadbala.planets;
  const max = Math.max(...Object.values(sb).map((r) => r.rupas), 8);
  const bav = chart.ashtakavarga.bhinnashtakavarga;
  const ascIdx = chart.ascendant.sign_index;
  return (
    <div className="stack">
      <Card title="Shadbala" sub={chart.shadbala.method}>
        <div className="sb-chart">
          {Object.entries(sb).map(([name, r]) => (
            <div key={name} className="sb-row">
              <span className="sb-name"><span className="glyph">{PLANET_GLYPH[name]}</span>{name}</span>
              <div className="sb-track">
                <Bar value={r.rupas} max={max} label={`${name} ${r.rupas} rupas`} tone={r.strong ? "linear-gradient(90deg,#8a6d33,#e9c97f)" : "linear-gradient(90deg,#6b3b33,#d98a6c)"} />
                <i className="sb-req" style={{ left: `${(r.required / max) * 100}%` }} title={`Required ${r.required}`} />
              </div>
              <span className="mono">{r.rupas.toFixed(2)}</span>
            </div>
          ))}
        </div>
        <details className="fine-details"><summary>Component breakdown (virupas)</summary>
          <div className="table-wrap"><table className="tbl tbl-compact"><thead><tr><th>Planet</th><th>Sthana</th><th>Dig</th><th>Kala</th><th>Chesta</th><th>Naisargika</th><th>Drik</th><th>Total</th></tr></thead>
            <tbody>{Object.entries(sb).map(([n, r]) => <tr key={n}><td>{n}</td><td>{r.sthana}</td><td>{r.dig}</td><td>{r.kala}</td><td>{r.chesta}</td><td>{r.naisargika}</td><td>{r.drik}</td><td><b>{r.total_virupas}</b></td></tr>)}</tbody></table></div>
        </details>
      </Card>
      <Card title="Ashtakavarga" sub={`Sarvashtakavarga total ${chart.ashtakavarga.total} · houses ≥ 28 are supportive`}>
        <div className="table-wrap">
          <table className="tbl tbl-compact av">
            <thead><tr><th>Sign</th>{SIGNS.map((s, i) => <th key={s} className={i === ascIdx ? "asc-col" : ""}>{s.slice(0, 3)}</th>)}<th>Σ</th></tr></thead>
            <tbody>
              {Object.entries(bav).map(([p, pts]) => <tr key={p}><td>{p}</td>{pts.map((v, i) => <td key={i} className={i === ascIdx ? "asc-col" : ""} style={{ opacity: 0.45 + v / 14 }}>{v}</td>)}<td>{chart.ashtakavarga.bav_totals[p]}</td></tr>)}
              <tr className="sav-row"><td>SAV</td>{chart.ashtakavarga.sarvashtakavarga.map((v, i) => <td key={i} className={`${v >= 28 ? "hi" : "lo"}${i === ascIdx ? " asc-col" : ""}`}>{v}</td>)}<td>{chart.ashtakavarga.total}</td></tr>
            </tbody>
          </table>
        </div>
        <div className="sav-bars" aria-label="Sarvashtakavarga by house">
          {chart.ashtakavarga.by_house.map((h) => (
            <div key={h.house} className="sav-col" title={`House ${h.house} (${h.sign}): ${h.points}`}>
              <motion.i initial={{ height: 0 }} animate={{ height: `${(h.points / 45) * 100}%` }} className={h.strong ? "hi" : "lo"} />
              <small>{h.house}</small>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function Houses({ chart }: { chart: Chart }) {
  return (
    <div className="acc-list">
      {chart.house_analysis.map((h) => (
        <Accordion key={h.house} title={<><span className="house-no">{h.house}</span> {h.name} bhava <small className="muted">{h.sign}</small></>} meta={<Bar value={h.score} label={`House ${h.house} score`} />}>
          <p className="body-sm"><b>Significations:</b> {h.significations}</p>
          <p className="body-sm">{h.interpretation}</p>
        </Accordion>
      ))}
    </div>
  );
}

function Life({ chart }: { chart: Chart }) {
  const areas = useMemo(() => Object.entries(chart.life_areas), [chart]);
  return (
    <div className="stack">
      <div className="area-grid">
        {areas.map(([k, a]) => (
          <Card key={k} className="area">
            <div className="row-between"><h3 className="card-title">{cap(k)}</h3><ScoreRing value={a.score} size={64} label={k} /></div>
            <Pill tone={a.outlook === "excellent" || a.outlook === "good" ? "good" : a.outlook === "mixed" ? "gold" : "warn"}>{a.outlook}</Pill>
            <p className="body-sm">{a.summary}</p>
          </Card>
        ))}
      </div>
      <Card title="Remedies" sub="Prescribed only for afflicted or weak planets. Gemstones only where the planet is a functional benefic.">
        {chart.remedies.length === 0 ? <Empty icon={<CheckCircle2 />} title="No major afflictions">No planet needs corrective remedies.</Empty> : (
          <div className="remedy-grid">
            {chart.remedies.map((r) => (
              <div key={r.planet} className="remedy">
                <div className="row-between"><b><span className="glyph">{PLANET_GLYPH[r.planet]}</span> {r.planet}</b><small className="muted">{r.reasons.join(" · ")}</small></div>
                <dl className="kv">
                  <dt><Gem size={13} /> Gemstone</dt><dd>{r.gemstone ? `${r.gemstone} — ${r.metal}, ${r.finger} finger, ${r.day}` : "Not advised"}</dd>
                  <dt>Mantra</dt><dd className="mantra">{r.mantra} <small>({r.mantra_count.toLocaleString()} japa)</small></dd>
                  <dt>Charity</dt><dd>{r.charity}</dd>
                  <dt>Ritual</dt><dd>{r.ritual} · {r.deity}</dd>
                </dl>
                <p className="fine">{r.gem_note}</p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function TransitsView({ chart }: { chart: Chart }) {
  const t = chart.transits;
  return (
    <Card title="Gochar — current transits" sub={`Judged from natal Moon (${t.reference_moon_sign}) · ${fmtDate(t.date)}`} action={<ScoreRing value={t.score} size={60} label="Transit favourability" />}>
      <div className="transit-grid">
        {t.planets.map((p) => (
          <div key={p.name} className={`transit ${p.favourable ? "fav" : "unfav"}`}>
            <div className="row-between"><b><span className="glyph">{PLANET_GLYPH[p.name]}</span> {p.name}{p.retrograde ? " ℞" : ""}</b><Orbit size={14} aria-hidden /></div>
            <small className="muted">{p.sign} {p.degree} · {p.nakshatra}</small>
            <p>{p.effect}</p>
            <small>{p.house_from_moon} from Moon · {p.house_from_lagna} from Lagna{p.conjunct_natal ? ` · over natal ${p.conjunct_natal.join(", ")}` : ""}</small>
          </div>
        ))}
      </div>
    </Card>
  );
}
