"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import dynamic from "next/dynamic";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, Clock, Loader2, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import type { BirthForm, Profile } from "@/lib/types";
import { Skeleton } from "@/components/ui";

const LocationPicker = dynamic(() => import("@/components/LocationPicker"), { ssr: false, loading: () => <Skeleton h={260} /> });

export const AYANAMSAS = [["lahiri", "Lahiri (Chitrapaksha)"], ["raman", "B.V. Raman"], ["kp", "Krishnamurti (KP)"], ["yukteshwar", "Sri Yukteshwar"], ["fagan_bradley", "Fagan–Bradley"]];
export const HOUSE_SYSTEMS = [["whole_sign", "Whole Sign"], ["equal", "Equal"], ["placidus", "Placidus"], ["kp", "KP (Placidus cusps)"]];

let zoneList: string[] | null = null;
function zones(): string[] {
  if (zoneList) return zoneList;
  try {
    zoneList = (Intl as unknown as { supportedValuesOf: (k: string) => string[] }).supportedValuesOf("timeZone");
  } catch {
    zoneList = ["Asia/Kolkata", "UTC"];
  }
  return zoneList;
}

function Float({ id, label, children, hint }: { id: string; label: string; children: React.ReactNode; hint?: string }) {
  return (
    <div className="ffield">
      {children}
      <label htmlFor={id}>{label}</label>
      {hint && <small className="hint">{hint}</small>}
    </div>
  );
}

export default function BirthFormCard({ form, setForm, profiles, busy, onSubmit, submitLabel = "Calculate Kundli" }: {
  form: BirthForm;
  setForm: (f: BirthForm | ((f: BirthForm) => BirthForm)) => void;
  profiles: Profile[];
  busy: boolean;
  onSubmit: () => void;
  submitLabel?: string;
}) {
  const [advanced, setAdvanced] = useState(false);
  const [tzBusy, setTzBusy] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof BirthForm, string>>>({});
  const tzReq = useRef(0);
  const set = <K extends keyof BirthForm>(k: K, v: BirthForm[K]) => setForm((f) => ({ ...f, [k]: v }));

  // resolve IANA zone from coordinates
  useEffect(() => {
    const lat = Number(form.latitude), lon = Number(form.longitude);
    if (!form.latitude || !form.longitude || Number.isNaN(lat) || Number.isNaN(lon)) return;
    const id = ++tzReq.current;
    const t = setTimeout(async () => {
      setTzBusy(true);
      try {
        const res = await api<{ timezone: string | null }>(`/api/timezone?lat=${lat}&lon=${lon}`, { retries: 0 });
        if (id === tzReq.current && res.timezone) setForm((f) => ({ ...f, timezone: res.timezone as string }));
      } catch { /* keep manual zone */ } finally { if (id === tzReq.current) setTzBusy(false); }
    }, 350);
    return () => clearTimeout(t);
  }, [form.latitude, form.longitude, setForm]);

  const validate = () => {
    const e: typeof errors = {};
    if (!form.name.trim()) e.name = "Name is required";
    if (!form.birth_date) e.birth_date = "Birth date is required";
    else if (form.birth_date < "1600-01-01" || form.birth_date > "2200-12-31") e.birth_date = "Date must be 1600–2200";
    if (!form.birth_time) e.birth_time = "Birth time is required";
    const lat = Number(form.latitude), lon = Number(form.longitude);
    if (form.latitude === "" || Number.isNaN(lat) || lat < -90 || lat > 90) e.latitude = "Pick a birthplace or enter latitude";
    if (form.longitude === "" || Number.isNaN(lon) || lon < -180 || lon > 180) e.longitude = "Longitude −180…180";
    if (!/^[A-Za-z_]+(\/[A-Za-z0-9_+-]+)*$/.test(form.timezone.trim())) e.timezone = "Enter an IANA zone, e.g. Asia/Kolkata";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const submit = (ev: FormEvent) => {
    ev.preventDefault();
    if (validate()) onSubmit();
    else requestAnimationFrame(() => (ev.target as HTMLFormElement).querySelector<HTMLElement>("[aria-invalid=true]")?.focus());
  };

  const loadProfile = (id: string) => {
    const p = profiles.find((x) => x.id === id);
    if (!p) { set("profile_id", undefined); return; }
    setForm((f) => ({ ...f, profile_id: p.id, name: p.name, birth_date: p.birth_date, birth_time: p.birth_time.slice(0, 8), birthplace: p.birthplace, latitude: String(p.latitude), longitude: String(p.longitude), timezone: p.timezone }));
    setErrors({});
  };

  const err = (k: keyof BirthForm) => errors[k] ? <small className="err" role="alert">{errors[k]}</small> : null;

  return (
    <form className="glass form-card" onSubmit={submit} noValidate>
      <div className="card-head"><div><h2 className="card-title">Birth details</h2><p className="card-sub">Local wall-clock time at birthplace. Seconds improve ascendant precision.</p></div></div>

      {profiles.length > 0 && (
        <div className="ffield">
          <select id="saved" value={form.profile_id ?? ""} onChange={(e) => loadProfile(e.target.value)}>
            <option value="">New person</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name} · {p.birth_date}</option>)}
          </select>
          <label htmlFor="saved">Saved profile</label>
        </div>
      )}

      <Float id="name" label="Full name">
        <input id="name" placeholder=" " value={form.name} onChange={(e) => set("name", e.target.value)} aria-invalid={!!errors.name} autoComplete="name" maxLength={100} />
      </Float>
      {err("name")}

      <div className="grid-2">
        <div>
          <Float id="bdate" label="Date of birth"><input id="bdate" type="date" placeholder=" " value={form.birth_date} onChange={(e) => set("birth_date", e.target.value)} aria-invalid={!!errors.birth_date} min="1600-01-01" max="2200-12-31" /></Float>
          {err("birth_date")}
        </div>
        <div>
          <Float id="btime" label="Time of birth"><input id="btime" type="time" step="1" placeholder=" " value={form.birth_time} onChange={(e) => set("birth_time", e.target.value)} aria-invalid={!!errors.birth_time} /></Float>
          {err("birth_time")}
        </div>
      </div>

      <LocationPicker
        value={form.birthplace} latitude={form.latitude} longitude={form.longitude}
        onLocation={(name, lat, lon) => setForm((f) => ({ ...f, birthplace: name, latitude: lat.toFixed(6), longitude: lon.toFixed(6) }))}
        onName={(name) => set("birthplace", name)}
        onCoords={(lat, lon) => setForm((f) => ({ ...f, latitude: lat, longitude: lon }))}
      />

      <div className="grid-3" style={{ marginTop: 14 }}>
        <div>
          <Float id="lat" label="Latitude"><input id="lat" inputMode="decimal" placeholder=" " value={form.latitude} onChange={(e) => set("latitude", e.target.value)} aria-invalid={!!errors.latitude} /></Float>
          {err("latitude")}
        </div>
        <div>
          <Float id="lon" label="Longitude"><input id="lon" inputMode="decimal" placeholder=" " value={form.longitude} onChange={(e) => set("longitude", e.target.value)} aria-invalid={!!errors.longitude} /></Float>
          {err("longitude")}
        </div>
        <div>
          <Float id="tz" label="Time zone" hint={tzBusy ? "Resolving from coordinates…" : "Auto-detected from birthplace"}>
            <input id="tz" list="tz-list" placeholder=" " value={form.timezone} onChange={(e) => set("timezone", e.target.value)} aria-invalid={!!errors.timezone} />
          </Float>
          <datalist id="tz-list">{zones().map((z) => <option key={z} value={z} />)}</datalist>
          {err("timezone")}
        </div>
      </div>

      <button type="button" className="adv-toggle" aria-expanded={advanced} onClick={() => setAdvanced(!advanced)}>
        Calculation settings <ChevronDown size={15} style={{ transform: advanced ? "rotate(180deg)" : undefined, transition: ".2s" }} />
      </button>
      <AnimatePresence initial={false}>
        {advanced && (
          <motion.div className="grid-2" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
            <div className="ffield"><select id="ayan" value={form.ayanamsa} onChange={(e) => set("ayanamsa", e.target.value)}>{AYANAMSAS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select><label htmlFor="ayan">Ayanamsa</label></div>
            <div className="ffield"><select id="hs" value={form.house_system} onChange={(e) => set("house_system", e.target.value)}>{HOUSE_SYSTEMS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select><label htmlFor="hs">House system (Bhava/Chalit)</label></div>
            <div className="ffield"><select id="node" value={form.node_type} onChange={(e) => set("node_type", e.target.value)}><option value="true">True node</option><option value="mean">Mean node</option></select><label htmlFor="node">Rahu/Ketu</label></div>
            <div className="ffield"><select id="style" value={form.chart_style} onChange={(e) => set("chart_style", e.target.value as BirthForm["chart_style"])}><option value="north">North Indian</option><option value="south">South Indian</option><option value="east">East Indian</option></select><label htmlFor="style">Chart style</label></div>
          </motion.div>
        )}
      </AnimatePresence>

      <button className="btn btn-gold btn-block btn-lg" disabled={busy} type="submit">
        {busy ? <><Loader2 size={16} className="spin" /> Calculating…</> : <><Sparkles size={16} /> {submitLabel}</>}
      </button>
      <p className="fine"><Clock size={12} aria-hidden /> Unknown exact time? Use noon — ascendant and houses will be approximate.</p>
    </form>
  );
}
