import type { Metadata } from "next";
import Link from "next/link";
import { PageHeader } from "@/components/ui";

export const metadata: Metadata = {
  title: "Learn Vedic Astrology",
  description: "Grahas, rashis, bhavas, nakshatras, divisional charts, Vimshottari dasha, yogas and doshas explained.",
};

const SECTIONS: { title: string; intro: string; items: [string, string][] }[] = [
  {
    title: "Grahas — the nine planets", intro: "Jyotish uses seven visible planets plus the lunar nodes. Each carries natural significations (karakatva).",
    items: [["Surya (Sun)", "Soul, authority, father, vitality, government."], ["Chandra (Moon)", "Mind, emotions, mother, public, nourishment."], ["Mangala (Mars)", "Energy, courage, siblings, land, surgery."], ["Budha (Mercury)", "Intellect, speech, commerce, skills."], ["Guru (Jupiter)", "Wisdom, children, wealth, teachers, dharma."], ["Shukra (Venus)", "Love, marriage, arts, comfort, vehicles."], ["Shani (Saturn)", "Discipline, longevity, labour, delay, karma."], ["Rahu", "North node: ambition, foreign, obsession, innovation."], ["Ketu", "South node: detachment, moksha, research, past-life skill."]],
  },
  {
    title: "Bhavas — the twelve houses", intro: "Houses map life areas. Kendras (1,4,7,10) give strength; trikonas (1,5,9) give fortune; dusthanas (6,8,12) bring challenge.",
    items: [["1 Lagna", "Self, body, temperament"], ["2 Dhana", "Wealth, family, speech"], ["3 Sahaja", "Courage, siblings, effort"], ["4 Sukha", "Mother, home, peace"], ["5 Putra", "Intellect, children, merit"], ["6 Ripu", "Enemies, illness, service"], ["7 Kalatra", "Spouse, partnership"], ["8 Randhra", "Longevity, transformation"], ["9 Dharma", "Fortune, father, guru"], ["10 Karma", "Career, status"], ["11 Labha", "Gains, networks"], ["12 Vyaya", "Loss, foreign, liberation"]],
  },
  {
    title: "Nakshatras", intro: "The zodiac divides into 27 lunar mansions of 13°20′, each with four padas of 3°20′. The Moon's nakshatra at birth fixes the starting Vimshottari dasha.",
    items: [["Lords cycle", "Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury — repeated three times across the 27."], ["Pada", "Each pada maps to one navamsa sign, linking nakshatra and D9."]],
  },
  {
    title: "Divisional charts (Vargas)", intro: "Each sign is subdivided to zoom into a life area. Parashara lists sixteen (Shodashavarga).",
    items: [["D1 Rashi", "Overall life"], ["D2 Hora", "Wealth"], ["D3 Drekkana", "Siblings"], ["D4 Chaturthamsa", "Property"], ["D7 Saptamsa", "Children"], ["D9 Navamsa", "Spouse, dharma — the most important after D1"], ["D10 Dasamsa", "Career"], ["D12 Dwadasamsa", "Parents"], ["D16 Shodasamsa", "Vehicles, comforts"], ["D20 Vimsamsa", "Spiritual life"], ["D24 Chaturvimsamsa", "Education"], ["D27 Bhamsa", "Strengths"], ["D30 Trimsamsa", "Misfortunes"], ["D40 / D45", "Maternal / paternal legacy"], ["D60 Shashtiamsa", "Past karma — needs accurate birth time"]],
  },
  {
    title: "Vimshottari dasha", intro: "A 120-year planetary period system. Each Mahadasha subdivides proportionally into Antardasha, Pratyantardasha and Sookshma.",
    items: [["Years", "Ketu 7 · Venus 20 · Sun 6 · Moon 10 · Mars 7 · Rahu 18 · Jupiter 16 · Saturn 19 · Mercury 17"], ["Reading", "Judge the dasha lord by its house, sign, dignity, lordship and strength; the sub-lord colours the result."]],
  },
  {
    title: "Yogas & doshas", intro: "Yogas are planetary combinations producing specific results; doshas are afflictions with classical cancellations.",
    items: [["Raja Yoga", "Kendra lord linked with trikona lord — status and power."], ["Gajakesari", "Jupiter in a kendra from the Moon — wisdom and reputation."], ["Pancha Mahapurusha", "Mars, Mercury, Jupiter, Venus or Saturn dignified in a kendra."], ["Manglik Dosha", "Mars in 1, 2, 4, 7, 8 or 12 — relationship friction; cancelled in several conditions."], ["Kaal Sarp", "All planets hemmed between Rahu and Ketu."], ["Sade Sati", "Saturn transiting 12th, 1st and 2nd from natal Moon — roughly 7½ years."]],
  },
];

export default function LearnPage() {
  return (
    <>
      <PageHeader eyebrow="Knowledge" title={<>Learn <em>Jyotish</em></>} sub="The concepts behind every number in your chart." actions={<Link href="/kundli" className="btn btn-gold">Apply to your chart</Link>} />
      <div className="learn">
        {SECTIONS.map((s) => (
          <section key={s.title} className="glass learn-sec">
            <h2 className="card-title">{s.title}</h2>
            <p className="body-sm">{s.intro}</p>
            <dl className="gloss">{s.items.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
          </section>
        ))}
      </div>
    </>
  );
}
