"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { AnimatePresence } from "framer-motion";
import { ArrowRight, RotateCcw, Send, Sparkles, Square } from "lucide-react";
import CalcOverlay from "@/components/kundli/CalcOverlay";
import { RequireAuth } from "@/components/ui";
import { useToast } from "@/components/providers";
import { API, api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import type { Profile } from "@/lib/types";

type Msg = { role: "user" | "assistant"; content: string };
type Summary = { name: string; lagna: string; moon: string; nakshatra: string; dasha: string; yogas: number; facts: number };

const STUDY_STEPS = [
  "Opening your saved Kundli",
  "Reading Lagna, Moon sign & Nakshatra",
  "Weighing all 9 planets — dignity & strength",
  "Mapping the 12 houses & their lords",
  "Laying out your Vimshottari dasha timeline",
  "Checking yogas, doshas & cancellations",
  "Noting current transits & remedies",
  "Your AI astrologer is ready",
];
const SUGGEST = [
  "How will my career and finances look over the next 10 years?",
  "What does the next 5 years hold for my marriage? Any complications or remedies?",
  "What are my biggest strengths and weaknesses according to my chart?",
  "When is a good period for buying property or a big investment?",
  "What should I watch out for in my health?",
  "Explain my current dasha in simple words.",
];

function renderMd(text: string) {
  return text.split(/\n{2,}/).map((block, i) => {
    const lines = block.split("\n").filter((l) => l.trim());
    if (!lines.length) return null;
    if (lines.every((l) => /^\s*[-*•]\s/.test(l))) return <ul key={i}>{lines.map((l, j) => <li key={j}>{inline(l.replace(/^\s*[-*•]\s+/, ""))}</li>)}</ul>;
    const h = block.match(/^#{1,4}\s+(.*)/);
    if (h) return <h4 key={i}>{inline(h[1])}</h4>;
    return <p key={i}>{lines.map((l, j) => <span key={j}>{inline(l.replace(/^\s*[-*•]\s+/, "• "))}{j < lines.length - 1 && <br />}</span>)}</p>;
  });
}
function inline(s: string) {
  return s.split(/(\*\*[^*]+\*\*|\*[^*]+\*|_[^_]+_)/g).map((part, i) =>
    part.startsWith("**") ? <strong key={i}>{part.slice(2, -2)}</strong>
      : (part.startsWith("*") || part.startsWith("_")) && part.length > 2 ? <em key={i}>{part.slice(1, -1)}</em> : part);
}

/** Animated crystal ball: CSS-only swirl + orbiting stars (cheap, compositor-driven). */
function CrystalBall({ thinking = false }: { thinking?: boolean }) {
  return (
    <div className={`orb${thinking ? " thinking" : ""}`} aria-hidden>
      <div className="orb-glow" />
      <div className="orb-sphere">
        <div className="orb-swirl s1" /><div className="orb-swirl s2" /><div className="orb-swirl s3" />
        <div className="orb-stars" />
        <div className="orb-shine" />
      </div>
      <div className="orb-ring" />
      <div className="orb-base" />
    </div>
  );
}

function Assistant() {
  const toast = useToast();
  const { data: profiles = [], loading } = useApi<Profile[]>("/api/profiles");
  const [pid, setPid] = useState<string>("");
  const [phase, setPhase] = useState<"intro" | "study" | "chat">("intro");
  const [studyReady, setStudyReady] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const abort = useRef<AbortController | null>(null);
  const log = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { if (!pid && profiles[0]) setPid(profiles[0].id); }, [profiles, pid]);
  useEffect(() => { const el = log.current; if (el) el.scrollTop = el.scrollHeight; }, [msgs, busy]);

  const begin = async () => {
    if (!pid) { setSummary(null); setPhase("chat"); return; }
    setStudyReady(false); setPhase("study");
    try {
      const res = await api<{ summary: Summary }>("/api/assistant/prepare", { method: "POST", body: { profile_id: pid } });
      setSummary(res.summary); setMsgs([]); setStudyReady(true);
    } catch (e) {
      setPhase("intro");
      toast(e instanceof Error ? e.message : "Could not open this chart", "error");
    }
  };

  const ask = useCallback(async (text: string) => {
    const question = text.trim();
    if (!question || busy) return;
    const history = msgs.slice(-8);
    setMsgs((m) => [...m, { role: "user", content: question }, { role: "assistant", content: "" }]);
    setQ(""); setBusy(true);
    const ctl = new AbortController(); abort.current = ctl;
    let got = "";
    const put = (t: string) => setMsgs((m) => { const c = m.slice(); c[c.length - 1] = { role: "assistant", content: t }; return c; });
    try {
      const res = await fetch(`${API}/api/assistant/stream`, {
        method: "POST", credentials: "include", signal: ctl.signal, headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, profile_id: summary ? pid : null, history }),
      });
      if (!res.ok || !res.body) {
        const err = await res.json().catch(() => ({}));
        throw new Error(typeof err.detail === "string" ? err.detail : `The AI astrologer is unavailable (${res.status}).`);
      }
      const reader = res.body.getReader(); const dec = new TextDecoder(); let buf = "";
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const events = buf.split("\n\n"); buf = events.pop() ?? "";
        for (const ev of events) {
          const line = ev.trim();
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (data === "[DONE]") continue;
          const o = JSON.parse(data) as { t?: string; e?: string };
          if (o.e) throw new Error(o.e);
          if (o.t) { got += o.t; put(got); }
        }
      }
      if (!got) throw new Error("No answer came back. Please try again.");
    } catch (e) {
      if ((e as Error).name === "AbortError") { if (!got) setMsgs((m) => m.slice(0, -2)); }
      else {
        toast(e instanceof Error ? e.message : "Assistant unavailable", "error");
        if (!got) { setMsgs((m) => m.slice(0, -2)); setQ(question); }
      }
    } finally { setBusy(false); abort.current = null; input.current?.focus(); }
  }, [busy, msgs, pid, summary, toast]);

  const submit = (e: FormEvent) => { e.preventDefault(); void ask(q); };

  if (phase !== "chat") {
    return (
      <>
        <AnimatePresence>
          {phase === "study" && (
            <CalcOverlay key="study" steps={STUDY_STEPS} ready={studyReady}
              title="Your astrologer is studying your Kundli" sub="Reading every placement, period and yoga before you ask"
              doneTitle="Ready for your questions" doneSub="Opening the consultation…"
              onDone={() => setPhase("chat")} />
          )}
        </AnimatePresence>
        <section className="ai-hero glass featured">
          <CrystalBall />
          <div className="ai-hero-copy">
            <p className="eyebrow">AI Astrologer</p>
            <h1 className="display">Seek guidance from <em>the stars</em></h1>
            <p className="lede">Your personal Vedic astrologer studies your full Kundli — every planet, house, dasha period, yoga and dosha — then answers in plain language. Ask anything, however you like: “How will my finances look in 10 years?”, “When is a good time to marry?”, “What remedies help my career?”</p>
            {loading ? <p className="muted small">Loading your charts…</p> : (
              <div className="ai-start">
                <label htmlFor="ctx" className="small muted">Whose chart should I read?</label>
                <div className="ai-start-row">
                  <select id="ctx" value={pid} onChange={(e) => setPid(e.target.value)}>
                    {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                    <option value="">General astrology question (no chart)</option>
                  </select>
                  <button className="btn btn-gold btn-lg" onClick={begin}>{pid ? "Begin consultation" : "Ask a general question"} <ArrowRight size={17} /></button>
                </div>
                {!profiles.length && <p className="small muted">No saved Kundli yet — <Link href="/kundli">create one</Link> for a personal reading.</p>}
              </div>
            )}
          </div>
        </section>
        <p className="fine center">Guidance for reflection — not medical, legal or financial advice.</p>
      </>
    );
  }

  return (
    <>
      <div className="ai-head">
        <CrystalBall thinking={busy} />
        <div className="ai-head-copy">
          <p className="eyebrow">AI Astrologer</p>
          <h2>{summary ? <>Reading for <em>{summary.name}</em></> : "General astrology guidance"}</h2>
          {summary && <div className="an-chips">
            <span className="an-chip">Lagna {summary.lagna}</span><span className="an-chip">Moon {summary.moon}</span>
            <span className="an-chip">{summary.nakshatra}</span>{summary.dasha && <span className="an-chip v">Dasha {summary.dasha}</span>}
          </div>}
        </div>
        <button className="btn btn-ghost btn-sm" onClick={() => { abort.current?.abort(); setPhase("intro"); setMsgs([]); }}><RotateCcw size={14} /> Change chart</button>
      </div>
      <div className="chat glass">
        <div ref={log} className="chat-log" aria-live="polite" data-lenis-prevent>
          {msgs.length === 0 && (
            <div className="chat-empty">
              <Sparkles size={26} aria-hidden />
              <p>{summary ? `I've studied ${summary.name.split(" ")[0]}'s chart. Ask anything — or start with one of these:` : "Ask any astrology question, or try:"}</p>
              <div className="chips">{SUGGEST.map((s) => <button key={s} className="chip" onClick={() => ask(s)}>{s}</button>)}</div>
            </div>
          )}
          {msgs.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              {m.role === "assistant"
                ? (m.content ? renderMd(m.content) : <span className="typing" aria-label="Consulting the chart"><i /><i /><i /> <span className="small muted">Consulting the chart…</span></span>)
                : m.content}
            </div>
          ))}
        </div>
        <form className="chat-input" onSubmit={submit}>
          <textarea ref={input} aria-label="Your question" rows={1} value={q} maxLength={2000}
            placeholder="Ask in your own words — e.g. “How will the next 5 years be for my marriage?”"
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void ask(q); } }} />
          {busy
            ? <button type="button" className="btn btn-ghost" onClick={() => abort.current?.abort()} aria-label="Stop"><Square size={15} /></button>
            : <button className="btn btn-gold" disabled={!q.trim()} aria-label="Send"><Send size={16} /></button>}
        </form>
      </div>
      <p className="fine center">Guidance for reflection — not medical, legal or financial advice.</p>
    </>
  );
}

export default function AssistantPage() { return <RequireAuth><Assistant /></RequireAuth>; }
