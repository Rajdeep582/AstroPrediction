"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence } from "framer-motion";
import CalcOverlay from "@/components/kundli/CalcOverlay";
import Link from "next/link";
import { Star } from "lucide-react";
import BirthFormCard from "@/components/BirthFormCard";
import KundliResult from "@/components/kundli/KundliResult";
import { Card, Empty, PageHeader, SkeletonBlock } from "@/components/ui";
import { useAuth, usePrefs, useToast } from "@/components/providers";
import { api } from "@/lib/api";
import { invalidate, mutateKey, useApi } from "@/lib/useApi";
import type { BirthForm, Chart, ChartStyle, Profile } from "@/lib/types";

const blank = (p: { ayanamsa: string; houseSystem: string; nodeType: string; chartStyle: ChartStyle }): BirthForm => ({
  name: "", birth_date: "", birth_time: "", birthplace: "", latitude: "", longitude: "", timezone: "Asia/Kolkata",
  ayanamsa: p.ayanamsa, chart_style: p.chartStyle, node_type: p.nodeType, house_system: p.houseSystem,
});

function KundliWorkspace() {
  const params = useSearchParams();
  const { user } = useAuth();
  const { prefs, ready } = usePrefs();
  const toast = useToast();
  const [form, setForm] = useState<BirthForm>(() => blank(prefs));
  const { data: profiles = [] } = useApi<Profile[]>(user ? "/api/profiles" : null);
  const [chart, setChart] = useState<Chart | null>(null);
  const [style, setStyle] = useState<ChartStyle>(prefs.chartStyle);
  const [busy, setBusy] = useState(false);
  const [calc, setCalc] = useState<{ ready: boolean; dest?: string } | null>(null);
  const router = useRouter();
  const [loadingRecord, setLoadingRecord] = useState(false);
  const resultRef = useRef<HTMLDivElement>(null);

  // apply stored defaults once they load from localStorage (before any chart is shown)
  const prefsApplied = useRef(false);
  useEffect(() => {
    if (prefsApplied.current || !ready) return;
    prefsApplied.current = true;
    setStyle((s) => (chart ? s : prefs.chartStyle));
    setForm((f) => ({ ...f, ayanamsa: prefs.ayanamsa, house_system: prefs.houseSystem, node_type: prefs.nodeType, chart_style: prefs.chartStyle }));
  }, [prefs, ready, chart]);

  // open ?profile=
  const pid = params.get("profile");
  useEffect(() => {
    const p = pid && profiles.find((x) => x.id === pid);
    if (p) setForm((f) => (f.profile_id === p.id ? f : { ...f, profile_id: p.id, name: p.name, birth_date: p.birth_date, birth_time: p.birth_time.slice(0, 8), birthplace: p.birthplace, latitude: String(p.latitude), longitude: String(p.longitude), timezone: p.timezone }));
  }, [pid, profiles]);

  // open ?record=
  const rid = params.get("record");
  useEffect(() => {
    if (!user || !rid) return;
    let alive = true;
    setLoadingRecord(true);
    api<Chart & { input?: Partial<BirthForm> }>(`/api/kundli/records/${encodeURIComponent(rid)}`)
      .then((c) => {
        if (!alive) return;
        setChart(c);
        if (c.settings?.chart_style) setStyle(c.settings.chart_style);
        const p = c.profile;
        if (p) setForm((f) => ({ ...f, profile_id: p.id, name: p.name, birth_date: p.birth_date, birth_time: p.birth_time.slice(0, 8), birthplace: p.birthplace, latitude: String(p.latitude), longitude: String(p.longitude), timezone: p.timezone }));
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => alive && setLoadingRecord(false));
    return () => { alive = false; };
  }, [user, rid, toast]);

  const calculate = useCallback(async () => {
    setBusy(true);
    setCalc({ ready: false });
    const body = {
      name: form.name.trim(), profile_id: form.profile_id || null, birth_date: form.birth_date,
      birth_time: form.birth_time.length === 5 ? `${form.birth_time}:00` : form.birth_time,
      birthplace: form.birthplace, latitude: Number(form.latitude), longitude: Number(form.longitude), timezone: form.timezone,
      ayanamsa: form.ayanamsa, chart_style: form.chart_style, node_type: form.node_type, house_system: form.house_system,
    };
    try {
      const res = await api<Chart & { record_id?: string }>(user ? "/api/kundli/calculate" : "/api/kundli/preview", { method: "POST", body });
      setChart(res);
      setStyle(form.chart_style);
      let dest = "/kundli/analysis?preview=1";
      if (res.record_id) dest = `/kundli/analysis?record=${encodeURIComponent(res.record_id)}`;
      try { sessionStorage.setItem("kundli:last", JSON.stringify({ ...res, profile: res.profile ?? { name: body.name, birthplace: body.birthplace } })); } catch {}
      router.prefetch(dest);
      setCalc({ ready: true, dest });
      if (user && res.profile) {
        setForm((f) => ({ ...f, profile_id: res.profile?.id }));
        mutateKey<Profile[]>("/api/profiles", (ps = []) => [res.profile as Profile, ...ps.filter((p) => p.id !== res.profile?.id)]);
        invalidate("/api/kundli/history");
        toast("Chart calculated and saved", "success");
      } else toast("Chart calculated — sign in to save it", "info");
    } catch (e) {
      setCalc(null);
      toast(e instanceof Error ? e.message : "Calculation failed", "error");
    } finally { setBusy(false); }
  }, [form, user, toast, router]);

  return (
    <>
      <AnimatePresence>
        {calc && <CalcOverlay key="calc" name={form.name.trim()} ready={calc.ready} onDone={() => { if (calc.dest) router.push(calc.dest); setTimeout(() => setCalc(null), 400); }} />}
      </AnimatePresence>
      <PageHeader eyebrow="Janma Kundli" title={<>Birth chart <em>studio</em></>} sub="Sidereal positions, divisional charts, dashas, yogas, strengths and transits — from one calculation." />
      <div className="kundli-layout">
        <div className="kundli-form">
          <BirthFormCard form={form} setForm={setForm} profiles={profiles} busy={busy} onSubmit={calculate} />
          {!user && <p className="fine center"><Link href="/signin?next=/kundli">Sign in</Link> to save charts and profiles.</p>}
        </div>
        <div ref={resultRef} className="kundli-result">
          {loadingRecord ? (
            <Card><SkeletonBlock lines={3} /><div className="skeleton" style={{ aspectRatio: "1", marginTop: 16, borderRadius: 12 }} /></Card>
          ) : chart ? (
            <>
              {chart.record_id || params.get("record") ? (
                <Link className="btn btn-gold btn-block" href={`/kundli/analysis?record=${chart.record_id ?? params.get("record")}`} style={{ marginBottom: 14 }}>Open full Kundli analysis →</Link>
              ) : null}
              <KundliResult chart={chart} style={style} setStyle={setStyle} />
            </>
          ) : (
            <Card className="placeholder-card"><Empty icon={<Star size={30} />} title="Your chart will appear here">Enter birth details and pick the birthplace on the map. Everything is calculated in one pass.</Empty></Card>
          )}
        </div>
      </div>
    </>
  );
}

export default function KundliPage() {
  return <Suspense fallback={<SkeletonBlock />}><KundliWorkspace /></Suspense>;
}
