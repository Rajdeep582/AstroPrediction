"use client";

import { Fragment, useState, type ReactNode } from "react";
import { ChevronDown } from "lucide-react";

const TERMS = /(\b(?:Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\b|\b(?:Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)\b|\b\d{1,2}(?:st|nd|rd|th)(?: house| lord)?\b|\b(?:exalted|debilitated|own sign|moolatrikona|retrograde|combust|yogakaraka|Mahadasha|Antardasha)\b)/g;

/** Highlights planets, signs, house numbers and key states so the eye can scan a paragraph. */
export function Hl({ text }: { text: string }) {
  const parts = text.split(TERMS);
  return <>{parts.map((p, i) => (i % 2 ? <mark key={i} className="kw">{p}</mark> : <Fragment key={i}>{p}</Fragment>))}</>;
}

const sentences = (t: string) => t.match(/[^.!?]+[.!?]+(?:\s|$)|[^.!?]+$/g)?.map((s) => s.trim()).filter(Boolean) ?? [t];

/**
 * Shows the first `keep` sentences (the gist); the rest sits behind "Know more".
 * Short texts render as-is with no button.
 */
export function ReadMore({ text, keep = 2, className = "" }: { text: string; keep?: number; className?: string }) {
  const [open, setOpen] = useState(false);
  const s = sentences(text);
  if (s.length <= keep) return <p className={`rd ${className}`}><Hl text={text} /></p>;
  return (
    <div className={`rd-wrap ${className}`}>
      <p className="rd"><Hl text={s.slice(0, keep).join(" ")} /></p>
      {open && <ul className="rd-more">{s.slice(keep).map((x) => <li key={x}><Hl text={x} /></li>)}</ul>}
      <MoreBtn open={open} onClick={() => setOpen((o) => !o)} />
    </div>
  );
}

export function MoreBtn({ open, onClick, label = "Know more", count }: { open: boolean; onClick: () => void; label?: string; count?: number }) {
  return (
    <button type="button" className={`more-btn${open ? " open" : ""}`} aria-expanded={open} onClick={onClick}>
      {open ? "Show less" : count ? `${label} (+${count})` : label} <ChevronDown size={14} />
    </button>
  );
}

/** Renders the first `show` items of a list; the remainder appears on "Know more". */
export function MoreList<T>({ items, show, render, className, label = "Show more" }: { items: T[]; show: number; render: (item: T, i: number) => ReactNode; className: string; label?: string }) {
  const [open, setOpen] = useState(false);
  const visible = open ? items : items.slice(0, show);
  return (
    <>
      <div className={className}>{visible.map(render)}</div>
      {items.length > show && <div className="more-row"><MoreBtn open={open} onClick={() => setOpen((o) => !o)} label={label} count={items.length - show} /></div>}
    </>
  );
}

/** Generic collapsible block for secondary details inside a card. */
export function Details({ children, label = "Know more" }: { children: ReactNode; label?: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      {open && <div className="rd-extra">{children}</div>}
      <MoreBtn open={open} onClick={() => setOpen((o) => !o)} label={label} />
    </>
  );
}
