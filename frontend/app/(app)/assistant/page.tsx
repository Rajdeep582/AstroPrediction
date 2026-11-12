"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Send, Sparkles } from "lucide-react";
import { PageHeader, RequireAuth } from "@/components/ui";
import { useToast } from "@/components/providers";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import type { Profile } from "@/lib/types";

type Msg = { role: "user" | "assistant"; content: string };
const SUGGEST = ["What does my current dasha emphasise?", "Which yogas are strongest in my chart?", "How is my 10th house for career?", "Explain my Moon nakshatra."];

function renderMd(text: string) {
  return text.split(/\n{2,}/).map((block, i) => {
    const lines = block.split("\n");
    if (lines.every((l) => /^\s*[-*]\s/.test(l))) return <ul key={i}>{lines.map((l, j) => <li key={j}>{inline(l.replace(/^\s*[-*]\s/, ""))}</li>)}</ul>;
    const h = block.match(/^#{1,3}\s+(.*)/);
    if (h) return <h4 key={i}>{inline(h[1])}</h4>;
    return <p key={i}>{lines.map((l, j) => <span key={j}>{inline(l)}{j < lines.length - 1 && <br />}</span>)}</p>;
  });
}
function inline(s: string) {
  return s.split(/(\*\*[^*]+\*\*)/g).map((part, i) => part.startsWith("**") ? <strong key={i}>{part.slice(2, -2)}</strong> : part);
}

function Assistant() {
  const toast = useToast();
  const { data: profiles = [] } = useApi<Profile[]>("/api/profiles");
  const [pid, setPid] = useState<string | null>(null);
  const ctx = pid ?? profiles[0]?.id ?? "";
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const log = useRef<HTMLDivElement>(null);

  useEffect(() => { const el = log.current; if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" }); }, [msgs, busy]);

  const ask = async (text: string) => {
    if (!text.trim() || busy) return;
    const history = msgs.slice(-10);
    setMsgs((m) => [...m, { role: "user", content: text }]);
    setQ(""); setBusy(true);
    try {
      const res = await api<{ answer: string }>("/api/assistant", { method: "POST", body: { question: text, profile_id: ctx || null, history } });
      setMsgs((m) => [...m, { role: "assistant", content: res.answer }]);
    } catch (e) {
      toast(e instanceof Error ? e.message : "Assistant unavailable", "error");
      setMsgs((m) => m.slice(0, -1)); setQ(text);
    } finally { setBusy(false); }
  };
  const submit = (e: FormEvent) => { e.preventDefault(); void ask(q); };

  return (
    <>
      <PageHeader eyebrow="AI Astrologer" title={<>Ask the <em>chart</em></>} sub="Answers are grounded in your saved calculation: placements, dashas, yogas, doshas and strengths. Positions are never invented." />
      <div className="chat glass">
        <div className="chat-bar">
          <label htmlFor="ctx" className="muted small">Chart context</label>
          <select id="ctx" value={ctx} onChange={(e) => setPid(e.target.value)}>
            <option value="">General question (no chart)</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div ref={log} className="chat-log" aria-live="polite" data-lenis-prevent>
          {msgs.length === 0 && (
            <div className="chat-empty">
              <Sparkles size={28} aria-hidden />
              <p>Try one of these:</p>
              <div className="chips">{SUGGEST.map((s) => <button key={s} className="chip" onClick={() => ask(s)}>{s}</button>)}</div>
            </div>
          )}
          <AnimatePresence initial={false}>
            {msgs.map((m, i) => (
              <motion.div key={i} className={`bubble ${m.role}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                {m.role === "assistant" ? renderMd(m.content) : m.content}
              </motion.div>
            ))}
          </AnimatePresence>
          {busy && <div className="bubble assistant typing" aria-label="Thinking"><i /><i /><i /></div>}
        </div>
        <form className="chat-input" onSubmit={submit}>
          <textarea aria-label="Your question" rows={1} value={q} maxLength={2000} placeholder="Ask about career timing, relationships, a yoga…" onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void ask(q); } }} />
          <button className="btn btn-gold" disabled={busy || !q.trim()} aria-label="Send">{busy ? <Loader2 size={16} className="spin" /> : <Send size={16} />}</button>
        </form>
      </div>
      <p className="fine center">Guidance for reflection — not medical, legal or financial advice.</p>
    </>
  );
}

export default function AssistantPage() { return <RequireAuth><Assistant /></RequireAuth>; }
