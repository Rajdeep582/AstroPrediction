"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { MapPin, Plus, Search, Star, Trash2, UsersRound } from "lucide-react";
import { Card, Empty, PageHeader, RequireAuth, SkeletonBlock } from "@/components/ui";
import { useToast } from "@/components/providers";
import { api } from "@/lib/api";
import { invalidate, mutateKey, useApi } from "@/lib/useApi";
import type { Profile } from "@/lib/types";

function Profiles() {
  const toast = useToast();
  const { data, error } = useApi<Profile[]>("/api/profiles");
  const items = useMemo(() => data ?? (error ? [] : null), [data, error]);
  const [q, setQ] = useState("");
  const [confirm, setConfirm] = useState<string | null>(null);

  const list = useMemo(() => (items ?? []).filter((p) => `${p.name} ${p.birthplace}`.toLowerCase().includes(q.toLowerCase())), [items, q]);

  const remove = async (p: Profile) => {
    try {
      await api(`/api/profiles/${encodeURIComponent(p.id)}`, { method: "DELETE" });
      mutateKey<Profile[]>("/api/profiles", (xs = []) => xs.filter((x) => x.id !== p.id));
      invalidate("/api/kundli/history");
      toast(`${p.name} and their readings deleted`, "success");
    } catch (e) { toast(e instanceof Error ? e.message : "Delete failed", "error"); }
    setConfirm(null);
  };

  return (
    <>
      <PageHeader eyebrow="Birth profiles" title="People in your sky" sub="Saved birth details are reused across charts, matching and the AI astrologer." actions={<Link href="/kundli" className="btn btn-gold"><Plus size={16} /> New profile</Link>} />
      <div className="search"><Search size={16} aria-hidden /><input aria-label="Search profiles" placeholder="Search by name or place" value={q} onChange={(e) => setQ(e.target.value)} /></div>
      {items === null ? <Card><SkeletonBlock /></Card> : list.length === 0 ? (
        <Card><Empty icon={<UsersRound size={28} />} title={q ? "No matches" : "No profiles yet"}>Profiles are created automatically when you save a chart.</Empty></Card>
      ) : (
        <div className="profile-grid">
          <AnimatePresence>
            {list.map((p) => (
              <motion.article key={p.id} layout="position" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.97 }} transition={{ duration: 0.18 }} className="glass profile">
                <div className="row-between">
                  <span className="avatar lg" aria-hidden>{p.name.slice(0, 1).toUpperCase()}</span>
                  {confirm === p.id ? (
                    <span className="confirm"><button className="btn btn-danger btn-sm" onClick={() => remove(p)}>Delete all</button><button className="btn btn-ghost btn-sm" onClick={() => setConfirm(null)}>Cancel</button></span>
                  ) : <button className="icon-btn" aria-label={`Delete ${p.name}`} onClick={() => setConfirm(p.id)}><Trash2 size={15} /></button>}
                </div>
                <h3>{p.name}</h3>
                <p className="muted">{new Date(`${p.birth_date}T00:00`).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })} · {p.birth_time.slice(0, 5)}</p>
                <p className="muted small"><MapPin size={12} aria-hidden /> {p.birthplace} · {p.timezone}</p>
                <Link href={`/kundli?profile=${p.id}`} className="btn btn-ghost btn-sm"><Star size={14} /> Open in Kundli</Link>
              </motion.article>
            ))}
          </AnimatePresence>
        </div>
      )}
    </>
  );
}

export default function ProfilesPage() { return <RequireAuth><Profiles /></RequireAuth>; }
