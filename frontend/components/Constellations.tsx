"use client";

import { useEffect, useRef } from "react";

/**
 * Animated constellation sky: real asterism shapes that slowly drift, glow, draw their
 * lines in and out, plus occasional shooting stars. Capped at ~30fps and paused when
 * the tab is hidden or the user prefers reduced motion.
 */
type Shape = { name: string; stars: [number, number, number][]; lines: [number, number][] };

// Star coordinates are normalised (0–1) inside each constellation's box; third value = magnitude weight.
const SHAPES: Shape[] = [
  { name: "Orion", stars: [[.2,.05,1],[.75,.1,.8],[.42,.45,.7],[.5,.48,.7],[.58,.51,.7],[.25,.92,.8],[.8,.88,1],[.48,.2,.5]],
    lines: [[0,7],[7,1],[0,2],[1,4],[2,3],[3,4],[2,5],[4,6]] },
  { name: "Ursa Major", stars: [[0,.3,.8],[.18,.35,.7],[.34,.42,.7],[.5,.48,.6],[.56,.75,.7],[.88,.8,.8],[.95,.5,.8]],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,3]] },
  { name: "Cassiopeia", stars: [[0,.3,.8],[.25,.75,.7],[.5,.4,.9],[.75,.8,.7],[1,.2,.8]],
    lines: [[0,1],[1,2],[2,3],[3,4]] },
  { name: "Cygnus", stars: [[.5,0,1],[.5,.4,.8],[.5,.75,.6],[.5,1,.7],[.05,.35,.6],[.95,.45,.6]],
    lines: [[0,1],[1,2],[2,3],[4,1],[1,5]] },
  { name: "Leo", stars: [[.15,.7,1],[.2,.4,.7],[.3,.15,.6],[.45,.1,.6],[.55,.35,.6],[.85,.45,.6],[1,.75,.8],[.6,.7,.5]],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,1],[4,5],[5,6],[6,7],[7,0]] },
  { name: "Scorpius", stars: [[0,.1,.6],[.1,.25,.7],[.2,.4,1],[.3,.55,.6],[.38,.75,.6],[.5,.9,.6],[.68,.95,.6],[.82,.85,.7],[.9,.7,.7]],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8]] },
  { name: "Lyra", stars: [[.5,0,1],[.35,.35,.6],[.65,.38,.6],[.3,.9,.6],[.7,.95,.6]],
    lines: [[0,1],[0,2],[1,2],[1,3],[2,4],[3,4]] },
  { name: "Gemini", stars: [[.15,0,.9],[.55,.05,1],[.2,.35,.6],[.6,.4,.6],[.1,.75,.6],[.5,.8,.6],[.3,1,.5],[.75,.95,.5]],
    lines: [[0,2],[2,4],[4,6],[1,3],[3,5],[5,7],[0,1]] },
];

type Live = { shape: Shape; x: number; y: number; size: number; rot: number; vx: number; vy: number; born: number; life: number; hue: number };
type Meteor = { x: number; y: number; vx: number; vy: number; t: number };

export default function Constellations() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current!;
    const ctx = canvas.getContext("2d")!;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.documentElement.dataset.reduceMotion === "true";
    const low = document.documentElement.dataset.perf === "low";
    const frameMs = low ? 66 : 40; // ~15fps low-end, ~25fps otherwise: slow drift needs no more
    let w = 0, h = 0, dpr = 1, raf = 0, last = 0, next = 0;
    const makeSprite = (rgb: string) => {
      const S = 64, cv = document.createElement("canvas"); cv.width = cv.height = S;
      const g = cv.getContext("2d")!, m = S / 2;
      const rg = g.createRadialGradient(m, m, 0, m, m, m);
      rg.addColorStop(0, "rgba(255,248,230,1)"); rg.addColorStop(0.1, "rgba(255,240,205,.95)");
      rg.addColorStop(0.16, `rgba(${rgb},.45)`); rg.addColorStop(0.45, `rgba(${rgb},.12)`); rg.addColorStop(1, "rgba(0,0,0,0)");
      g.fillStyle = rg; g.fillRect(0, 0, S, S);
      return cv;
    };
    const goldSprite = makeSprite("216,180,106"), violetSprite = makeSprite("155,134,255");
    const flareSprite = (() => {
      const S = 64, cv = document.createElement("canvas"); cv.width = cv.height = S;
      const g = cv.getContext("2d")!; g.strokeStyle = "rgba(255,236,190,1)"; g.lineWidth = 1;
      g.beginPath(); g.moveTo(4, 32); g.lineTo(60, 32); g.moveTo(32, 4); g.lineTo(32, 60); g.stroke();
      return cv;
    })();
    const live: Live[] = [];
    const meteors: Meteor[] = [];

    const resize = () => {
      dpr = low ? 1 : Math.min(window.devicePixelRatio || 1, 1.5);
      w = window.innerWidth; h = window.innerHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const spawn = (now: number, i?: number) => {
      const used = new Set(live.map((l) => l.shape.name));
      const pool = SHAPES.filter((s) => !used.has(s.name));
      const shape = pool[(i ?? Math.floor(Math.random() * 1e6)) % pool.length];
      const size = Math.min(w, h) * (0.16 + Math.random() * 0.12);
      // keep away from overlapping existing ones
      let x = 0, y = 0;
      for (let k = 0; k < 12; k++) {
        x = Math.random() * (w - size); y = Math.random() * (h - size);
        if (live.every((l) => Math.hypot(l.x - x, l.y - y) > size * 1.1)) break;
      }
      live.push({ shape, x, y, size, rot: (Math.random() - 0.5) * 0.5, vx: (Math.random() - 0.5) * 4, vy: (Math.random() - 0.5) * 3,
        born: now, life: 16000 + Math.random() * 10000, hue: Math.random() });
    };

    const draw = (now: number) => {
      ctx.clearRect(0, 0, w, h);
      const target = low ? (w < 700 ? 2 : 3) : w < 700 ? 3 : 5;
      while (live.length < target) spawn(now - (live.length ? 0 : 4000));

      for (let i = live.length - 1; i >= 0; i--) {
        const c = live[i];
        const age = (now - c.born) / c.life;
        if (age >= 1) { live.splice(i, 1); continue; }
        const fade = Math.min(1, age * 5, (1 - age) * 5);
        const drawn = Math.min(1, age * 3); // lines draw in over first third
        const dt = (now - c.born) / 1000;
        const ox = c.x + c.vx * dt, oy = c.y + c.vy * dt;
        const pts = c.shape.stars.map(([sx, sy, m]) => {
          const px = (sx - 0.5) * c.size, py = (sy - 0.5) * c.size;
          const cos = Math.cos(c.rot), sin = Math.sin(c.rot);
          return [ox + c.size / 2 + px * cos - py * sin, oy + c.size / 2 + px * sin + py * cos, m] as const;
        });
        const lineCol = c.hue > 0.5 ? "216,180,106" : "155,134,255";

        // lines: one path per constellation, flat colour (no per-segment gradients / shadows)
        ctx.lineWidth = 1;
        ctx.strokeStyle = `rgba(${lineCol},${0.42 * fade})`;
        ctx.beginPath();
        c.shape.lines.forEach(([a, b], li) => {
          const seg = Math.max(0, Math.min(1, drawn * c.shape.lines.length - li));
          if (!seg) return;
          const [ax, ay] = pts[a], [bx, by] = pts[b];
          ctx.moveTo(ax, ay); ctx.lineTo(ax + (bx - ax) * seg, ay + (by - ay) * seg);
        });
        ctx.stroke();

        // stars: pre-rendered glow sprite (gradient + bloom baked once), twinkle via alpha only
        const sprite = c.hue > 0.5 ? goldSprite : violetSprite;
        pts.forEach(([px, py, m], si) => {
          const tw = 0.7 + 0.3 * Math.sin(now / 600 + si * 1.7 + c.hue * 9);
          const r = (1.1 + m * 1.6) * 7;
          ctx.globalAlpha = fade * tw;
          ctx.drawImage(sprite, px - r, py - r, r * 2, r * 2);
          if (m >= 0.9) {
            ctx.globalAlpha = 0.35 * fade * tw;
            ctx.drawImage(flareSprite, px - r, py - r, r * 2, r * 2);
          }
        });
        ctx.globalAlpha = 1;
        if (fade > 0.6 && drawn >= 1) {
          ctx.font = "500 10px var(--font-sans), sans-serif"; ctx.letterSpacing = "3px";
          ctx.fillStyle = `rgba(216,200,160,${0.35 * (fade - 0.6) * 2.5})`;
          const [lx, ly] = pts[0];
          ctx.fillText(c.shape.name.toUpperCase(), lx + 10, ly - 10);
        }
      }

      // shooting stars
      if (!low && now > next) { next = now + 4000 + Math.random() * 7000;
        meteors.push({ x: Math.random() * w * 0.8 + w * 0.2, y: Math.random() * h * 0.4, vx: -(6 + Math.random() * 4), vy: 2.5 + Math.random() * 2, t: 0 }); }
      for (let i = meteors.length - 1; i >= 0; i--) {
        const s = meteors[i]; s.t += 1; s.x += s.vx; s.y += s.vy;
        const a = Math.max(0, 1 - s.t / 45);
        if (a <= 0) { meteors.splice(i, 1); continue; }
        const g = ctx.createLinearGradient(s.x, s.y, s.x - s.vx * 14, s.y - s.vy * 14);
        g.addColorStop(0, `rgba(255,244,214,${a})`); g.addColorStop(0.3, `rgba(216,180,106,${a * 0.6})`); g.addColorStop(1, "rgba(155,134,255,0)");
        ctx.strokeStyle = g; ctx.lineWidth = 1.6;
        ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(s.x - s.vx * 14, s.y - s.vy * 14); ctx.stroke();
      }
    };

    const loop = (now: number) => {
      raf = requestAnimationFrame(loop);
      if (now - last < frameMs || (window as Window & { __scrolling?: boolean }).__scrolling) return;
      last = now; draw(now);
    };

    resize();
    window.addEventListener("resize", resize);
    if (reduce) { for (let i = 0; i < 4; i++) spawn(-8000, i); draw(performance.now()); }
    else raf = requestAnimationFrame(loop);
    const onVis = () => { cancelAnimationFrame(raf); if (!document.hidden && !reduce) raf = requestAnimationFrame(loop); };
    document.addEventListener("visibilitychange", onVis);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", resize); document.removeEventListener("visibilitychange", onVis); };
  }, []);

  return <canvas ref={ref} className="constellations" aria-hidden />;
}
