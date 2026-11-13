"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { FileText, Search } from "lucide-react";
import { Card, Empty, PageHeader, Pill, RequireAuth, SkeletonBlock } from "@/components/ui";
import { useApi } from "@/lib/useApi";
import { fmtDate, type SavedChart } from "@/lib/types";

function Reports() {
  const { data, error } = useApi<SavedChart[]>("/api/kundli/history");
  const items = useMemo(() => data ?? (error ? [] : null), [data, error]);
  const [q, setQ] = useState("");
  const list = useMemo(() => (items ?? []).filter((r) => r.profile_name.toLowerCase().includes(q.toLowerCase())), [items, q]);
  return (
    <>
      <PageHeader eyebrow="History" title="Saved readings" sub="Every calculation you save is kept with the exact settings used." />
      <div className="search"><Search size={16} aria-hidden /><input aria-label="Search readings" placeholder="Search by name" value={q} onChange={(e) => setQ(e.target.value)} /></div>
      {error && <div className="alert" role="alert">{error}</div>}
      {items === null ? <Card><SkeletonBlock lines={6} /></Card> : list.length === 0 ? <Card><Empty icon={<FileText size={28} />} title="Nothing saved yet"><Link href="/kundli" className="btn btn-ghost btn-sm">Calculate a chart</Link></Empty></Card> : (
        <div className="table-wrap glass">
          <table className="tbl tbl-cards">
            <thead><tr><th>Person</th><th>Lagna</th><th>Moon</th><th>Running dasha</th><th>Settings</th><th>Saved</th><th><span className="sr-only">Open</span></th></tr></thead>
            <tbody>
              {list.map((r) => {
                const c = r.calculation;
                return (
                  <tr key={r.record_id}>
                    <td data-label="Person" className="td-name"><b>{r.profile_name}</b></td>
                    <td data-label="Lagna">{c.ascendant?.sign ?? "—"}</td>
                    <td data-label="Moon">{c.moon_sign ?? c.planets?.find((p) => p.name === "Moon")?.sign ?? "—"}</td>
                    <td data-label="Running dasha">{c.dasha?.current?.slice(0, 2).map((d) => d.lord).join(" › ") ?? <Pill tone="warn">legacy</Pill>}</td>
                    <td data-label="Settings" className="muted small">{c.settings?.ayanamsa} · {c.settings?.house_system ?? "whole sign"}</td>
                    <td data-label="Saved">{fmtDate(r.created_at)}</td>
                    <td className="td-open"><Link className="btn btn-ghost btn-sm" href={`/kundli/analysis?record=${r.record_id}`} >Open analysis</Link></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default function ReportsPage() { return <RequireAuth><Reports /></RequireAuth>; }
