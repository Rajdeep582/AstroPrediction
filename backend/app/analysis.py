"""Kundli analysis: turns a calculated chart into a structured, readable report.

Every statement is derived from the chart produced by ``jyotish.build_chart`` using standard
Parashari rules (functional nature by lagna, dignity, house placement, Vimshottari dasha lords,
Avakhada/Panchang conventions). Nothing here alters calculated positions.
"""
from __future__ import annotations

from datetime import UTC, datetime

from . import jyotish as J

SIGNS = J.SIGNS
ORD = {1: "1st", 2: "2nd", 3: "3rd"}


def ordn(n: int) -> str:
    return ORD.get(n, f"{n}th")


# ───────── reference tables (standard Jyotish conventions) ─────────
SIGN_PROFILE = {
    "Aries": ("Fire", "Movable", "pioneering, direct and energetic", "initiative, courage, quick decisions", "impatience, impulsiveness, unfinished starts"),
    "Taurus": ("Earth", "Fixed", "steady, sensual and practical", "reliability, patience, building lasting value", "stubbornness, resistance to change, over-indulgence"),
    "Gemini": ("Air", "Dual", "curious, communicative and adaptable", "intellect, wit, versatility, networking", "restlessness, scattered focus, nervous tension"),
    "Cancer": ("Water", "Movable", "nurturing, intuitive and protective", "empathy, memory, care for family", "moodiness, over-sensitivity, holding on to the past"),
    "Leo": ("Fire", "Fixed", "dignified, generous and expressive", "leadership, confidence, creativity", "pride, need for recognition, rigidity"),
    "Virgo": ("Earth", "Dual", "analytical, precise and service-minded", "discernment, organisation, health awareness", "over-criticism, worry, perfectionism"),
    "Libra": ("Air", "Movable", "diplomatic, refined and fair-minded", "balance, aesthetics, partnership skills", "indecision, dependence on approval"),
    "Scorpio": ("Water", "Fixed", "intense, private and transformative", "depth, research, resilience in crisis", "secrecy, jealousy, holding grudges"),
    "Sagittarius": ("Fire", "Dual", "optimistic, principled and philosophical", "faith, teaching, love of learning and travel", "bluntness, over-promising, restlessness"),
    "Capricorn": ("Earth", "Movable", "ambitious, disciplined and responsible", "persistence, structure, long-term planning", "rigidity, pessimism, overwork"),
    "Aquarius": ("Air", "Fixed", "independent, humanitarian and inventive", "original thinking, social vision, detachment", "aloofness, contrarianism, emotional distance"),
    "Pisces": ("Water", "Dual", "compassionate, imaginative and spiritual", "intuition, kindness, artistic sensitivity", "escapism, vagueness, weak boundaries"),
}
LUCKY = {  # by lagna lord
    "Sun": ("Ruby", "Sunday", "Orange, gold", "1"), "Moon": ("Pearl", "Monday", "White, silver", "2"),
    "Mars": ("Red Coral", "Tuesday", "Red", "9"), "Mercury": ("Emerald", "Wednesday", "Green", "5"),
    "Jupiter": ("Yellow Sapphire", "Thursday", "Yellow", "3"), "Venus": ("Diamond / White Sapphire", "Friday", "White, pastel", "6"),
    "Saturn": ("Blue Sapphire", "Saturday", "Blue, black", "8"),
}
NAK_PROFILE = (
    ("Ashvini Kumaras", "Horse's head", "swift, healing and adventurous"), ("Yama", "Yoni", "intense, disciplined and creative"),
    ("Agni", "Razor / flame", "sharp, purifying and determined"), ("Brahma", "Chariot", "charming, artistic and prosperous"),
    ("Soma", "Deer's head", "curious, gentle and seeking"), ("Rudra", "Teardrop", "probing, transformative and emotional"),
    ("Aditi", "Quiver of arrows", "renewing, generous and optimistic"), ("Brihaspati", "Cow's udder", "nourishing, dutiful and wise"),
    ("Nagas", "Coiled serpent", "perceptive, strategic and secretive"), ("Pitris", "Royal throne", "noble, traditional and proud"),
    ("Bhaga", "Front legs of a bed", "pleasure-loving, warm and creative"), ("Aryaman", "Back legs of a bed", "helpful, loyal and principled"),
    ("Savitar", "Hand", "skilful, resourceful and witty"), ("Vishvakarma", "Pearl / gem", "artistic, stylish and inventive"),
    ("Vayu", "Young shoot in wind", "independent, flexible and diplomatic"), ("Indra-Agni", "Triumphal arch", "goal-driven, focused and ambitious"),
    ("Mitra", "Lotus", "devoted, friendly and organised"), ("Indra", "Earring / umbrella", "protective, senior and resourceful"),
    ("Nirriti", "Bundle of roots", "investigative, radical and spiritual"), ("Apas", "Fan / winnowing basket", "invincible, persuasive and proud"),
    ("Vishvadevas", "Elephant's tusk", "righteous, persistent and victorious"), ("Vishnu", "Ear", "attentive, learned and connected"),
    ("Vasus", "Drum", "musical, wealthy and generous"), ("Varuna", "Empty circle", "healing, secretive and philosophical"),
    ("Aja Ekapada", "Front of funeral cot", "passionate, idealistic and intense"), ("Ahir Budhnya", "Back of funeral cot", "wise, calm and disciplined"),
    ("Pushan", "Fish / drum", "nurturing, gentle and guiding"),
)
VARNA = {3: "Brahmin", 7: "Brahmin", 11: "Brahmin", 0: "Kshatriya", 4: "Kshatriya", 8: "Kshatriya", 1: "Vaishya", 5: "Vaishya", 9: "Vaishya", 2: "Shudra", 6: "Shudra", 10: "Shudra"}
VASHYA = ("Chatushpada", "Chatushpada", "Manava", "Jalachara", "Vanachara", "Manava", "Manava", "Keeta", "Manava / Chatushpada", "Chatushpada / Jalachara", "Manava", "Jalachara")
YONI = ("Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant")
GANA = ("Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya", "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva")
NADI = ("Adi (Vata)", "Madhya (Pitta)", "Antya (Kapha)")
SYLLABLES = ("Chu Che Cho La", "Li Lu Le Lo", "A I U E", "O Va Vi Vu", "Ve Vo Ka Ki", "Ku Gha Ng Chha", "Ke Ko Ha Hi", "Hu He Ho Da", "Di Du De Do",
             "Ma Mi Mu Me", "Mo Ta Ti Tu", "Te To Pa Pi", "Pu Sha Na Tha", "Pe Po Ra Ri", "Ru Re Ro Ta", "Ti Tu Te To", "Na Ni Nu Ne", "No Ya Yi Yu",
             "Ye Yo Bha Bhi", "Bhu Dha Pha Dha", "Bhe Bho Ja Ji", "Ju Je Jo Gha", "Ga Gi Gu Ge", "Go Sa Si Su", "Se So Da Di", "Du Tha Jha Na", "De Do Cha Chi")

PLANET_GOOD = {
    "Sun": "confidence, leadership, recognition and support from authority",
    "Moon": "emotional stability, public goodwill, comfort and nourishment",
    "Mars": "courage, energy, competitive success and gains through land or technical work",
    "Mercury": "sharp intellect, communication, trade and learning",
    "Jupiter": "wisdom, growth, good counsel, children and prosperity",
    "Venus": "harmony in relationships, comforts, creativity and refinement",
    "Saturn": "discipline, endurance, steady long-term achievement and seniority",
    "Rahu": "ambition, unconventional breakthroughs, foreign links and technology",
    "Ketu": "insight, research ability, spiritual depth and detachment from distractions",
}
PLANET_HARD = {
    "Sun": "ego clashes, friction with authority or father, and strain on vitality",
    "Moon": "mood swings, anxiety and changeability in home life",
    "Mars": "conflict, haste, accidents, inflammation and disputes over property",
    "Mercury": "nervous stress, miscommunication and indecision",
    "Jupiter": "over-optimism, over-expansion and misplaced trust",
    "Venus": "indulgence, relationship imbalances and overspending",
    "Saturn": "delays, heavy responsibility, isolation and fatigue",
    "Rahu": "confusion, restlessness, illusions and risky shortcuts",
    "Ketu": "sudden separations, lack of direction and losses that force inner change",
}
HOUSE_THEME = {1: "self, health and personal direction", 2: "finances, family and speech", 3: "initiative, siblings, skills and short travel", 4: "home, mother, property and peace of mind",
               5: "intelligence, children, creativity and romance", 6: "work routine, health, competition and debts", 7: "marriage, partnerships and business",
               8: "transformation, research, joint resources and sudden events", 9: "fortune, higher learning, father and dharma", 10: "career, status and public life",
               11: "income, gains, networks and ambitions", 12: "expenses, foreign lands, retreat and spiritual liberation"}
DIG_SCORE = {"exalted": 22, "moolatrikona": 16, "own": 14, "friendly": 6, "neutral": 0, "enemy": -8, "debilitated": -20}


# ───────── functional nature ─────────
def functional_role(c: dict, planet: str) -> dict:
    if planet in ("Rahu", "Ketu"):
        disp = J.P(c, planet)["sign_lord"]
        return {"role": "shadow", "rules": [], "label": f"Node — gives results of its dispositor {disp}", "score": 0}
    rules = [h for h in range(1, 13) if J.lord_of_house(c, h) == planet]
    s = set(rules)
    if s & {1, 4, 7, 10} - {1} and s & {5, 9}:
        return {"role": "yogakaraka", "rules": rules, "label": "Yogakaraka — rules a kendra and a trikona; the most auspicious planet for this lagna", "score": 18}
    if 1 in s:
        return {"role": "benefic", "rules": rules, "label": "Lagna lord — always supportive of the native", "score": 10}
    if s & {5, 9}:
        if s & {6, 8, 12}:
            return {"role": "mixed", "rules": rules, "label": "Mixed — rules a trikona and a dusthana", "score": 2}
        return {"role": "benefic", "rules": rules, "label": "Functional benefic — trikona lord", "score": 10}
    if s & {3, 6, 11} and not s & {1, 5, 9}:
        return {"role": "malefic", "rules": rules, "label": "Functional malefic — lord of trishadaya (3/6/11)", "score": -8}
    if 8 in s:
        return {"role": "malefic", "rules": rules, "label": "Functional malefic — 8th lord", "score": -8}
    if s & {4, 7, 10} and planet in J.BENEFICS:
        return {"role": "neutral", "rules": rules, "label": "Neutral — natural benefic owning a kendra (kendradhipati)", "score": 0}
    if s & {4, 7, 10}:
        return {"role": "benefic", "rules": rules, "label": "Mildly benefic — natural malefic owning a kendra", "score": 5}
    if s & {2, 12}:
        return {"role": "neutral", "rules": rules, "label": "Neutral — gives results by association (2nd/12th lord)", "score": 0}
    return {"role": "neutral", "rules": rules, "label": "Neutral", "score": 0}


def planet_strength(c: dict, name: str) -> int:
    p = J.P(c, name)
    fr = functional_role(c, name)
    s = 50 + DIG_SCORE[p["dignity"]] + fr["score"]
    s += 8 if p["house"] in J.KENDRA | J.TRIKONA else -10 if p["house"] in J.DUSTHANA else 3
    if p["combust"]:
        s -= 12
    sb = c.get("shadbala", {}).get("planets", {}).get(name)
    if sb:
        s += max(-12, min(12, round((sb["ratio"] - 1) * 25)))
    return max(5, min(98, round(s)))


def tone(score: int) -> str:
    return "excellent" if score >= 75 else "favourable" if score >= 60 else "mixed" if score >= 45 else "challenging"


# ───────── sections ─────────
def birth_panchang(c: dict) -> dict:
    sun, moon = J.P(c, "Sun")["absolute_longitude"], J.P(c, "Moon")["absolute_longitude"]
    diff = (moon - sun) % 360
    tithi, paksha = J.tithi_name(int(diff // 12))
    yoga = J.YOGAS27[int(((sun + moon) % 360) // (360 / 27))]
    karana = J.karana_name(int(diff // 6))
    local = datetime.fromisoformat(c["birth"]["local_datetime"])
    return {"tithi": f"{paksha} {tithi}", "yoga": yoga, "karana": karana, "vara": J.VARAS[(local.weekday() + 1) % 7],
            "note": "Weekday shown by civil date; traditional vara changes at sunrise."}


def avakhada(c: dict) -> list[dict]:
    m = J.P(c, "Moon")
    ni = J.NAKSHATRAS.index(m["nakshatra"])
    si = m["sign_index"]
    el = SIGN_PROFILE[m["sign"]][0]
    return [
        {"label": "Moon sign (Rashi)", "value": m["sign"], "hint": f"Lord {m['sign_lord']}"},
        {"label": "Nakshatra – Pada", "value": f"{m['nakshatra']} – {m['pada']}", "hint": f"Lord {m['nakshatra_lord']}"},
        {"label": "Varna", "value": VARNA[si], "hint": "Temperament class by Moon sign"},
        {"label": "Vashya", "value": VASHYA[si], "hint": "Nature of influence"},
        {"label": "Yoni", "value": YONI[ni], "hint": "Instinctive nature"},
        {"label": "Gana", "value": GANA[ni], "hint": "Deva / Manushya / Rakshasa"},
        {"label": "Nadi", "value": NADI[nadi_index(ni)], "hint": "Constitution (Ayurvedic dosha)"},
        {"label": "Tatva", "value": el, "hint": "Element of Moon sign"},
        {"label": "Name syllables", "value": SYLLABLES[ni].split()[m["pada"] - 1], "hint": f"All for {m['nakshatra']}: {SYLLABLES[ni]}"},
    ]


def nadi_index(ni: int) -> int:
    return (0, 1, 2, 2, 1, 0, 0, 1, 2)[ni % 9]


def sign_profile(sign: str, lord: str) -> dict:
    el, mod, nature, plus, minus = SIGN_PROFILE[sign]
    gem, day, colour, num = LUCKY[lord]
    return {"sign": sign, "lord": lord, "element": el, "modality": mod, "nature": nature, "strengths": plus, "challenges": minus,
            "lucky": {"gemstone": gem, "day": day, "colour": colour, "number": num}}


def planet_reading(c: dict, name: str) -> dict:
    p = J.P(c, name)
    fr = functional_role(c, name)
    score = planet_strength(c, name)
    h = p["house"]
    cond = []
    if p["retrograde"] and name not in ("Rahu", "Ketu"):
        cond.append("retrograde — results come through review, repetition or delay")
    if p["combust"]:
        cond.append("combust — its significations are overshadowed by the Sun")
    weak_dig = p["dignity"] in ("enemy", "debilitated") or p["combust"]
    text = (f"{name} occupies the {ordn(h)} house in {p['sign']} ({p['nakshatra']} pada {p['pada']}), where it is {J.DIG_WORD[p['dignity']]} ({p['dignity']}). "
            f"It focuses {name}'s energy on {HOUSE_THEME[h]}. ")
    if fr["rules"]:
        text += f"As lord of the {', '.join(ordn(x) for x in fr['rules'])} house{'s' if len(fr['rules']) > 1 else ''}, it links {' and '.join(HOUSE_THEME[x].split(',')[0] for x in fr['rules'])} to this area. "
    if score >= 62 and not weak_dig:
        text += f"Well placed, it supports {PLANET_GOOD[name]}."
    elif score >= 45:
        text += (f"Results are mixed: it can give {PLANET_GOOD[name]}, but "
                 + (f"its {'combustion' if p['combust'] else p['dignity'] + ' sign'} means" if weak_dig else "its functional role means")
                 + f" occasional {PLANET_HARD[name].split(',')[0]}.")
    else:
        text += f"Under strain, watch for {PLANET_HARD[name]}; conscious effort and remedies help."
    return {"planet": name, "house": h, "sign": p["sign"], "nakshatra": p["nakshatra"], "pada": p["pada"], "dignity": p["dignity"],
            "retrograde": p["retrograde"], "combust": p["combust"], "functional": fr, "score": score, "tone": tone(score),
            "conditions": cond, "interpretation": text}


def _period_score(c: dict, lord: str, sub: str | None = None) -> int:
    s = planet_strength(c, lord)
    if sub and sub != lord:
        rel = J.house_from(J.P(c, sub)["sign_index"], J.P(c, lord)["sign_index"])
        s = round(s * 0.6 + planet_strength(c, sub) * 0.4)
        s += 6 if rel in (1, 5, 9, 10, 11) else -6 if rel in (6, 8, 12) else 0
        s += 4 if J.relation(lord, sub) == "friend" else -4 if J.relation(lord, sub) == "enemy" else 0
    return max(5, min(98, s))


def _activated(c: dict, lord: str) -> list[int]:
    fr = functional_role(c, lord)
    hs = list(fr["rules"]) + [J.P(c, lord)["house"]]
    return sorted(set(hs))


AREA_HOUSES = {"Career & status": {10, 6, 11}, "Wealth & income": {2, 11, 5, 9}, "Marriage & partnerships": {7, 2, 5},
               "Health & vitality": {1, 6, 8}, "Home, mother & property": {4}, "Learning & children": {5, 9, 4},
               "Travel & foreign links": {3, 9, 12}, "Spiritual growth": {9, 12, 8}}
AREA_GOOD = {"Career & status": "recognition, promotions or a clear step up in responsibility", "Wealth & income": "steady earnings, savings and new income sources",
             "Marriage & partnerships": "harmony, commitment and supportive alliances", "Health & vitality": "good stamina and recovery",
             "Home, mother & property": "domestic comfort, property or vehicle gains", "Learning & children": "academic success, creativity and joy through children",
             "Travel & foreign links": "rewarding journeys and opportunities abroad", "Spiritual growth": "inner clarity, meaningful study and guidance from mentors"}
AREA_HARD = {"Career & status": "workplace pressure, changes of role or friction with seniors", "Wealth & income": "uneven cash flow; avoid speculation and large loans",
             "Marriage & partnerships": "misunderstandings that need patience and honest talk", "Health & vitality": "fatigue or recurring minor ailments; keep routines regular",
             "Home, mother & property": "domestic responsibilities or delays in property matters", "Learning & children": "distraction in studies or concerns over children",
             "Travel & foreign links": "tiring or unplanned travel and expenses away from home", "Spiritual growth": "restlessness that pushes you to look inward"}
NAT_KARAKA = {"Sun": "father, government, vitality", "Moon": "mother, mind, public", "Mars": "siblings, property, energy", "Mercury": "speech, trade, education",
              "Jupiter": "children, teachers, wealth", "Venus": "spouse, comforts, arts", "Saturn": "work, longevity, service", "Rahu": "foreign, technology, ambition", "Ketu": "spirituality, research, detachment"}


def _aspects_cast(c: dict, planet: str) -> list[int]:
    h = J.P(c, planet)["house"]
    return sorted({(h + x - 2) % 12 + 1 for x in J.aspects_houses(planet)})


def _conjunctions(c: dict, planet: str) -> list[str]:
    s = J.P(c, planet)["sign_index"]
    return [p["name"] for p in c["planets"] if p["sign_index"] == s and p["name"] != planet]


def life_effects(c: dict, lord: str, score: int, sub: str | None = None) -> list[dict]:
    acts = set(_activated(c, lord)) | (set(_activated(c, sub)) if sub else set())
    out = []
    for area, hs in AREA_HOUSES.items():
        hit = sorted(acts & hs)
        if not hit:
            continue
        hard = score < 50 or (all(x in J.DUSTHANA for x in hit) and area not in ("Spiritual growth", "Health & vitality"))
        t = "challenging" if hard and score < 45 else "mixed" if hard else "favourable" if score < 70 else "excellent"
        via = ", ".join(ordn(x) for x in hit)
        out.append({"area": area, "tone": t, "via": [ordn(x) for x in hit],
                    "text": ("Possible " + AREA_HARD[area] if hard else "Likely " + AREA_GOOD[area]) + f" (via the {via} house" + ("s" if len(hit) > 1 else "") + ")."})
    return out


def lord_profile(c: dict, lord: str) -> dict:
    p = J.P(c, lord)
    sb = c.get("shadbala", {}).get("planets", {}).get(lord)
    fr = functional_role(c, lord)
    l1 = c["ascendant"]["sign_lord"]
    rel_l1 = J.house_from(p["sign_index"], J.P(c, l1)["sign_index"]) if lord != l1 else 1
    dig = p["dignity"].title()
    if p["retrograde"] and lord not in ("Rahu", "Ketu"):
        dig += " · retrograde"
    if p["combust"]:
        dig += " · combust"
    link = "supportive" if rel_l1 in (1, 4, 5, 7, 9, 10, 11) else "demanding"
    facts = [
        {"label": "Placement", "value": f"{ordn(p['house'])} house · {p['sign']} {p['dms']}"},
        {"label": "Nakshatra", "value": f"{p['nakshatra']} pada {p['pada']} (lord {p['nakshatra_lord']})"},
        {"label": "Dignity", "value": dig},
        {"label": "Rules houses", "value": ", ".join(ordn(h) for h in fr["rules"]) or f"None (node; acts for {p['sign_lord']})"},
        {"label": "Aspects houses", "value": ", ".join(ordn(h) for h in _aspects_cast(c, lord))},
        {"label": "Conjunct with", "value": ", ".join(_conjunctions(c, lord)) or "None"},
        {"label": "Natural karaka of", "value": NAT_KARAKA[lord]},
        {"label": "From lagna lord", "value": f"{ordn(rel_l1)} from {l1}: {link} link with the self"},
    ]
    if sb:
        facts.append({"label": "Shadbala", "value": f"{sb['rupas']} / {sb['required']} rupas (" + ("strong" if sb["strong"] else "below required") + ")"})
    return {"facts": facts, "aspects": _aspects_cast(c, lord), "conjunctions": _conjunctions(c, lord)}


def lord_remedy(lord: str) -> dict:
    r = J.REMEDY_DB[lord]
    return {"mantra": r["mantra"], "count": r["count"], "day": r["day"], "charity": r["charity"], "practice": r["ritual"], "deity": r["deity"]}


def _ad_more(c: dict, lord: str, ad: dict, sc: int, birth) -> dict:
    al = ad["lord"]
    dist = J.house_from(J.P(c, al)["sign_index"], J.P(c, lord)["sign_index"])
    rel = J.relation(lord, al)
    pds = []
    for pd in ad.get("children", []):
        if datetime.fromisoformat(pd["end"]) < birth:
            continue
        ps = _period_score(c, al, pd["lord"])
        pds.append({"lord": pd["lord"], "start": pd["start"][:10], "end": pd["end"][:10], "current": pd["current"], "score": ps, "tone": tone(ps)})
    if dist in (1, 4, 5, 7, 9, 10):
        angle = "kendra/trikona: cooperative, results flow smoothly"
    elif dist in (6, 8, 12):
        angle = "6/8/12: friction, results come with effort"
    else:
        angle = "neutral angle"
    word = {"friend": "a friend", "enemy": "an enemy", "neutral": "neutral", "same": "itself"}[rel]
    day = J.REMEDY_DB[al]["day"]
    advice = (f"Lean into {PLANET_GOOD[al].split(',')[0]}; schedule important starts on {day}s." if sc >= 55
              else f"Go slow on major commitments; {al}'s remedy ({J.REMEDY_DB[al]['ritual'].lower()}) helps steady this phase.")
    return {"relationship": f"{al} is placed {ordn(dist)} from {lord} ({angle}). Natural relationship: {lord} regards {al} as {word}.",
            "effects": life_effects(c, lord, sc, al), "pratyantar": pds, "advice": advice}


def dasha_analysis(c: dict) -> list[dict]:
    now = datetime.now(UTC)
    birth = datetime.fromisoformat(c["birth"]["utc_datetime"])
    out = []
    for md in c["dasha"]["mahadashas"]:
        start, end = datetime.fromisoformat(md["start"]), datetime.fromisoformat(md["end"])
        if end < birth:
            continue
        lord = md["lord"]
        p = J.P(c, lord)
        score = _period_score(c, lord)
        acts = _activated(c, lord)
        fr = functional_role(c, lord)
        good = score >= 55
        summary = (f"{J.DASHA_THEMES[lord]} {lord} is {fr['label'].split(' — ')[0].lower()} for {c['ascendant']['sign']} lagna and sits in the {ordn(p['house'])} house "
                   f"({p['sign']}, {p['dignity']}), so this period activates {', '.join(HOUSE_THEME[h].split(',')[0] for h in acts)}.")
        highlights = [f"Growth in {HOUSE_THEME[h]}" for h in acts if h not in J.DUSTHANA][:3] or [f"Inner growth through {HOUSE_THEME[acts[0]]}"]
        cautions = [f"Pressure around {HOUSE_THEME[h]}" for h in acts if h in J.DUSTHANA][:2]
        if not good:
            cautions.append(f"{lord}'s weaker condition can bring {PLANET_HARD[lord]}")
        ads = []
        for ad in md.get("children", []):
            a_end = datetime.fromisoformat(ad["end"])
            if a_end < birth:
                continue
            sc = _period_score(c, lord, ad["lord"])
            sub_acts = _activated(c, ad["lord"])
            ads.append({"lord": ad["lord"], "start": ad["start"], "end": ad["end"], "current": ad["current"], "score": sc, "tone": tone(sc), "more": _ad_more(c, lord, ad, sc, birth),
                        "focus": [HOUSE_THEME[h].split(",")[0] for h in sub_acts][:3],
                        "summary": (f"{ad['lord']} sub-period within {lord}: brings {PLANET_GOOD[ad['lord']] if sc >= 55 else PLANET_HARD[ad['lord']]}, "
                                    f"working through {', '.join(HOUSE_THEME[h].split(',')[0] for h in sub_acts)}.")})
        age_from = max(0.0, (start - birth).days / J.YEAR_DAYS)
        out.append({"lord": lord, "start": md["start"], "end": md["end"], "years": md["years"], "age_from": round(age_from, 1), "age_to": round((end - birth).days / J.YEAR_DAYS, 1),
                    "current": md["current"], "past": end < now, "score": score, "tone": tone(score), "functional": fr["label"], "activates": acts,
                    "summary": summary, "highlights": highlights, "cautions": cautions, "antardashas": ads,
                    "more": {"effects": life_effects(c, lord, score), "remedy": lord_remedy(lord),
                             "houses": [{"house": h, "theme": HOUSE_THEME[h], "why": "occupied" if h == p["house"] else "ruled"} for h in acts],
                             "best_sub": max(ads, key=lambda x: x["score"])["lord"] if ads else None,
                             "hard_sub": min(ads, key=lambda x: x["score"])["lord"] if ads else None}})
        if (start - birth).days / J.YEAR_DAYS > 100:
            break
    return out


def key_predictions(c: dict, planets: list[dict], dashas: list[dict]) -> list[dict]:
    la = c["life_areas"]
    asc = c["ascendant"]
    sp = SIGN_PROFILE[asc["sign"]]
    l1 = J.P(c, asc["sign_lord"])
    moon = J.P(c, "Moon")
    cur = next((d for d in dashas if d["current"]), None)
    nxt = next((d for d in dashas if not d["past"] and not d["current"]), None)
    items = [{"area": "Personality", "score": planet_strength(c, asc["sign_lord"]),
              "text": f"With {asc['sign']} rising you come across as {sp[2]}. Your lagna lord {asc['sign_lord']} in the {ordn(l1['house'])} house directs life energy toward {HOUSE_THEME[l1['house']]}. "
                      f"The Moon in {moon['sign']} ({moon['nakshatra']}) gives a {NAK_PROFILE[J.NAKSHATRAS.index(moon['nakshatra'])][2]} emotional nature."}]
    for key, label in (("career", "Career"), ("finance", "Wealth"), ("relationships", "Marriage & relationships"), ("health", "Health"), ("education", "Education")):
        a = la[key]
        items.append({"area": label, "score": a["score"], "text": f"Outlook {a['outlook']}. {a['summary']}"})
    if cur:
        ad = next((x for x in cur["antardashas"] if x["current"]), None)
        items.append({"area": "Current period", "score": ad["score"] if ad else cur["score"],
                      "text": f"You are in {cur['lord']} Mahadasha" + (f" / {ad['lord']} Antardasha (until {ad['end'][:10]})" if ad else "") + f". {cur['summary']}"})
    if nxt:
        items.append({"area": "Next major period", "score": nxt["score"],
                      "text": f"{nxt['lord']} Mahadasha begins {nxt['start'][:10]} (age {nxt['age_from']:.0f}) and is expected to be {nxt['tone']}: {nxt['highlights'][0].lower()}."})
    return items


def build_analysis(c: dict) -> dict:
    asc = c["ascendant"]
    moon = J.P(c, "Moon")
    planets = [planet_reading(c, n) for n in J.NINE]
    dashas = dasha_analysis(c)
    ranked = sorted((p for p in planets if p["planet"] not in ("Rahu", "Ketu")), key=lambda x: -x["score"])
    ni = J.NAKSHATRAS.index(moon["nakshatra"])
    deity, symbol, nature = NAK_PROFILE[ni]
    present_yogas = [y for y in c["yogas"] if y["present"]]
    active_doshas = [d for d in c["doshas"] if d["present"]]
    yk = [p["planet"] for p in planets if p["functional"]["role"] == "yogakaraka"]
    return {
        "version": 1,
        "overview": {
            "headline": f"{asc['sign']} ascendant · {moon['sign']} Moon · {moon['nakshatra']} nakshatra",
            "strongest": [p["planet"] for p in ranked[:3]], "weakest": [p["planet"] for p in ranked[-2:]],
            "yogakaraka": yk, "yoga_count": len(present_yogas), "dosha_count": len(active_doshas),
            "overall": round(sum(a["score"] for a in c["life_areas"].values()) / len(c["life_areas"])),
        },
        "ascendant": sign_profile(asc["sign"], asc["sign_lord"]) | {"nakshatra": asc["nakshatra"], "pada": asc["pada"], "degree": asc["dms"]},
        "moon": sign_profile(moon["sign"], moon["sign_lord"]),
        "nakshatra": {"name": moon["nakshatra"], "pada": moon["pada"], "lord": moon["nakshatra_lord"], "deity": deity, "symbol": symbol, "nature": nature,
                      "gana": GANA[ni], "yoni": YONI[ni], "nadi": NADI[nadi_index(ni)]},
        "avakhada": avakhada(c),
        "panchang": birth_panchang(c),
        "predictions": key_predictions(c, planets, dashas),
        "planets": planets,
        "dashas": dashas,
        "lord_profiles": {n: lord_profile(c, n)["facts"] for n in J.NINE},
        "methodology": [
            f"Sidereal zodiac, {c['settings']['ayanamsa'].replace('_', ' ').title()} ayanamsa ({c['ayanamsa_degrees']:.4f}°), {c['settings']['node_type']} node.",
            f"Houses: {c['settings']['house_system'].replace('_', ' ')}; planetary positions from {c['engine']}.",
            "Vimshottari dasha from the Moon's nakshatra, year = 365.2425 days.",
            "Functional nature by lagna (Parashari), dignity, house placement and Shadbala combine into the strength scores shown.",
            "Interpretations describe tendencies for reflection — not certainties, and not medical, legal or financial advice.",
        ],
    }
