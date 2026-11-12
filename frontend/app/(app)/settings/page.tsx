"use client";

import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { AYANAMSAS, HOUSE_SYSTEMS } from "@/components/BirthFormCard";
import { Card, PageHeader, RequireAuth } from "@/components/ui";
import { useAuth, usePrefs, useToast } from "@/components/providers";
import type { ChartStyle } from "@/lib/types";

function Settings() {
  const { prefs, setPrefs } = usePrefs();
  const { user, signout } = useAuth();
  const toast = useToast();
  const router = useRouter();
  const save = (p: Parameters<typeof setPrefs>[0]) => { setPrefs(p); toast("Preference saved", "success"); };
  return (
    <>
      <PageHeader eyebrow="Preferences" title="Settings" sub="Defaults applied to every new calculation on this device." />
      <div className="two-col">
        <Card title="Calculation defaults">
          <div className="stack-sm">
            <div className="ffield"><select id="s-style" value={prefs.chartStyle} onChange={(e) => save({ chartStyle: e.target.value as ChartStyle })}><option value="north">North Indian</option><option value="south">South Indian</option><option value="east">East Indian</option></select><label htmlFor="s-style">Chart style</label></div>
            <div className="ffield"><select id="s-ayan" value={prefs.ayanamsa} onChange={(e) => save({ ayanamsa: e.target.value })}>{AYANAMSAS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select><label htmlFor="s-ayan">Ayanamsa</label></div>
            <div className="ffield"><select id="s-hs" value={prefs.houseSystem} onChange={(e) => save({ houseSystem: e.target.value })}>{HOUSE_SYSTEMS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select><label htmlFor="s-hs">House system</label></div>
            <div className="ffield"><select id="s-node" value={prefs.nodeType} onChange={(e) => save({ nodeType: e.target.value })}><option value="true">True node</option><option value="mean">Mean node</option></select><label htmlFor="s-node">Rahu/Ketu</label></div>
          </div>
        </Card>
        <Card title="Experience">
          <label className="switch">
            <input type="checkbox" checked={prefs.reduceMotion} onChange={(e) => save({ reduceMotion: e.target.checked })} />
            <span aria-hidden /> Reduce motion (static stars, minimal transitions)
          </label>
          <hr className="rule" />
          <p className="muted">Signed in as <b>{user?.username}</b></p>
          <button className="btn btn-ghost" onClick={async () => { await signout(); router.push("/"); }}><LogOut size={15} /> Sign out</button>
        </Card>
      </div>
    </>
  );
}

export default function SettingsPage() { return <RequireAuth><Settings /></RequireAuth>; }
