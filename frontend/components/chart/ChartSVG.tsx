"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { PLANET_SHORT, SIGNS, SIGN_SHORT, type ChartStyle } from "@/lib/types";

export type ChartBody = { name: string; sign_index: number; house?: number; retrograde?: boolean; degree?: string; combust?: boolean; dignity?: string };
export type ChartSelection = { kind: "planet"; name: string } | { kind: "house"; house: number; sign: number };

type Props = {
  bodies: ChartBody[];
  ascSign: number;
  style: ChartStyle;
  title?: string;
  /** use explicit house numbers (bhava/chalit) instead of sign-derived houses (north style only) */
  useBodyHouses?: boolean;
  selected?: ChartSelection | null;
  onSelect?: (s: ChartSelection) => void;
  size?: number;
};

const S = 400;
type Pt = [number, number];
type Cell = { key: string; poly: Pt[]; label: Pt; sign: number; house: number };

const centroid = (p: Pt[]): Pt => [p.reduce((a, x) => a + x[0], 0) / p.length, p.reduce((a, x) => a + x[1], 0) / p.length];

function northCells(asc: number): Cell[] {
  const A: Pt = [0, 0], B: Pt = [S, 0], C: Pt = [S, S], D: Pt = [0, S], M: Pt = [200, 200];
  const T: Pt = [200, 0], R: Pt = [S, 200], Bm: Pt = [200, S], L: Pt = [0, 200];
  const P1: Pt = [100, 100], P2: Pt = [300, 100], P3: Pt = [300, 300], P4: Pt = [100, 300];
  const polys: Pt[][] = [[T, P2, M, P1], [A, T, P1], [A, P1, L], [L, P1, M, P4], [L, P4, D], [D, P4, Bm], [Bm, P4, M, P3], [Bm, P3, C], [C, P3, R], [R, P3, M, P2], [R, P2, B], [B, P2, T]];
  return polys.map((poly, i) => ({ key: `h${i + 1}`, poly, label: centroid(poly), house: i + 1, sign: (asc + i) % 12 }));
}

function southCells(asc: number): Cell[] {
  const pos: [number, number][] = [[1, 0], [2, 0], [3, 0], [3, 1], [3, 2], [3, 3], [2, 3], [1, 3], [0, 3], [0, 2], [0, 1], [0, 0]];
  const c = S / 4;
  return pos.map(([x, y], sign) => {
    const poly: Pt[] = [[x * c, y * c], [(x + 1) * c, y * c], [(x + 1) * c, (y + 1) * c], [x * c, (y + 1) * c]];
    return { key: `s${sign}`, poly, label: centroid(poly), sign, house: ((sign - asc + 12) % 12) + 1 };
  });
}

function eastCells(asc: number): Cell[] {
  const c = S / 3, k = 2 * c;
  const sq = (x: number, y: number): Pt[] => [[x, y], [x + c, y], [x + c, y + c], [x, y + c]];
  const polys: Pt[][] = [
    sq(c, 0), // Aries top-centre
    [[0, 0], [c, 0], [c, c]], // Taurus
    [[0, 0], [c, c], [0, c]], // Gemini
    sq(0, c), // Cancer
    [[0, k], [c, k], [0, S]], // Leo
    [[c, k], [c, S], [0, S]], // Virgo
    sq(c, k), // Libra
    [[k, k], [k, S], [S, S]], // Scorpio
    [[k, k], [S, k], [S, S]], // Sagittarius
    sq(k, c), // Capricorn
    [[k, c], [S, 0], [S, c]], // Aquarius
    [[k, 0], [S, 0], [k, c]], // Pisces
  ];
  return polys.map((poly, sign) => ({ key: `e${sign}`, poly, label: centroid(poly), sign, house: ((sign - asc + 12) % 12) + 1 }));
}

export default function ChartSVG({ bodies, ascSign, style, title, useBodyHouses, selected, onSelect, size }: Props) {
  const [hover, setHover] = useState<string | null>(null);
  const cells = useMemo(() => (style === "north" ? northCells(ascSign) : style === "south" ? southCells(ascSign) : eastCells(ascSign)), [style, ascSign]);

  const byCell = useMemo(() => {
    const map = new Map<string, ChartBody[]>();
    for (const b of bodies) {
      const cell = style === "north"
        ? cells.find((c) => c.house === (useBodyHouses && b.house ? b.house : ((b.sign_index - ascSign + 12) % 12) + 1))
        : cells.find((c) => c.sign === b.sign_index);
      if (!cell) continue;
      map.set(cell.key, [...(map.get(cell.key) ?? []), b]);
    }
    return map;
  }, [bodies, cells, style, ascSign, useBodyHouses]);

  const lines = useMemo(() => {
    if (style === "north") return ["M0 0L400 400", "M400 0L0 400", "M200 0L400 200L200 400L0 200Z"];
    if (style === "south") return ["M100 0V400", "M300 0V400", "M200 0V100", "M200 300V400", "M0 100H400", "M0 300H400", "M0 200H100", "M300 200H400"];
    return ["M133.3 0V400", "M266.7 0V400", "M0 133.3H400", "M0 266.7H400", "M0 0L133.3 133.3", "M400 0L266.7 133.3", "M0 400L133.3 266.7", "M400 400L266.7 266.7"];
  }, [style]);

  const isSel = (c: Cell) => selected?.kind === "house" && (style === "north" ? selected.house === c.house : selected.sign === c.sign);

  return (
    <figure className="chart-figure" style={size ? { maxWidth: size } : undefined}>
      <svg viewBox="-4 -4 408 408" role="group" aria-label={`${title ?? "Birth chart"}, ${style} Indian style, ascendant ${SIGNS[ascSign]}`}>
        <defs>
          <linearGradient id="chartGold" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="400" y2="400">
            <stop offset="0" stopColor="#f0d79c" /><stop offset="1" stopColor="#a8823f" />
          </linearGradient>
          <radialGradient id="chartBg" cx=".5" cy=".5" r=".7">
            <stop offset="0" stopColor="#1a1c34" /><stop offset="1" stopColor="#0b0c18" />
          </radialGradient>
        </defs>
        <rect x="0" y="0" width="400" height="400" rx="6" fill="url(#chartBg)" />
        {cells.map((c) => {
          const sel = isSel(c);
          const hov = hover === c.key;
          return (
            <polygon key={c.key} points={c.poly.map((p) => p.join(",")).join(" ")} className="chart-cell" data-selected={sel || undefined}
              fill={sel ? "rgba(216,180,106,.18)" : hov ? "rgba(216,180,106,.08)" : "transparent"}
              tabIndex={0} role="button" aria-label={`House ${c.house}, ${SIGNS[c.sign]}${(byCell.get(c.key) ?? []).length ? `: ${(byCell.get(c.key) ?? []).map((b) => b.name).join(", ")}` : ", empty"}`}
              onMouseEnter={() => setHover(c.key)} onMouseLeave={() => setHover(null)}
              onClick={() => onSelect?.({ kind: "house", house: c.house, sign: c.sign })}
              onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect?.({ kind: "house", house: c.house, sign: c.sign }); } }} />
          );
        })}
        <rect x="0" y="0" width="400" height="400" rx="6" fill="none" stroke="url(#chartGold)" strokeWidth="2" pointerEvents="none" />
        {lines.map((d, i) => (
          <motion.path key={`${style}-${i}`} d={d} fill="none" stroke="url(#chartGold)" strokeWidth="1.2" strokeOpacity=".85" pointerEvents="none"
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.9, delay: i * 0.06, ease: "easeInOut" }} />
        ))}
        {cells.map((c) => {
          const items = byCell.get(c.key) ?? [];
          const [cx, cy] = c.label;
          const isAsc = c.sign === ascSign;
          const tag = style === "north" ? String(c.sign + 1) : SIGN_SHORT[c.sign];
          const inner = c.poly.reduce((best, p) => (Math.hypot(p[0] - 200, p[1] - 200) < Math.hypot(best[0] - 200, best[1] - 200) ? p : best), c.poly[0]);
          const tagPos: Pt = style === "north" ? [cx + (inner[0] - cx) * 0.62, cy + (inner[1] - cy) * 0.62 + 4] : [c.poly[0][0] + 8, c.poly[0][1] + 16];
          const rows = Math.ceil(items.length / 2);
          const startY = cy - (rows - 1) * 9;
          return (
            <g key={`t${c.key}`} pointerEvents="none">
              {(style === "north" || c.poly.length === 4) && <text x={tagPos[0]} y={tagPos[1]} className="chart-sign" textAnchor={style === "north" ? "middle" : "start"}>{tag}</text>}
              {isAsc && (
                style === "north"
                  ? <text x={cx} y={cy - 38} className="chart-asc" textAnchor="middle">Asc</text>
                  : <text x={cx} y={c.poly.length === 4 ? c.poly[2][1] - 8 : cy + 30} className="chart-asc" textAnchor="middle">Asc</text>
              )}
              {items.map((b, i) => {
                const col = items.length > 2 ? (i % 2 ? 1 : -1) : 0;
                const row = items.length > 2 ? Math.floor(i / 2) : i;
                const x = cx + col * 20;
                const y = (items.length > 2 ? startY : cy - (items.length - 1) * 9) + row * 18 + 4;
                const sel = selected?.kind === "planet" && selected.name === b.name;
                return (
                  <motion.text key={b.name} x={x} y={y} textAnchor="middle" className={`chart-planet${sel ? " sel" : ""}${b.dignity === "exalted" ? " ex" : b.dignity === "debilitated" ? " deb" : ""}`}
                    initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 + i * 0.05 }}>
                    {PLANET_SHORT[b.name] ?? b.name.slice(0, 2)}{b.retrograde && !["Rahu", "Ketu"].includes(b.name) ? "ᴿ" : ""}{b.combust ? "°" : ""}
                    {b.degree && <tspan className="chart-deg" dx="2">{b.degree}</tspan>}
                  </motion.text>
                );
              })}
            </g>
          );
        })}
        {/* invisible planet hit targets */}
        {cells.flatMap((c) => {
          const items = byCell.get(c.key) ?? [];
          const [cx, cy] = c.label;
          const rows = Math.ceil(items.length / 2);
          const startY = cy - (rows - 1) * 9;
          return items.map((b, i) => {
            const col = items.length > 2 ? (i % 2 ? 1 : -1) : 0;
            const row = items.length > 2 ? Math.floor(i / 2) : i;
            const y = (items.length > 2 ? startY : cy - (items.length - 1) * 9) + row * 18;
            return (
              <rect key={`hit${b.name}`} x={cx + col * 20 - 15} y={y - 8} width="30" height="16" fill="transparent" style={{ cursor: "pointer" }}
                onClick={(e) => { e.stopPropagation(); onSelect?.({ kind: "planet", name: b.name }); }}>
                <title>{`${b.name}${b.degree ? ` ${b.degree}` : ""} — ${SIGNS[b.sign_index]}${b.retrograde && !["Rahu", "Ketu"].includes(b.name) ? " (R)" : ""}`}</title>
              </rect>
            );
          });
        })}
      </svg>
      {title && <figcaption>{title}</figcaption>}
    </figure>
  );
}
