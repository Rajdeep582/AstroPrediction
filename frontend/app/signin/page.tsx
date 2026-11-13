"use client";

import { Suspense, useEffect, useMemo, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Eye, EyeOff, Loader2, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/shell/AppShell";
import { useAuth, useToast } from "@/components/providers";

// Orion-like constellation, normalised 0..100
const STARS: [number, number, number][] = [[22, 18, 2.6], [70, 14, 2.2], [36, 44, 1.7], [46, 47, 2], [56, 50, 1.7], [26, 82, 2.4], [74, 86, 2.8], [46, 30, 1.2], [48, 64, 1.3], [12, 50, 1.1], [86, 48, 1.1]];
const LINKS: [number, number][] = [[0, 7], [1, 7], [7, 3], [2, 3], [3, 4], [2, 0], [4, 1], [2, 5], [4, 6], [3, 8], [0, 9], [1, 10]];

function Constellation() {
  return (
    <svg viewBox="0 0 100 100" className="constellation" aria-hidden>
      {LINKS.map(([a, b], i) => (
        <motion.line key={i} x1={STARS[a][0]} y1={STARS[a][1]} x2={STARS[b][0]} y2={STARS[b][1]} stroke="url(#cg)" strokeWidth=".25"
          initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 0.8 }} transition={{ duration: 0.9, delay: 0.15 + i * 0.05 }} />
      ))}
      {STARS.map(([x, y, r], i) => (
        <motion.circle key={i} cx={x} cy={y} r={r / 3} fill="#f6e2ad"
          initial={{ scale: 0, opacity: 0 }} animate={{ scale: [0, 1.4, 1], opacity: [0, 1, 0.9] }} transition={{ duration: 0.5, delay: i * 0.04 }}>
          <animate attributeName="opacity" values=".55;1;.55" dur={`${2.5 + (i % 4)}s`} repeatCount="indefinite" />
        </motion.circle>
      ))}
      <defs><linearGradient id="cg"><stop offset="0" stopColor="#e9cc8a" /><stop offset="1" stopColor="#8b7bd8" /></linearGradient></defs>
    </svg>
  );
}

function AuthForm() {
  const params = useSearchParams();
  const router = useRouter();
  const { user, signin, signup } = useAuth();
  const toast = useToast();
  const next = useMemo(() => { const n = params.get("next") || "/dashboard"; return n.startsWith("/") && !n.startsWith("//") ? n : "/dashboard"; }, [params]);
  const [mode, setMode] = useState<"signin" | "signup">(params.get("mode") === "signup" ? "signup" : "signin");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  useEffect(() => { if (user) router.replace(next); }, [user, next, router]);

  const v = {
    username: /^[A-Za-z0-9_.-]{3,32}$/.test(username) ? "" : "3–32 letters, digits, dot, dash or underscore",
    password: password.length < 4 ? "At least 4 characters" : mode === "signup" && password.length > 10 ? "At most 10 characters" : "",
    confirm: mode === "signin" || confirm === password ? "" : "Passwords don't match",
  };
  const strength = Math.min(4, [password.length >= 6, /[A-Z]/.test(password) && /[a-z]/.test(password), /\d/.test(password), /[^A-Za-z0-9]/.test(password) || password.length >= 9].filter(Boolean).length);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setTouched({ username: true, password: true, confirm: true });
    if (v.username || v.password || v.confirm) return;
    setBusy(true); setError("");
    try {
      await (mode === "signup" ? signup : signin)(username.trim(), password);
      toast(mode === "signup" ? "Welcome to Jyotish Studio" : "Signed in", "success");
      router.replace(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally { setBusy(false); }
  };

  const field = (id: "username" | "password" | "confirm", label: string, type: string, value: string, set: (s: string) => void, auto: string) => (
    <div className={`ffield${touched[id] && v[id] ? " invalid" : touched[id] && value ? " valid" : ""}`}>
      <input id={id} type={type} value={value} placeholder=" " autoComplete={auto} onChange={(e) => set(e.target.value)} onBlur={() => setTouched((t) => ({ ...t, [id]: true }))} aria-invalid={!!(touched[id] && v[id])} aria-describedby={`${id}-msg`} />
      <label htmlFor={id}>{label}</label>
      {id === "password" && <button type="button" className="eye" aria-label={show ? "Hide password" : "Show password"} onClick={() => setShow(!show)}>{show ? <EyeOff size={16} /> : <Eye size={16} />}</button>}
      <AnimatePresence>{touched[id] && v[id] && <motion.small id={`${id}-msg`} className="err" role="alert" initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>{v[id]}</motion.small>}</AnimatePresence>
    </div>
  );

  return (
    <motion.div className="auth-panel glass">
      <div className="seg seg-full" role="tablist" aria-label="Account">
        <button role="tab" aria-selected={mode === "signin"} onClick={() => { setMode("signin"); setError(""); }}>Sign in</button>
        <button role="tab" aria-selected={mode === "signup"} onClick={() => { setMode("signup"); setError(""); }}>Create account</button>
      </div>
      <AnimatePresence mode="wait">
        <motion.div key={mode} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.2 }}>
          <h1 className="auth-title">{mode === "signin" ? "Welcome back" : "Begin your chart"}</h1>
          <p className="muted">{mode === "signin" ? "Your saved charts and readings are waiting." : "Save profiles, history and AI conversations."}</p>
        </motion.div>
      </AnimatePresence>
      <form onSubmit={submit} noValidate className="stack-sm">
        {field("username", "Username", "text", username, setUsername, "username")}
        {field("password", "Password", show ? "text" : "password", password, setPassword, mode === "signup" ? "new-password" : "current-password")}
        {mode === "signup" && (
          <>
            <div className="strength" aria-label={`Password strength ${strength} of 4`}>{[0, 1, 2, 3].map((i) => <i key={i} className={i < strength ? `on s${strength}` : ""} />)}</div>
            {field("confirm", "Confirm password", show ? "text" : "password", confirm, setConfirm, "new-password")}
          </>
        )}
        {error && <div className="alert" role="alert">{error}</div>}
        <button className="btn btn-gold btn-block btn-lg" disabled={busy}>{busy ? <Loader2 size={17} className="spin" /> : <>{mode === "signin" ? "Sign in" : "Create account"} <ArrowRight size={17} /></>}</button>
      </form>
      <p className="fine center"><ShieldCheck size={13} aria-hidden /> Argon2-hashed passwords · HTTP-only session cookie</p>
    </motion.div>
  );
}

export default function SignInPage() {
  return (
    <div className="auth-split page-enter">
      <section className="auth-art" aria-hidden>
        <Constellation />
        <div className="auth-art-copy">
          <Brand />
          <h2 className="hero-title sm">As above, <em>so within.</em></h2>
          <p className="lede">Every chart is a map of a single moment. Yours begins here.</p>
        </div>
        <div className="orbit o1" /><div className="orbit o2" /><div className="orbit o3" />
      </section>
      <section className="auth-side">
        <Link href="/" className="back-link"><ArrowLeft size={15} /> Home</Link>
        <Suspense fallback={<div className="auth-panel glass" />}><AuthForm /></Suspense>
      </section>
    </div>
  );
}
