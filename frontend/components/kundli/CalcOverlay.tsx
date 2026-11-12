"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { motion } from "framer-motion";

export const CALC_STEPS = [
  "Converting birth time to UTC & Julian day",
  "Reading Swiss Ephemeris planetary positions",
  "Applying ayanamsa — sidereal zodiac",
  "Rising sign (Lagna) & house cusps",
  "Nakshatras, padas & dignities",
  "16 divisional charts (D1 – D60)",
  "Vimshottari Mahadasha & Antardasha",
  "Yogas, doshas & Shadbala strength",
  "Composing your Kundli analysis",
];

// Orion-like constellation drawn on the wheel; one star lights per completed step.
const STARS: [number, number][] = [[70, 52], [168, 60], [104, 112], [120, 118], [136, 124], [78, 190], [172, 182], [120, 74], [120, 150]];
const LINES: [number, number][] = [[0, 7], [7, 1], [0, 2], [1, 4], [2, 3], [3, 4], [3, 8], [2, 5], [4, 6]];

/**
 * Full-screen "analysing" sequence. Steps advance on a timer; the final step waits for `ready`
 * (the API result), then a completion glow plays and `onDone` fires.
 */
export default function CalcOverlay({ ready, onDone, name }: { ready: boolean; onDone: () => void; name?: string }) {
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);
  const last = CALC_STEPS.length - 1;

  useEffect(() => {
    if (step >= last) return;
    const t = setTimeout(() => setStep((s) => s + 1), 330 + Math.random() * 120);
    return () => clearTimeout(t);
  }, [step, last]);

  const doneRef = useRef(onDone);
  doneRef.current = onDone;
  useEffect(() => {
    if (step < last || !ready || done) return;
    const t = setTimeout(() => setDone(true), 450);
    return () => clearTimeout(t);
  }, [step, last, ready, done]);
  useEffect(() => {
    if (!done) return;
    const t = setTimeout(() => doneRef.current(), 1100);
    return () => clearTimeout(t);
  }, [done]);

  const lit = done ? STARS.length : Math.min(step, STARS.length);
  const pct = done ? 100 : Math.round((step / CALC_STEPS.length) * 100);

  if (typeof document === "undefined") return null;
  return createPortal(
    <motion.div className={`calc${done ? " done" : ""}`} role="status" aria-live="polite"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 1.04 }} transition={{ duration: 0.35 }}>
      <div className="calc-inner">
        <div className="calc-wheel" aria-hidden>
          <svg viewBox="0 0 240 240">
            <defs>
              <linearGradient id="calcGrad" x1="0" x2="1"><stop offset="0" stopColor="#fbe7b2" /><stop offset="1" stopColor="#9b86ff" /></linearGradient>
              <radialGradient id="calcCore"><stop offset="0" stopColor="rgba(233,199,125,.35)" /><stop offset="1" stopColor="rgba(111,82,224,0)" /></radialGradient>
            </defs>
            <circle cx="120" cy="120" r="118" fill="url(#calcCore)" />
            <g className="calc-ring">
              <circle cx="120" cy="120" r="112" fill="none" stroke="rgba(233,199,125,.35)" strokeDasharray="2 6" />
              {Array.from({ length: 12 }, (_, i) => {
                const a = (i * Math.PI) / 6;
                return <line key={i} x1={120 + Math.cos(a) * 100} y1={120 + Math.sin(a) * 100} x2={120 + Math.cos(a) * 112} y2={120 + Math.sin(a) * 112} stroke="rgba(233,199,125,.55)" />;
              })}
            </g>
            <g className="calc-ring r2"><circle cx="120" cy="120" r="92" fill="none" stroke="rgba(155,120,255,.35)" strokeDasharray="1 4" /></g>
            <g className="calc-orbit"><circle cx="120" cy="8" r="3.5" fill="#fbe7b2" /></g>
            {LINES.map(([a, b], i) => (
              <line key={i} pathLength={1} className={`calc-line${lit > Math.max(a, b) ? " lit" : ""}`} x1={STARS[a][0]} y1={STARS[a][1]} x2={STARS[b][0]} y2={STARS[b][1]} />
            ))}
            {STARS.map(([x, y], i) => <circle key={i} className={`calc-star${i < lit ? " lit" : ""}`} cx={x} cy={y} r={i === 0 || i === 6 ? 4 : 2.8} />)}
          </svg>
        </div>
        <h2>{done ? "Your Kundli is ready" : "Reading the sky at your birth"}</h2>
        <p className="muted small" style={{ margin: 0 }}>{done ? "Opening your analysis…" : name ? `Calculating ${name}'s chart with Swiss Ephemeris` : "Calculating with Swiss Ephemeris"}</p>
        <ul className="calc-steps">
          {CALC_STEPS.map((s, i) => {
            const state = done || i < step ? "ok" : i === step ? "active" : "";
            return <li key={s} className={state}><span className="dot">{state === "ok" ? "✓" : ""}</span>{s}</li>;
          })}
        </ul>
        <div className="calc-progress" aria-hidden><i style={{ width: `${pct}%` }} /></div>
      </div>
    </motion.div>,
    document.body,
  );
}
