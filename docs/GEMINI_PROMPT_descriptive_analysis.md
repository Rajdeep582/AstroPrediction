# Prompt for Gemini — make the Kundli analysis text descriptive and human

Copy everything below the line into Gemini.

---

You are working on **Jyotish Studio** (repo root: `AstroPrediction/`), a Vedic astrology web app with a FastAPI backend (`backend/`) and a Next.js frontend (`frontend/`). After a user creates a Kundli, the page `/kundli/analysis` shows about ten sections: Summary/Predictions, Birth chart, Lagna & Moon & Nakshatra, Birth details (Avakhada), Planets, Dasha periods, Houses, Yogas & Doshas, Remedies and Method.

## Your one task

**Rewrite and expand the interpretive writing so an ordinary person with no astrology knowledge understands what their chart means for their life.**

The current text is too short, list-like and technical. Here is an example the owner is unhappy with, from the "Personality" prediction:

> "With Virgo rising you come across as analytical, precise and service-minded. Your lagna lord Mercury in the 8th house directs life energy toward transformation, research, joint resources and sudden events. The Moon in Taurus (Mrigashira) gives a curious, gentle and seeking emotional nature."

That is a list of facts with a few adjectives. The owner wants **real descriptive writing**: several sentences, ideally 2–4 short paragraphs per topic. The writing should explain what the combination means, how it tends to show up in everyday life (work, relationships, family, health, money and mindset), what the person's strengths are, what to watch out for, and practical guidance. It should read like a thoughtful, experienced astrologer explaining the chart warmly to a client.

### What "good" looks like (target quality for the same Personality item)

> **Paragraph 1 — who you are.** With Virgo rising, the first impression you give is of someone calm, observant and quietly capable. You notice details others miss, you like things done properly, and people often come to you when something needs sorting out. You are usually modest about your abilities, and you prefer being useful to being the centre of attention.
>
> **Paragraph 2 — the inner drive (lagna lord).** Your chart's ruling planet, Mercury, sits in the 8th house, the house of hidden matters and transformation. This gives your mind real depth. You are drawn to understand *why* things happen, whether through research, psychology, finance or the less visible side of life. You may go through a few major turning points that reshape your direction, and each one tends to leave you wiser and more resourceful.
>
> **Paragraph 3 — the emotional nature (Moon).** Emotionally, the Moon in Taurus in Mrigashira nakshatra makes you steady, affectionate and comfort-loving, but also curious and always searching for something a little more meaningful. You value security, good food, a peaceful home and loyal people around you.
>
> **Paragraph 4 — in practice.** Your biggest strengths are reliability, practical intelligence and patience. The main thing to watch is overthinking and worry, because your mind can keep turning a problem over long after it needs to. Routine, time in nature and talking things through help you most.

Every interpretive item in the app should reach roughly this depth and tone.

## Where the text lives (edit only these strings and templates)

All interpretive text is generated **deterministically in Python** from the calculated chart. There is no AI at runtime and you must not add any. Improve the templates and reference tables in these files:

1. `backend/app/analysis.py`
   - `SIGN_PROFILE`: Ascendant and Moon-sign profiles (nature, strengths, challenges). Expand each sign into richer phrases, or add new fields for full paragraphs (personality, relationships, career style, health tendencies, emotional nature).
   - `NAK_PROFILE`: 27 nakshatras (deity, symbol, nature). Add a descriptive paragraph for each nakshatra covering temperament, motivations, gifts and challenges.
   - `PLANET_GOOD` / `PLANET_HARD`, `HOUSE_THEME`, `AREA_GOOD` / `AREA_HARD`.
   - `planet_reading()` → `interpretation`
   - `key_predictions()` → the Summary cards: Personality, Career, Wealth, Marriage & relationships, Health, Education, Current period and Next major period. **This is the most visible part. Make each card a proper multi-paragraph reading.**
   - `dasha_analysis()` → `summary`, `highlights`, `cautions`, the Antardasha `summary`, `more.relationship`, `more.advice`, `life_effects()` text, and `plain`.
2. `backend/app/meanings.py`
   - `PLANET_IN_HOUSE` (9 planets × 12 houses, as (life, caution)). Expand each entry into 3–5 sentences: what it brings, how it shows up, and the caution.
   - `DIGNITY_NOTE`, `HOUSE_PLAIN`, `house_meaning()`, `DOSHA_PLAIN`, `YOGA_CATEGORY_PLAIN`, `yoga_meaning()`, `dasha_plain()`
3. `backend/app/jyotish.py`. Edit **only text-producing parts**, never calculation logic:
   - `DASHA_THEMES`, `dasha_interpretation()`, `HOUSE_SIG`, `PLANET_NATURE`
   - the `text` built in `house_analysis()`
   - the `summary` in `life_areas()` (Career, Finance, Health, Relationships, Education). Make these full paragraphs.
   - the `description` strings in `detect_yogas()`, and the `details` / `remedies` strings in `detect_doshas()`
   - remedy wording in `remedies()` / `REMEDY_DB`

## Hard rules: do NOT break these

1. **Keep every fact exactly as it is.** House numbers, signs, degrees, nakshatra and pada, planet names, dignity labels, scores, dates, ages, "Key houses 10, 6, 2, 11", "karaka(s) Sun, Saturn, Mercury" and the like stay present and unchanged. Put the facts first and your new descriptive interpretation **after** them in the same field or in a new field. Never remove or alter a calculated value.
2. **Do not touch any calculation.** Leave alone planet positions, ayanamsa, houses, dashas, yoga and dosha *detection conditions*, scores, Shadbala, Ashtakavarga, `functional_role()`, `planet_strength()` and `_period_score()`. Your work is wording only.
3. **Do not change the format.** Keep every existing JSON key and type, so the frontend keeps working. If you add new fields (for example `paragraphs: list[str]`), add them **alongside** the existing ones. If you add a new field, also add it to `frontend/lib/types.ts` and render it in `frontend/app/(app)/kundli/analysis/page.tsx`, using the existing `ReadMore`, `Details`, `Meaning` and `MoreList` components from `frontend/components/kundli/Readable.tsx`. Do not redesign the UI.
4. **The text must follow the chart.** Every sentence has to depend on the actual chart data (sign, house, dignity, functional role, strength/score tone, dasha lord and houses activated). Two different charts must read differently. Use the existing tone signals (`score`, `tone`: excellent / favourable / mixed / challenging, plus `dignity`, `combust`, `retrograde` and functional role) to choose between encouraging and cautionary wording. Never say something positive about a weak or debilitated placement without acknowledging the difficulty, and vice versa.
5. **Accuracy and sources.** Base meanings on standard classical Vedic sources: Brihat Parashara Hora Shastra (Bhava-phala and Dasha-phala chapters), Phaladeepika (esp. ch. 8 for planets in houses and the dasha chapters), Saravali, Jataka Parijata, and B.V. Raman's *How to Judge a Horoscope* and *Three Hundred Important Combinations*. Paraphrase them in modern plain English. Do not copy translations verbatim, and do not invent rules that contradict these texts.
6. **Responsible tone.** Describe tendencies, not certainties ("tends to", "you may notice", "this period favours"). No fear-mongering. Never predict death, specific illnesses, accidents or divorce as facts. For health, talk about areas to look after and healthy habits. Keep the existing disclaimer that it is not medical, legal or financial advice.
7. **Readable for anyone.** The first time a term appears (lagna, dasha, nakshatra, yoga, dosha, kendra, trikona, functional benefic, combust, retrograde, dignity), explain it in a short clause. Use short sentences, everyday words and second person ("you"). Each paragraph should be 2–5 sentences.
8. **Length.** The frontend shows the first 1–2 sentences and hides the rest behind "Know more", so long text is fine. Put the most important point in the first sentence. Targets:
   - **Summary prediction cards:** 3–4 paragraphs each.
   - **Planet readings:** 2–3 paragraphs (meaning, how it shows up, guidance).
   - **House readings:** 2 paragraphs.
   - **Mahadasha:** 3–4 paragraphs: overall feel; career and money; relationships and family; health and mindset; plus advice.
   - **Antardasha:** 1–2 paragraphs.
   - **Yogas and doshas:** 1–2 paragraphs each (what it is, how it affects life, what helps).
   - **Lagna, Moon and Nakshatra profiles:** 2–3 paragraphs each.
9. Keep it **deterministic and fast**. Use plain Python string templates and dictionaries, with no network calls and no heavy libraries. Building the chart must still take well under 200 ms.

## Section-by-section checklist

- [ ] **Summary → Personality:** a full portrait from lagna sign, lagna lord placement, Moon sign and nakshatra.
- [ ] **Summary → Career / Wealth / Marriage & relationships / Health / Education:** each explains what the relevant houses and karakas mean for this person, what is supportive, what needs care, and when (link it to the current or upcoming dasha if relevant).
- [ ] **Summary → Current period and Next major period:** what the phase will feel like, with practical guidance.
- [ ] **Lagna & Moon & Nakshatra:** descriptive profiles, not adjective lists.
- [ ] **Birth details (Avakhada):** add a one-to-two-sentence plain explanation of what each attribute (Varna, Vashya, Yoni, Gana, Nadi, Tatva) says about the person and why it matters (for example in marriage matching).
- [ ] **Planets (all 9):** a full reading per planet using sign, house, dignity, functional role and conditions.
- [ ] **Dasha periods:** a rich Mahadasha write-up plus an Antardasha write-up for each sub-period.
- [ ] **Houses (all 12):** what this life area looks like for the person, and why.
- [ ] **Yogas & Doshas:** what each one means in daily life, cancellation in plain words, and practical help.
- [ ] **Remedies:** why this planet needs support, and what the mantra, charity or practice is meant to do, explained gently.

## How to verify

1. Run the backend with `cd backend` then `.venv\Scripts\python run.py`, and the frontend with `cd frontend` then `npm run dev`. Or run `npm run dev` from the repo root.
2. Generate charts for at least three very different birth data sets, for example:
   - 2003-06-01 14:25 Asia/Kolkata, 22.69 N 88.44 E
   - 1985-11-20 06:10 Asia/Kolkata, 19.07 N 72.88 E
   - 1992-03-05 23:45 Europe/London, 51.51 N −0.13 E
   
   Confirm that the texts differ and match each chart.
3. Quick check in Python (from `backend/`):
   ```python
   from datetime import date, time
   from app import jyotish as J
   a = J.build_chart(date(2003,6,1), time(14,25), "Asia/Kolkata", 22.69, 88.44)["analysis"]
   for p in a["predictions"]: print(p["area"], "\n", p["text"], "\n")
   ```
4. `cd frontend` then `npx tsc --noEmit -p .` and `npx next build` must pass. Open `/kundli/analysis` on a phone-width screen (360 px) and confirm everything is readable and "Know more" expands the full text.
5. Confirm that no calculated value changed. Compare the `planets`, `ascendant`, `dasha` dates, `yogas[].present`, `doshas[].present` and all `score` values before and after your change for the same birth data. They must be identical.

Deliver: the updated files, plus a short note listing which text sources and tables you expanded.
