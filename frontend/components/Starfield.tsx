"use client";

import { useEffect, useRef } from "react";
import Constellations from "@/components/Constellations";

/**
 * GPU-cheap star field: stars are painted ONCE into three static layers;
 * parallax is a CSS transform per layer (compositor only), twinkle is a CSS opacity animation.
 * No per-frame canvas redraw — keeps scrolling smooth on integrated GPUs.
 */
const LAYERS = [
  { count: 260, size: [0.35, 0.9], alpha: [0.25, 0.6], depth: 0.04 },
  { count: 110, size: [0.6, 1.25], alpha: [0.45, 0.85], depth: 0.09 },
  { count: 34, size: [1.0, 1.8], alpha: [0.7, 1], depth: 0.16, gold: true },
];

function paint(w: number, h: number, l: (typeof LAYERS)[number], seed: number) {
  const c = document.createElement("canvas");
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  c.width = w * dpr; c.height = h * dpr;
  const ctx = c.getContext("2d")!;
  ctx.scale(dpr, dpr);
  let s = seed;
  const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < l.count; i++) {
    const r = l.size[0] + rnd() * (l.size[1] - l.size[0]);
    ctx.globalAlpha = l.alpha[0] + rnd() * (l.alpha[1] - l.alpha[0]);
    ctx.fillStyle = l.gold && rnd() > 0.4 ? "#f3dca4" : "#e8e6f5";
    ctx.beginPath();
    ctx.arc(rnd() * w, rnd() * h, r, 0, Math.PI * 2);
    ctx.fill();
  }
  return c.toDataURL("image/png");
}

export default function Starfield() {
  const refs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const tile = { w: Math.min(1400, window.innerWidth), h: Math.min(1000, window.innerHeight) };
    LAYERS.forEach((l, i) => {
      const el = refs.current[i];
      if (el) el.style.backgroundImage = `url(${paint(tile.w, tile.h, l, 1234 + i * 777)})`;
      if (el) { el.style.backgroundSize = `${tile.w}px ${tile.h}px`; el.style.inset = `-80px -120px -${tile.h + 80}px -120px`; }
    });
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.documentElement.dataset.reduceMotion === "true";
    if (reduce) return;
    let mx = 0, my = 0, raf = 0;
    const apply = () => {
      raf = 0;
      LAYERS.forEach((l, i) => {
        const el = refs.current[i];
        if (el) el.style.transform = `translate3d(${(mx * l.depth * 220).toFixed(1)}px, ${(my * l.depth * 160).toFixed(1)}px, 0)`;
      });
    };
    const queue = () => { if (!raf) raf = requestAnimationFrame(apply); };
    const onMove = (e: PointerEvent) => { mx = e.clientX / window.innerWidth - 0.5; my = e.clientY / window.innerHeight - 0.5; queue(); };
    window.addEventListener("pointermove", onMove, { passive: true });
    return () => { cancelAnimationFrame(raf); window.removeEventListener("pointermove", onMove); };
  }, []);

  return (
    <div className="sky" aria-hidden>
      <div className="nebula" />
      <Constellations />
      {LAYERS.map((_, i) => <div key={i} ref={(el) => { refs.current[i] = el; }} className={`stars stars-${i}`} />)}
    </div>
  );
}
