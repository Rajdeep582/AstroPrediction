"""Vedic (sidereal) calculation engine built on Swiss Ephemeris.

Covers: positions, nakshatras, 16 vargas, house systems + chalit, Vimshottari (4 levels),
dignity/combustion, 30+ yogas, doshas, Ashtakavarga, approximate Shadbala, Gochar,
Panchang, Muhurta, festivals, Ashtakoota matching, numerology, interpretations, remedies.
"""
from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import swisseph as swe

try:
    from .config import SWISSEPH_EPHE_PATH
except ImportError:  # standalone tests
    SWISSEPH_EPHE_PATH = ""

EPHE = bool(SWISSEPH_EPHE_PATH and Path(SWISSEPH_EPHE_PATH).is_dir() and any(Path(SWISSEPH_EPHE_PATH).glob("*.se1")))
if EPHE:
    swe.set_ephe_path(SWISSEPH_EPHE_PATH)
BASE_FLAGS = swe.FLG_SWIEPH if EPHE else swe.FLG_MOSEPH
FLAGS = BASE_FLAGS | swe.FLG_SIDEREAL | swe.FLG_SPEED
YEAR_DAYS = 365.2425

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
SIGN_LORD = ("Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter")
PLANET_IDS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN}
SEVEN = tuple(PLANET_IDS)
NINE = SEVEN + ("Rahu", "Ketu")
AYANAMSA = {"lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN, "kp": swe.SIDM_KRISHNAMURTI, "yukteshwar": swe.SIDM_YUKTESHWAR, "fagan_bradley": swe.SIDM_FAGAN_BRADLEY}
HOUSE_CODES = {"placidus": b"P", "equal": b"E", "whole_sign": b"W", "kp": b"P"}
NAKSHATRAS = ("Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati")
DASHA_ORDER = ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
NAK_SPAN = 360 / 27
EXALT = {"Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15), "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20), "Rahu": (1, 20), "Ketu": (7, 20)}
OWN = {"Sun": {4}, "Moon": {3}, "Mars": {0, 7}, "Mercury": {2, 5}, "Jupiter": {8, 11}, "Venus": {1, 6}, "Saturn": {9, 10}, "Rahu": {10}, "Ketu": {7}}
MOOLATRIKONA = {"Sun": (4, 0, 20), "Moon": (1, 4, 30), "Mars": (0, 0, 12), "Mercury": (5, 16, 20), "Jupiter": (8, 0, 10), "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}
FRIENDS = {"Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"}, "Mars": {"Sun", "Moon", "Jupiter"}, "Mercury": {"Sun", "Venus"}, "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"}, "Saturn": {"Mercury", "Venus"}, "Rahu": {"Venus", "Saturn", "Mercury"}, "Ketu": {"Mars", "Venus", "Saturn"}}
ENEMIES = {"Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"}, "Mercury": {"Moon"}, "Jupiter": {"Mercury", "Venus"}, "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"}, "Rahu": {"Sun", "Moon", "Mars"}, "Ketu": {"Sun", "Moon"}}
COMBUST_ORB = {"Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11, "Venus": 10, "Saturn": 15}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
KENDRA, TRIKONA, DUSTHANA, UPACHAYA = {1, 4, 7, 10}, {1, 5, 9}, {6, 8, 12}, {3, 6, 10, 11}
SPECIAL_ASPECTS = {"Mars": (4, 7, 8), "Jupiter": (5, 7, 9), "Saturn": (3, 7, 10), "Rahu": (5, 7, 9), "Ketu": (5, 7, 9)}
VARGAS = (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)
VARGA_NAMES = {1: "Rashi", 2: "Hora", 3: "Drekkana", 4: "Chaturthamsa", 7: "Saptamsa", 9: "Navamsa", 10: "Dasamsa", 12: "Dwadasamsa", 16: "Shodasamsa", 20: "Vimsamsa", 24: "Chaturvimsamsa", 27: "Bhamsa", 30: "Trimsamsa", 40: "Khavedamsa", 45: "Akshavedamsa", 60: "Shashtiamsa"}
VARGA_AREA = {1: "Body, overall life", 2: "Wealth", 3: "Siblings, courage", 4: "Property, fortune", 7: "Children", 9: "Spouse, dharma", 10: "Career", 12: "Parents", 16: "Vehicles, comforts", 20: "Spiritual progress", 24: "Education", 27: "Strengths/weaknesses", 30: "Misfortunes", 40: "Maternal legacy", 45: "Paternal legacy", 60: "Past karma, overall"}


# ---------- basics ----------
def norm(x: float) -> float:
    return x % 360


def sign_of(lon: float) -> int:
    return int(norm(lon) // 30)


def house_from(sign: int, ref_sign: int) -> int:
    return (sign - ref_sign) % 12 + 1


def nakshatra(lon: float) -> dict:
    lon = norm(lon)
    i = int(lon // NAK_SPAN)
    within = lon - i * NAK_SPAN
    return {"index": i, "name": NAKSHATRAS[i], "pada": int(within // (NAK_SPAN / 4)) + 1, "lord": DASHA_ORDER[i % 9], "fraction_elapsed": within / NAK_SPAN}


def dms(deg: float) -> str:
    d = int(deg)
    m_full = (deg - d) * 60
    m = int(m_full)
    s = int(round((m_full - m) * 60))
    if s == 60:
        m, s = m + 1, 0
    return f"{d}°{m:02d}'{s:02d}\""


def jd_from_local(d: date, t, tz: str) -> tuple[float, datetime, datetime]:
    local = datetime.combine(d, t, tzinfo=ZoneInfo(tz))
    utc = local.astimezone(UTC)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    return swe.julday(utc.year, utc.month, utc.day, hour), local, utc


def jd_from_dt(dt: datetime) -> float:
    u = dt.astimezone(UTC)
    return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)


def dt_from_jd(jd: float, tz: str = "UTC") -> datetime:
    y, m, d, h = swe.revjul(jd)
    base = datetime(y, m, d, tzinfo=UTC) + timedelta(hours=h)
    return base.astimezone(ZoneInfo(tz))


# ---------- positions ----------
def planet_positions(jd: float, ayanamsa: str = "lahiri", node: str = "true") -> dict[str, dict]:
    swe.set_sid_mode(AYANAMSA.get(ayanamsa, swe.SIDM_LAHIRI))
    out = {}
    for name, pid in PLANET_IDS.items():
        xx, _ = swe.calc_ut(jd, pid, FLAGS)
        out[name] = {"lon": norm(xx[0]), "speed": xx[3], "lat": xx[1]}
    nx, _ = swe.calc_ut(jd, swe.TRUE_NODE if node == "true" else swe.MEAN_NODE, FLAGS)
    out["Rahu"] = {"lon": norm(nx[0]), "speed": nx[3], "lat": 0.0}
    out["Ketu"] = {"lon": norm(nx[0] + 180), "speed": nx[3], "lat": 0.0}
    return out


def houses(jd: float, lat: float, lon: float, system: str = "placidus") -> tuple[list[float], float, float]:
    code = HOUSE_CODES.get(system, b"P")
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, code, swe.FLG_SIDEREAL)
    except swe.Error:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"E", swe.FLG_SIDEREAL)
    cusps = list(cusps)[-12:]
    return [norm(c) for c in cusps], norm(ascmc[0]), norm(ascmc[1])


# ---------- dignity ----------
def dignity(planet: str, lon: float) -> str:
    s, deg = sign_of(lon), norm(lon) % 30
    if planet in MOOLATRIKONA:
        ms, a, b = MOOLATRIKONA[planet]
        if s == ms and a <= deg < b:
            return "moolatrikona"
    if planet in EXALT and EXALT[planet][0] == s:
        return "exalted"
    if planet in EXALT and (EXALT[planet][0] + 6) % 12 == s:
        return "debilitated"
    if s in OWN.get(planet, ()):
        return "own"
    lord = SIGN_LORD[s]
    if lord in FRIENDS.get(planet, ()):
        return "friendly"
    if lord in ENEMIES.get(planet, ()):
        return "enemy"
    return "neutral"


def relation(a: str, b: str) -> str:
    if a == b:
        return "same"
    if b in FRIENDS.get(a, ()):
        return "friend"
    if b in ENEMIES.get(a, ()):
        return "enemy"
    return "neutral"


# ---------- vargas ----------
def varga_sign(lon: float, n: int) -> int:
    lon = norm(lon)
    s, deg = int(lon // 30), lon % 30
    odd = s % 2 == 0  # Aries = odd sign
    mod = s % 3  # 0 movable, 1 fixed, 2 dual
    if n == 1:
        return s
    p = int(deg // (30 / n))
    if n == 2:
        first = deg < 15
        return (4 if first else 3) if odd else (3 if first else 4)
    if n == 3:
        return (s + 4 * p) % 12
    if n == 4:
        return (s + 3 * p) % 12
    if n == 7:
        return (s + p) % 12 if odd else (s + 6 + p) % 12
    if n == 9:
        return int(lon // (10 / 3)) % 12
    if n == 10:
        return (s + p) % 12 if odd else (s + 8 + p) % 12
    if n == 12:
        return (s + p) % 12
    if n == 16:
        return ((0, 4, 8)[mod] + p) % 12
    if n == 20:
        return ((0, 8, 4)[mod] + p) % 12
    if n == 24:
        return ((4 if odd else 3) + p) % 12
    if n == 27:
        return (s * 27 + p) % 12
    if n == 30:
        if odd:
            for lim, sg in ((5, 0), (10, 10), (18, 8), (25, 2), (30, 6)):
                if deg < lim:
                    return sg
        for lim, sg in ((5, 1), (12, 5), (20, 11), (25, 9), (30, 7)):
            if deg < lim:
                return sg
    if n == 40:
        return ((0 if odd else 6) + p) % 12
    if n == 45:
        return ((0, 4, 8)[mod] + p) % 12
    if n == 60:
        return (s + p) % 12
    raise ValueError(f"Unsupported varga D{n}")


def varga_chart(points: dict[str, float], n: int) -> dict:
    asc = varga_sign(points["Ascendant"], n)
    placements = {k: varga_sign(v, n) for k, v in points.items()}
    return {"division": n, "name": VARGA_NAMES[n], "signifies": VARGA_AREA[n], "ascendant_sign": asc,
            "placements": [{"name": k, "sign": SIGNS[s], "sign_index": s, "house": house_from(s, asc)} for k, s in placements.items() if k != "Ascendant"]}


# ---------- aspects ----------
def aspects_houses(planet: str) -> tuple[int, ...]:
    return SPECIAL_ASPECTS.get(planet, (7,))


def aspected_by(chart: dict, house: int) -> list[str]:
    res = []
    for p in chart["planets"]:
        for a in aspects_houses(p["name"]):
            if (p["house"] + a - 2) % 12 + 1 == house:
                res.append(p["name"])
    return res


# ---------- Vimshottari ----------
def _sub_periods(lord: str, start: datetime, years: float, level: int, max_level: int, now: datetime, expand_current_only: bool) -> list[dict]:
    out = []
    i = DASHA_ORDER.index(lord)
    t = start
    for k in range(9):
        sub = DASHA_ORDER[(i + k) % 9]
        span = years * DASHA_YEARS[sub] / 120
        end = t + timedelta(days=span * YEAR_DAYS)
        node = {"lord": sub, "start": t.isoformat(), "end": end.isoformat(), "years": round(span, 4), "level": level, "current": t <= now < end}
        if level < max_level and (not expand_current_only or node["current"] or level < 3):
            node["children"] = _sub_periods(sub, t, span, level + 1, max_level, now, expand_current_only)
        out.append(node)
        t = end
    return out


def vimshottari(moon_lon: float, birth_utc: datetime, now: datetime | None = None, max_level: int = 4) -> dict:
    now = now or datetime.now(UTC)
    nk = nakshatra(moon_lon)
    lord = nk["lord"]
    total = DASHA_YEARS[lord]
    elapsed = nk["fraction_elapsed"] * total
    start = birth_utc - timedelta(days=elapsed * YEAR_DAYS)
    periods = []
    t = start
    i = DASHA_ORDER.index(lord)
    for k in range(18):  # two full cycles = 240 y
        md = DASHA_ORDER[(i + k) % 9]
        yrs = DASHA_YEARS[md]
        end = t + timedelta(days=yrs * YEAR_DAYS)
        node = {"lord": md, "start": t.isoformat(), "end": end.isoformat(), "years": yrs, "level": 1, "current": t <= now < end}
        node["children"] = _sub_periods(md, t, yrs, 2, max_level, now, True)
        periods.append(node)
        t = end
        if t > birth_utc + timedelta(days=125 * YEAR_DAYS):
            break
    current = []
    level = periods
    while level:
        cur = next((p for p in level if p["current"]), None)
        if not cur:
            break
        current.append({"lord": cur["lord"], "start": cur["start"], "end": cur["end"], "level": cur["level"]})
        level = cur.get("children")
    return {"system": "Vimshottari", "balance_at_birth": {"lord": lord, "years": round(total - elapsed, 4)},
            "mahadashas": periods, "current": current, "levels": ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma"]}


# ---------- main chart ----------
def build_chart(birth_date: date, birth_time, tz: str, lat: float, lon: float, ayanamsa: str = "lahiri", node: str = "true", house_system: str = "whole_sign") -> dict:
    jd, local, utc = jd_from_local(birth_date, birth_time, tz)
    pos = planet_positions(jd, ayanamsa, node)
    cusps, asc, mc = houses(jd, lat, lon, "placidus" if house_system in ("whole_sign",) else house_system)
    asc_sign = sign_of(asc)
    sun = pos["Sun"]["lon"]
    planets = []
    for name in NINE:
        p = pos[name]
        s = sign_of(p["lon"])
        nk = nakshatra(p["lon"])
        combust = False
        if name in COMBUST_ORB:
            diff = abs((p["lon"] - sun + 180) % 360 - 180)
            orb = COMBUST_ORB[name] - (2 if name in ("Mercury", "Venus") and p["speed"] < 0 else 0)
            combust = diff < orb
        planets.append({
            "name": name, "absolute_longitude": round(p["lon"], 6), "longitude": round(p["lon"] % 30, 6), "dms": dms(p["lon"] % 30),
            "sign": SIGNS[s], "sign_index": s, "sign_lord": SIGN_LORD[s], "house": house_from(s, asc_sign),
            "nakshatra": nk["name"], "pada": nk["pada"], "nakshatra_lord": nk["lord"],
            "retrograde": p["speed"] < 0 if name not in ("Rahu", "Ketu") else True, "speed": round(p["speed"], 5),
            "dignity": dignity(name, p["lon"]), "combust": combust,
        })
    # Bhava chalit by cusp ranges (Placidus/Equal/KP); whole sign = rashi house
    chalit_cusps = cusps if house_system != "whole_sign" else [norm(asc_sign * 30 + i * 30) for i in range(12)]
    for pl in planets:
        pl["bhava"] = _bhava_of(pl["absolute_longitude"], chalit_cusps)
    asc_nk = nakshatra(asc)
    points = {p["name"]: p["absolute_longitude"] for p in planets}
    points["Ascendant"] = asc
    vargas = {f"D{n}": varga_chart(points, n) for n in VARGAS}
    chart = {
        "birth": {"local_datetime": local.isoformat(), "utc_datetime": utc.isoformat(), "timezone": tz, "latitude": lat, "longitude": lon, "julian_day": jd},
        "ascendant": {"sign": SIGNS[asc_sign], "sign_index": asc_sign, "absolute_longitude": round(asc, 6), "longitude": round(asc % 30, 6), "dms": dms(asc % 30), "nakshatra": asc_nk["name"], "pada": asc_nk["pada"], "nakshatra_lord": asc_nk["lord"], "sign_lord": SIGN_LORD[asc_sign]},
        "midheaven": round(mc, 6),
        "planets": planets,
        "house_cusps": [round(c, 6) for c in chalit_cusps],
        "houses": [{"house": h, "sign": SIGNS[(asc_sign + h - 1) % 12], "lord": SIGN_LORD[(asc_sign + h - 1) % 12], "cusp": round(chalit_cusps[h - 1], 4), "occupants": [p["name"] for p in planets if p["house"] == h]} for h in range(1, 13)],
        "vargas": vargas,
        "ayanamsa_degrees": round(swe.get_ayanamsa_ut(jd), 6),
        "settings": {"ayanamsa": ayanamsa, "node_type": node, "house_system": house_system, "zodiac": "sidereal"},
        "engine": "Swiss Ephemeris (files)" if EPHE else "Swiss Ephemeris (Moshier)",
    }
    moon = next(p for p in planets if p["name"] == "Moon")
    chart["moon_sign"] = moon["sign"]
    chart["birth_nakshatra"] = {"name": moon["nakshatra"], "pada": moon["pada"], "lord": moon["nakshatra_lord"]}
    chart["dasha"] = vimshottari(moon["absolute_longitude"], utc)
    chart["yogas"] = detect_yogas(chart)
    chart["doshas"] = detect_doshas(chart)
    chart["ashtakavarga"] = ashtakavarga(chart)
    chart["shadbala"] = shadbala(chart, pos, jd, lat, lon)
    chart["house_analysis"] = house_analysis(chart)
    chart["life_areas"] = life_areas(chart)
    chart["remedies"] = remedies(chart)
    chart["transits"] = gochar(chart)
    for md in chart["dasha"]["mahadashas"]:
        md["interpretation"] = dasha_interpretation(chart, md["lord"])
        for ad in md.get("children", []):
            ad["interpretation"] = dasha_interpretation(chart, md["lord"], ad["lord"])
    from .analysis import build_analysis
    chart["analysis"] = build_analysis(chart)
    return chart


def _bhava_of(lon: float, cusps: list[float]) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        span = (b - a) % 360
        if (lon - a) % 360 < span:
            return i + 1
    return 1


def P(chart: dict, name: str) -> dict:
    return next(p for p in chart["planets"] if p["name"] == name)


def lord_of_house(chart: dict, h: int) -> str:
    return SIGN_LORD[(chart["ascendant"]["sign_index"] + h - 1) % 12]


# ---------- yogas ----------
def detect_yogas(c: dict) -> list[dict]:
    Y = []

    def add(name, cat, present, desc, strength="medium"):
        Y.append({"name": name, "category": cat, "present": bool(present), "description": desc, "strength": strength if present else None})

    h = {p["name"]: p["house"] for p in c["planets"]}
    sg = {p["name"]: p["sign_index"] for p in c["planets"]}
    dig = {p["name"]: p["dignity"] for p in c["planets"]}
    moon_s = sg["Moon"]
    from_moon = {k: house_from(v, moon_s) for k, v in sg.items()}
    occ = {i: [p for p in SEVEN + ("Rahu", "Ketu") if h[p] == i] for i in range(1, 13)}
    real7 = [p for p in SEVEN if p not in ("Sun", "Moon")]
    lord = {i: lord_of_house(c, i) for i in range(1, 13)}

    def conj(a, b):
        return sg[a] == sg[b]

    def mutual_aspect_or_conj(a, b):
        if conj(a, b):
            return True
        return any((h[a] + x - 2) % 12 + 1 == h[b] for x in aspects_houses(a)) and any((h[b] + x - 2) % 12 + 1 == h[a] for x in aspects_houses(b))

    def exchange(a, b):
        return a != b and SIGN_LORD[sg[a]] == b and SIGN_LORD[sg[b]] == a

    # Pancha Mahapurusha
    for pl, nm in (("Mars", "Ruchaka"), ("Mercury", "Bhadra"), ("Jupiter", "Hamsa"), ("Venus", "Malavya"), ("Saturn", "Shasha")):
        add(f"{nm} Yoga", "Pancha Mahapurusha", h[pl] in KENDRA and dig[pl] in ("own", "exalted", "moolatrikona"), f"{pl} in own/exalted sign in a kendra: eminence through {pl}'s significations.", "strong")
    add("Gajakesari Yoga", "Lunar", from_moon["Jupiter"] in KENDRA, "Jupiter in a kendra from Moon: wisdom, reputation, lasting prosperity.", "strong")
    add("Budhaditya Yoga", "Solar", conj("Sun", "Mercury") and not P(c, "Mercury")["combust"], "Sun and Mercury together (Mercury not combust): intelligence, communication skill.")
    add("Chandra-Mangala Yoga", "Wealth", conj("Moon", "Mars") or (from_moon["Mars"] == 7), "Moon with/opposite Mars: earning power, enterprise.")
    add("Guru-Mangala Yoga", "Wealth", mutual_aspect_or_conj("Jupiter", "Mars"), "Jupiter and Mars linked: righteous action, technical/administrative skill.")
    second = [p for p in real7 if from_moon[p] == 2]
    twelfth = [p for p in real7 if from_moon[p] == 12]
    add("Sunapha Yoga", "Lunar", second and not twelfth, "Planet(s) 2nd from Moon: self-earned wealth.")
    add("Anapha Yoga", "Lunar", twelfth and not second, "Planet(s) 12th from Moon: good health, character.")
    add("Durudhara Yoga", "Lunar", second and twelfth, "Planets both sides of Moon: comforts, vehicles, generosity.", "strong")
    kemadruma = not second and not twelfth and not any(from_moon[p] in KENDRA for p in real7) and not any(h[p] in KENDRA for p in real7)
    add("Kemadruma Yoga", "Lunar (adverse)", kemadruma, "Moon isolated with no supporting planets: emotional/financial fluctuations.", "adverse")
    sun_s = sg["Sun"]
    s2 = [p for p in ("Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn") if p != "Moon" and house_from(sg[p], sun_s) == 2]
    s12 = [p for p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn") if house_from(sg[p], sun_s) == 12]
    add("Veshi Yoga", "Solar", s2 and not s12, "Planet 2nd from Sun: balanced outlook, steady effort.")
    add("Vashi Yoga", "Solar", s12 and not s2, "Planet 12th from Sun: skill, charity, fame.")
    add("Ubhayachari Yoga", "Solar", s2 and s12, "Planets both sides of Sun: kingly status, eloquence.", "strong")
    adhi = [p for p in ("Mercury", "Jupiter", "Venus") if from_moon[p] in (6, 7, 8)]
    add("Adhi Yoga", "Raja", len(adhi) >= 2, "Benefics in 6/7/8 from Moon: leadership, authority.", "strong" if len(adhi) == 3 else "medium")
    add("Amala Yoga", "Fame", any(p in BENEFICS - {"Moon"} for p in occ[10]) and not any(p in MALEFICS for p in occ[10]), "Only benefic in 10th: spotless reputation.")
    l9 = lord[9]
    add("Lakshmi Yoga", "Wealth", h[l9] in KENDRA | TRIKONA and dig[l9] in ("own", "exalted", "moolatrikona") and dig[lord[1]] not in ("debilitated",), "Strong 9th lord in kendra/trikona: fortune, wealth, grace.", "strong")
    add("Saraswati Yoga", "Learning", all(h[p] in KENDRA | TRIKONA | {2} for p in ("Jupiter", "Venus", "Mercury")) and dig["Jupiter"] not in ("debilitated", "enemy"), "Jupiter, Venus, Mercury in kendra/trikona/2nd: learning, arts.", "strong")
    # Raja yogas: kendra lord + trikona lord link
    rj = []
    for k in (1, 4, 7, 10):
        for t in (5, 9):
            a, b = lord[k], lord[t]
            if a != b and (mutual_aspect_or_conj(a, b) or exchange(a, b)):
                rj.append(f"{k}L {a} + {t}L {b}")
    add("Raja Yoga (Kendra-Trikona)", "Raja", rj, "Kendra and trikona lords linked: power, status. " + "; ".join(rj), "strong")
    yk = [p for p in SEVEN if {i for i in range(1, 13) if lord[i] == p} & KENDRA - {1} and {i for i in range(1, 13) if lord[i] == p} & {5, 9}]
    add("Yogakaraka", "Raja", yk, f"Single planet ruling kendra + trikona ({', '.join(yk)}): strong benefactor of the chart.", "strong")
    add("Dharma-Karmadhipati Yoga", "Raja", mutual_aspect_or_conj(lord[9], lord[10]) or exchange(lord[9], lord[10]) or lord[9] == lord[10], "9th and 10th lords linked: purposeful career, high achievement.", "strong")
    dh = []
    for a in (2, 11):
        for b in (1, 5, 9):
            if lord[a] != lord[b] and (conj(lord[a], lord[b]) or exchange(lord[a], lord[b])):
                dh.append(f"{a}L+{b}L")
    add("Dhana Yoga", "Wealth", dh, "Wealth lords linked with lagna/trikona lords: accumulation of wealth. " + ", ".join(dh))
    add("Harsha Viparita Raja Yoga", "Viparita", h[lord[6]] in DUSTHANA, "6th lord in dusthana: victory over enemies, health.")
    add("Sarala Viparita Raja Yoga", "Viparita", h[lord[8]] in DUSTHANA, "8th lord in dusthana: longevity, fearlessness.")
    add("Vimala Viparita Raja Yoga", "Viparita", h[lord[12]] in DUSTHANA, "12th lord in dusthana: frugality, independence.")
    nb = []
    for p in SEVEN:
        if dig[p] == "debilitated":
            deb_sign = sg[p]
            disp = SIGN_LORD[deb_sign]
            ex_lord = next((q for q, (es, _) in EXALT.items() if es == deb_sign and q in SEVEN), None)
            if h[disp] in KENDRA or from_moon[disp] in KENDRA or (ex_lord and (h[ex_lord] in KENDRA or from_moon[ex_lord] in KENDRA)) or dig.get(disp) == "exalted":
                nb.append(p)
    add("Neechabhanga Raja Yoga", "Raja", nb, f"Debilitation cancelled for {', '.join(nb)}: rise after early struggle.", "strong")
    ex = [f"{a}-{b}" for i, a in enumerate(SEVEN) for b in SEVEN[i + 1:] if exchange(a, b)]
    add("Parivartana Yoga", "Exchange", ex, "Sign exchange (" + ", ".join(ex) + "): mutual strengthening of houses involved.")
    add("Shakata Yoga", "Lunar (adverse)", house_from(sg["Moon"], sg["Jupiter"]) in (6, 8, 12) and h["Moon"] not in KENDRA, "Moon 6/8/12 from Jupiter: ups and downs in fortune.", "adverse")
    add("Kahala Yoga", "Courage", h[lord[4]] in KENDRA and h[lord[9]] in KENDRA and dig[lord[1]] in ("own", "exalted", "moolatrikona", "friendly"), "4th & 9th lords in kendras with strong lagna lord: boldness, command.")
    add("Chamara Yoga", "Fame", dig[lord[1]] == "exalted" and h[lord[1]] in KENDRA and from_moon["Jupiter"] in KENDRA, "Exalted lagna lord in kendra aspected by Jupiter: honour, scholarship.")
    up_ben = [p for p in ("Mercury", "Jupiter", "Venus") if from_moon[p] in UPACHAYA]
    add("Vasumati Yoga", "Wealth", len(up_ben) >= 2, "Benefics in upachayas from Moon: abundant wealth.")
    add("Parvata Yoga", "Fame", all(p not in MALEFICS for i in (6, 8) for p in occ[i]) and any(p in BENEFICS for i in KENDRA for p in occ[i]), "Benefics in kendras, 6/8 clean: prosperity, charity.")
    add("Shubha Kartari Yoga", "Lagna", any(p in BENEFICS for p in occ[2]) and any(p in BENEFICS for p in occ[12]), "Benefics hem the lagna: protection, good health.")
    add("Papa Kartari Yoga", "Lagna (adverse)", any(p in MALEFICS for p in occ[2]) and any(p in MALEFICS for p in occ[12]), "Malefics hem the lagna: obstacles, pressure.", "adverse")
    add("Sankha Yoga", "Prosperity", house_from(sg[lord[5]], sg[lord[6]]) in KENDRA and dig[lord[1]] not in ("debilitated",), "5th & 6th lords mutually in kendras: humane, long-lived, prosperous.")
    add("Mahabhagya-type Lagna strength", "Lagna", dig[lord[1]] in ("own", "exalted", "moolatrikona") and h[lord[1]] in KENDRA | TRIKONA, "Lagna lord dignified in kendra/trikona: vitality, self-made success.", "strong")
    add("Kalanidhi Yoga", "Learning", h["Jupiter"] in (2, 5) and (conj("Jupiter", "Mercury") or conj("Jupiter", "Venus")), "Jupiter in 2/5 with Mercury or Venus: refinement, learning.")
    add("Chandra-Adhi (Moon in kendra from Sun)", "Lunar", house_from(sg["Moon"], sg["Sun"]) in KENDRA, "Moon in kendra from Sun: moderate wealth and intelligence.")
    add("Guru-Chandala Yoga", "Adverse", conj("Jupiter", "Rahu") or conj("Jupiter", "Ketu"), "Jupiter with node: unorthodox beliefs, guidance issues.", "adverse")
    add("Angarak Yoga", "Adverse", conj("Mars", "Rahu"), "Mars with Rahu: temper, accidents, aggression.", "adverse")
    add("Vish Yoga", "Adverse", conj("Saturn", "Moon"), "Saturn with Moon: melancholy, heaviness.", "adverse")
    add("Grahan Yoga", "Adverse", conj("Sun", "Rahu") or conj("Moon", "Rahu") or conj("Sun", "Ketu") or conj("Moon", "Ketu"), "Luminary with node: eclipse-like obscuring of significations.", "adverse")
    return Y


# ---------- doshas ----------
REMEDY_DB = {
    "Sun": {"gem": "Ruby (Manik)", "metal": "Gold", "finger": "Ring", "mantra": "Om Hraam Hreem Hraum Sah Suryaya Namah", "count": 7000, "day": "Sunday", "charity": "Wheat, jaggery, copper to the needy on Sunday", "ritual": "Offer water (Arghya) to rising Sun; recite Aditya Hridayam", "deity": "Surya"},
    "Moon": {"gem": "Pearl (Moti)", "metal": "Silver", "finger": "Little", "mantra": "Om Shraam Shreem Shraum Sah Chandraya Namah", "count": 11000, "day": "Monday", "charity": "Rice, milk, white cloth on Monday", "ritual": "Shiva abhishek with milk on Mondays", "deity": "Shiva/Parvati"},
    "Mars": {"gem": "Red Coral (Moonga)", "metal": "Copper/Gold", "finger": "Ring", "mantra": "Om Kraam Kreem Kraum Sah Bhaumaya Namah", "count": 10000, "day": "Tuesday", "charity": "Red lentils (masoor), jaggery on Tuesday", "ritual": "Hanuman Chalisa on Tuesdays", "deity": "Hanuman/Kartikeya"},
    "Mercury": {"gem": "Emerald (Panna)", "metal": "Gold", "finger": "Little", "mantra": "Om Braam Breem Braum Sah Budhaya Namah", "count": 9000, "day": "Wednesday", "charity": "Green moong, green cloth on Wednesday", "ritual": "Vishnu Sahasranama; feed cows green grass", "deity": "Vishnu"},
    "Jupiter": {"gem": "Yellow Sapphire (Pukhraj)", "metal": "Gold", "finger": "Index", "mantra": "Om Graam Greem Graum Sah Gurave Namah", "count": 19000, "day": "Thursday", "charity": "Chana dal, turmeric, yellow cloth on Thursday", "ritual": "Respect teachers; Guru stotra on Thursdays", "deity": "Brihaspati/Vishnu"},
    "Venus": {"gem": "Diamond / White Sapphire", "metal": "Silver/Platinum", "finger": "Middle/Ring", "mantra": "Om Draam Dreem Draum Sah Shukraya Namah", "count": 16000, "day": "Friday", "charity": "Rice, sugar, white sweets on Friday", "ritual": "Lakshmi puja on Fridays", "deity": "Lakshmi"},
    "Saturn": {"gem": "Blue Sapphire (Neelam) — trial first", "metal": "Iron/Silver", "finger": "Middle", "mantra": "Om Praam Preem Praum Sah Shanaischaraya Namah", "count": 23000, "day": "Saturday", "charity": "Black sesame, mustard oil, iron to the poor on Saturday", "ritual": "Light sesame-oil lamp under Peepal on Saturdays; Shani stotra", "deity": "Shani/Hanuman"},
    "Rahu": {"gem": "Hessonite (Gomed)", "metal": "Silver/Ashtadhatu", "finger": "Middle", "mantra": "Om Bhraam Bhreem Bhraum Sah Rahave Namah", "count": 18000, "day": "Saturday", "charity": "Blue/black cloth, coconut, mustard on Saturday", "ritual": "Durga Saptashati; feed stray dogs", "deity": "Durga"},
    "Ketu": {"gem": "Cat's Eye (Lehsunia)", "metal": "Silver", "finger": "Little", "mantra": "Om Sraam Sreem Sraum Sah Ketave Namah", "count": 17000, "day": "Tuesday", "charity": "Blankets, sesame, multi-coloured cloth", "ritual": "Ganesha worship; feed dogs", "deity": "Ganesha"},
}


def detect_doshas(c: dict) -> list[dict]:
    out = []
    h = {p["name"]: p["house"] for p in c["planets"]}
    sg = {p["name"]: p["sign_index"] for p in c["planets"]}
    mars_s = sg["Mars"]
    mh = {"Lagna": h["Mars"], "Moon": house_from(mars_s, sg["Moon"]), "Venus": house_from(mars_s, sg["Venus"])}
    houses_m = (1, 2, 4, 7, 8, 12)
    hits = [k for k, v in mh.items() if v in houses_m]
    cancel = []
    if mars_s in (0, 7, 9):
        cancel.append("Mars in own/exalted sign")
    if P(c, "Mars")["sign_index"] in (4,) or SIGN_LORD[mars_s] == "Jupiter":
        cancel.append("Mars in Leo or Jupiter's sign")
    if sg["Jupiter"] == mars_s:
        cancel.append("Mars conjunct Jupiter")
    sev = len(hits) / 3
    if cancel:
        sev *= 0.4
    out.append({"name": "Manglik (Kuja) Dosha", "present": bool(hits), "severity": _sev(sev) if hits else "none", "score": round(sev * 100), "details": f"Mars in house {mh['Lagna']} from Lagna, {mh['Moon']} from Moon, {mh['Venus']} from Venus. Triggered from: {', '.join(hits) or 'none'}.",
                "cancellations": cancel, "remedies": ["Kumbh Vivah / match with Manglik partner", "Hanuman Chalisa on Tuesdays", REMEDY_DB["Mars"]["charity"], f"Mantra: {REMEDY_DB['Mars']['mantra']} ×108 daily"] if hits else []})
    rahu, ketu = P(c, "Rahu")["absolute_longitude"], P(c, "Ketu")["absolute_longitude"]
    side_a = all((P(c, p)["absolute_longitude"] - rahu) % 360 < 180 for p in SEVEN)
    side_b = all((P(c, p)["absolute_longitude"] - ketu) % 360 < 180 for p in SEVEN)
    ks_types = {1: "Anant", 2: "Kulik", 3: "Vasuki", 4: "Shankhpal", 5: "Padma", 6: "Mahapadma", 7: "Takshak", 8: "Karkotak", 9: "Shankhachood", 10: "Ghatak", 11: "Vishdhar", 12: "Sheshnag"}
    ks = side_a or side_b
    out.append({"name": "Kaal Sarp Dosha", "present": ks, "severity": "high" if ks else "none", "score": 80 if ks else 0, "type": ks_types[h["Rahu"]] if ks else None,
                "details": ("All seven planets hemmed between Rahu–Ketu axis (" + ("Rahu→Ketu" if side_a else "Ketu→Rahu") + f"); Rahu in house {h['Rahu']}.") if ks else "Planets on both sides of the nodal axis.",
                "cancellations": [], "remedies": ["Kaal Sarp shanti puja (Trimbakeshwar/Ujjain)", "Maha Mrityunjaya Japa", "Naag Panchami worship", REMEDY_DB["Rahu"]["ritual"]] if ks else []})
    pitra = []
    if sg["Sun"] == sg["Rahu"] or sg["Sun"] == sg["Ketu"]:
        pitra.append("Sun with node")
    if sg["Sun"] == sg["Saturn"]:
        pitra.append("Sun with Saturn")
    if any(p in ("Rahu", "Ketu", "Saturn") for p in [q["name"] for q in c["planets"] if q["house"] == 9]):
        pitra.append("Malefic in 9th house")
    if P(c, lord_of_house(c, 9))["house"] in DUSTHANA:
        pitra.append("9th lord in dusthana")
    out.append({"name": "Pitra Dosha", "present": bool(pitra), "severity": _sev(len(pitra) / 3), "score": min(100, len(pitra) * 33), "details": "; ".join(pitra) or "No ancestral affliction indicators.",
                "cancellations": ["Jupiter aspects 9th"] if "Jupiter" in aspected_by(c, 9) else [], "remedies": ["Pind daan / Shraddha during Pitru Paksha", "Tarpan on Amavasya", "Feed crows and Brahmins", REMEDY_DB["Sun"]["ritual"]] if pitra else []})
    sat = c.get("_transit_saturn")
    moon_s = sg["Moon"]
    swe.set_sid_mode(AYANAMSA.get(c["settings"]["ayanamsa"], swe.SIDM_LAHIRI))
    ts = sign_of(swe.calc_ut(jd_from_dt(datetime.now(UTC)), swe.SATURN, FLAGS)[0][0]) if sat is None else sat
    rel = house_from(ts, moon_s)
    phase = {12: "Sade Sati — rising phase", 1: "Sade Sati — peak phase", 2: "Sade Sati — setting phase", 4: "Kantaka Shani (Ardhashtama Dhaiya)", 8: "Ashtama Shani (Dhaiya)"}.get(rel)
    shani_issues = [phase] if phase else []
    if P(c, "Saturn")["dignity"] == "debilitated":
        shani_issues.append("Natal Saturn debilitated")
    out.append({"name": "Shani Dosha / Sade Sati", "present": bool(shani_issues), "severity": "high" if rel == 1 else ("medium" if shani_issues else "none"), "score": {1: 85, 12: 65, 2: 60, 8: 70, 4: 55}.get(rel, 30 if shani_issues else 0),
                "details": f"Transit Saturn in {SIGNS[ts]}, house {rel} from natal Moon ({SIGNS[moon_s]}). " + "; ".join(shani_issues), "cancellations": [],
                "remedies": [REMEDY_DB["Saturn"]["ritual"], REMEDY_DB["Saturn"]["charity"], f"Mantra: {REMEDY_DB['Saturn']['mantra']}", "Serve elderly/labourers; Hanuman worship"] if shani_issues else []})
    grahan = [x for x in ("Sun", "Moon") if sg[x] in (sg["Rahu"], sg["Ketu"])]
    out.append({"name": "Grahan Dosha", "present": bool(grahan), "severity": _sev(len(grahan) / 2), "score": len(grahan) * 45, "details": f"{', '.join(grahan)} conjunct a lunar node." if grahan else "Luminaries free of nodes.",
                "cancellations": [], "remedies": ["Grahan shanti puja", REMEDY_DB["Rahu"]["mantra"]] if grahan else []})
    return out


def _sev(x: float) -> str:
    return "none" if x <= 0 else "low" if x < 0.34 else "medium" if x < 0.67 else "high"


# ---------- Ashtakavarga ----------
AV_TABLE = {
    "Sun": {"Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [3, 5, 6, 9, 10, 11, 12], "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12], "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Ascendant": [3, 4, 6, 10, 11, 12]},
    "Moon": {"Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 10, 11], "Mars": [2, 3, 5, 6, 9, 10, 11], "Mercury": [1, 3, 4, 5, 7, 8, 10, 11], "Jupiter": [1, 4, 7, 8, 10, 11, 12], "Venus": [3, 4, 5, 7, 9, 10, 11], "Saturn": [3, 5, 6, 11], "Ascendant": [3, 6, 10, 11]},
    "Mars": {"Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11], "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [3, 5, 6, 11], "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12], "Saturn": [1, 4, 7, 8, 9, 10, 11], "Ascendant": [1, 3, 6, 10, 11]},
    "Mercury": {"Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [1, 3, 5, 6, 9, 10, 11, 12], "Jupiter": [6, 8, 11, 12], "Venus": [1, 2, 3, 4, 5, 8, 9, 11], "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Ascendant": [1, 2, 4, 6, 8, 10, 11]},
    "Jupiter": {"Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11], "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [1, 2, 4, 5, 6, 9, 10, 11], "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11], "Venus": [2, 5, 6, 9, 10, 11], "Saturn": [3, 5, 6, 12], "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]},
    "Venus": {"Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12], "Mars": [3, 5, 6, 9, 11, 12], "Mercury": [3, 5, 6, 9, 11], "Jupiter": [5, 8, 9, 10, 11], "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11], "Saturn": [3, 4, 5, 8, 9, 10, 11], "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]},
    "Saturn": {"Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11], "Mars": [3, 5, 6, 10, 11, 12], "Mercury": [6, 8, 9, 10, 11, 12], "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12], "Saturn": [3, 5, 6, 11], "Ascendant": [1, 3, 4, 6, 10, 11]},
}


def ashtakavarga(c: dict) -> dict:
    ref = {p["name"]: p["sign_index"] for p in c["planets"]}
    ref["Ascendant"] = c["ascendant"]["sign_index"]
    bav = {}
    for planet, table in AV_TABLE.items():
        pts = [0] * 12
        for contributor, hs in table.items():
            for hh in hs:
                pts[(ref[contributor] + hh - 1) % 12] += 1
        bav[planet] = pts
    sav = [sum(bav[p][i] for p in bav) for i in range(12)]
    asc = ref["Ascendant"]
    return {"signs": list(SIGNS), "bhinnashtakavarga": bav, "bav_totals": {k: sum(v) for k, v in bav.items()}, "sarvashtakavarga": sav, "total": sum(sav),
            "by_house": [{"house": h, "sign": SIGNS[(asc + h - 1) % 12], "points": sav[(asc + h - 1) % 12], "strong": sav[(asc + h - 1) % 12] >= 28} for h in range(1, 13)]}


# ---------- Shadbala (approximate) ----------
NAISARGIKA = {"Sun": 60, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29, "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}
REQUIRED_RUPAS = {"Sun": 5, "Moon": 6, "Mars": 5, "Mercury": 7, "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5}
DIG_STRONG = {"Sun": 10, "Mars": 10, "Jupiter": 1, "Mercury": 1, "Moon": 4, "Venus": 4, "Saturn": 7}
MEAN_SPEED = {"Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.083, "Venus": 1.2, "Saturn": 0.033}


def shadbala(c: dict, pos: dict, jd: float, lat: float, lon: float) -> dict:
    asc = c["ascendant"]["absolute_longitude"]
    res = {}
    sun, moon = pos["Sun"]["lon"], pos["Moon"]["lon"]
    elong = (moon - sun) % 360
    paksha_ben = (elong if elong <= 180 else 360 - elong) / 3
    # day/night via Sun altitude
    swe.set_sid_mode(AYANAMSA.get(c["settings"]["ayanamsa"], swe.SIDM_LAHIRI))
    trop_sun = swe.calc_ut(jd, swe.SUN, BASE_FLAGS)[0]
    az = swe.azalt(jd, swe.ECL2HOR, (lon, lat, 0), 0, 10, (trop_sun[0], trop_sun[1], trop_sun[2]))
    is_day = az[1] > 0
    for name in SEVEN:
        p = P(c, name)
        L = pos[name]["lon"]
        deb = (EXALT[name][0] * 30 + EXALT[name][1] + 180) % 360
        d = abs((L - deb + 180) % 360 - 180)
        uchcha = d / 3
        sapta = 0.0
        for n in (1, 2, 3, 7, 9, 12, 30):
            vs = varga_sign(L, n)
            if n == 1 and p["dignity"] == "moolatrikona":
                sapta += 45
            elif vs in OWN[name]:
                sapta += 30
            else:
                r = relation(name, SIGN_LORD[vs])
                sapta += {"friend": 15, "neutral": 7.5, "enemy": 3.75}.get(r, 30)
        odd_r, odd_n = sign_of(L) % 2 == 0, varga_sign(L, 9) % 2 == 0
        fem = name in ("Moon", "Venus")
        oja = (15 if odd_r != fem else 0) + (15 if odd_n != fem else 0)
        kendradi = 60 if p["house"] in KENDRA else 30 if p["house"] in (2, 5, 8, 11) else 15
        dec = int((L % 30) // 10)
        drek = 15 if (name in ("Sun", "Mars", "Jupiter") and dec == 0) or (name in ("Mercury", "Saturn") and dec == 1) or (fem and dec == 2) else 0
        sthana = uchcha + sapta + oja + kendradi + drek
        strong_pt = norm(asc + (DIG_STRONG[name] - 1) * 30)
        dig = (180 - abs((L - strong_pt + 180) % 360 - 180)) / 3
        if name == "Mercury":
            nath = 60
        elif name in ("Sun", "Jupiter", "Venus"):
            nath = 60 if is_day else 20
        else:
            nath = 20 if is_day else 60
        paksha = paksha_ben if name in BENEFICS else 60 - paksha_ben
        if name == "Moon":
            paksha *= 2
        kala = nath + paksha
        if name in MEAN_SPEED:
            sp = pos[name]["speed"]
            chesta = 60 if sp < 0 else max(0, min(60, 30 * (2 - abs(sp) / MEAN_SPEED[name])))
        elif name == "Moon":
            chesta = paksha_ben
        else:
            chesta = 30
        drik = 0.0
        for q in c["planets"]:
            if q["name"] == name or q["name"] in ("Rahu", "Ketu"):
                continue
            if any((q["house"] + a - 2) % 12 + 1 == p["house"] for a in aspects_houses(q["name"])):
                drik += 15 if q["name"] in BENEFICS else -15
        nais = NAISARGIKA[name]
        total = sthana + dig + kala + chesta + nais + drik
        rupas = total / 60
        res[name] = {"sthana": round(sthana, 2), "dig": round(dig, 2), "kala": round(kala, 2), "chesta": round(chesta, 2), "naisargika": nais, "drik": round(drik, 2),
                     "total_virupas": round(total, 2), "rupas": round(rupas, 2), "required": REQUIRED_RUPAS[name], "ratio": round(rupas / REQUIRED_RUPAS[name], 2), "strong": rupas >= REQUIRED_RUPAS[name]}
    ranked = sorted(res, key=lambda k: res[k]["ratio"], reverse=True)
    return {"planets": res, "ranking": ranked, "method": "Approximate Parashari Shadbala (simplified Kala & Saptavargaja using natural relationships)"}


# ---------- interpretations ----------
HOUSE_SIG = {
    1: ("Self, body, personality, vitality", "Lagna"), 2: ("Wealth, family, speech, food", "Dhana"), 3: ("Courage, siblings, communication, short travel", "Sahaja"),
    4: ("Mother, home, property, vehicles, inner peace", "Sukha"), 5: ("Intellect, children, creativity, past merit, romance", "Putra"), 6: ("Enemies, disease, debts, service, competition", "Ripu"),
    7: ("Spouse, partnerships, business, public dealings", "Kalatra"), 8: ("Longevity, transformation, occult, inheritance, sudden events", "Randhra"), 9: ("Fortune, father, dharma, guru, long travel", "Dharma"),
    10: ("Career, status, authority, karma", "Karma"), 11: ("Gains, income, friends, aspirations", "Labha"), 12: ("Loss, expenses, foreign lands, moksha, sleep", "Vyaya"),
}
PLANET_NATURE = {"Sun": "authority, father, soul, government", "Moon": "mind, mother, emotions, public", "Mars": "energy, courage, land, siblings", "Mercury": "intellect, trade, speech, skills",
                 "Jupiter": "wisdom, children, wealth, teachers", "Venus": "love, luxury, arts, spouse", "Saturn": "discipline, longevity, labour, delays", "Rahu": "ambition, foreign, technology, obsession", "Ketu": "detachment, spirituality, research, loss"}
DIG_WORD = {"exalted": "very strong", "moolatrikona": "strong", "own": "strong", "friendly": "comfortable", "neutral": "average", "enemy": "uncomfortable", "debilitated": "weak"}


def house_analysis(c: dict) -> list[dict]:
    sav = {h["house"]: h["points"] for h in c["ashtakavarga"]["by_house"]}
    out = []
    for hh in c["houses"]:
        n = hh["house"]
        L = P(c, hh["lord"])
        occ = hh["occupants"]
        asp = aspected_by(c, n)
        score = 50 + (sav[n] - 28) * 3
        score += {"exalted": 20, "moolatrikona": 15, "own": 15, "friendly": 6, "neutral": 0, "enemy": -8, "debilitated": -18}[L["dignity"]]
        score += 8 if L["house"] in KENDRA | TRIKONA else -10 if L["house"] in DUSTHANA and n not in DUSTHANA else 0
        score += sum(6 for o in occ if o in BENEFICS) - sum(5 for o in occ if o in MALEFICS and n not in UPACHAYA)
        score += sum(4 for a in asp if a in ("Jupiter", "Venus")) - sum(3 for a in asp if a in ("Saturn", "Mars", "Rahu"))
        score = max(5, min(98, score))
        text = (f"{HOUSE_SIG[n][1]} bhava ({hh['sign']}) governs {HOUSE_SIG[n][0].lower()}. Its lord {hh['lord']} sits in house {L['house']} ({L['sign']}), {DIG_WORD[L['dignity']]}"
                + (", combust" if L["combust"] else "") + (", retrograde" if L["retrograde"] and hh["lord"] not in ("Rahu", "Ketu") else "") + ". "
                + (f"Occupied by {', '.join(occ)}, bringing {'; '.join(PLANET_NATURE[o] for o in occ)}. " if occ else "No occupants; results depend mainly on the lord. ")
                + (f"Aspected by {', '.join(asp)}. " if asp else "") + f"Sarvashtakavarga {sav[n]} points ({'above' if sav[n] >= 28 else 'below'} average 28).")
        out.append({"house": n, "name": HOUSE_SIG[n][1], "significations": HOUSE_SIG[n][0], "sign": hh["sign"], "lord": hh["lord"], "lord_house": L["house"], "lord_dignity": L["dignity"],
                    "occupants": occ, "aspects": asp, "sav": sav[n], "score": round(score), "interpretation": text})
    return out


def life_areas(c: dict) -> dict:
    ha = {h["house"]: h for h in c["house_analysis"]}
    sb = c["shadbala"]["planets"]

    def area(name, houses, karakas, focus):
        s = sum(ha[h]["score"] for h in houses) / len(houses)
        ks = [k for k in karakas if k in sb]
        if ks:
            s = s * 0.75 + 0.25 * min(100, 70 * sum(sb[k]["ratio"] for k in ks) / len(ks))
        s = max(5, min(98, round(s)))
        strong = [h for h in houses if ha[h]["score"] >= 60]
        weak = [h for h in houses if ha[h]["score"] < 45]
        cur = c["dasha"]["current"]
        dl = cur[0]["lord"] if cur else None
        dasha_note = ""
        if dl:
            ruled = [h for h in range(1, 13) if lord_of_house(c, h) == dl]
            if set(ruled) & set(houses) or P(c, dl)["house"] in houses:
                dasha_note = f" Current {dl} Mahadasha directly activates this area."
        summary = (f"{focus} Key houses {', '.join(map(str, houses))}; karaka(s) {', '.join(karakas)}. "
                   + (f"Supportive: house {', '.join(map(str, strong))}. " if strong else "") + (f"Needs care: house {', '.join(map(str, weak))}. " if weak else "") + dasha_note)
        return {"score": s, "houses": houses, "karakas": karakas, "summary": summary.strip(), "outlook": "excellent" if s >= 75 else "good" if s >= 60 else "mixed" if s >= 45 else "challenging"}

    return {
        "career": area("career", [10, 6, 2, 11], ["Sun", "Saturn", "Mercury"], "Career is read from the 10th (status), 6th (service), 2nd/11th (earnings)."),
        "finance": area("finance", [2, 11, 5, 9], ["Jupiter", "Venus"], "Wealth combines savings (2nd), gains (11th) and fortune (5th/9th)."),
        "health": area("health", [1, 6, 8], ["Sun", "Moon"], "Health depends on lagna vitality, resistance to disease (6th) and longevity (8th)."),
        "relationships": area("relationships", [7, 5, 2], ["Venus", "Jupiter"], "Partnership is judged from the 7th, romance from the 5th, family life from the 2nd."),
        "education": area("education", [4, 5, 9], ["Mercury", "Jupiter"], "Foundational learning (4th), intellect (5th) and higher studies (9th)."),
    }


def remedies(c: dict) -> list[dict]:
    sb = c["shadbala"]["planets"]
    out = []
    for p in c["planets"]:
        n = p["name"]
        reasons = []
        if p["dignity"] == "debilitated":
            reasons.append("debilitated")
        if p["combust"]:
            reasons.append("combust")
        if n in sb and not sb[n]["strong"]:
            reasons.append(f"Shadbala {sb[n]['rupas']}/{sb[n]['required']} rupas")
        if p["house"] in DUSTHANA and n in BENEFICS:
            reasons.append(f"benefic in house {p['house']}")
        if n in ("Rahu", "Ketu") and p["house"] in (1, 5, 7, 9):
            reasons.append(f"node in house {p['house']}")
        if not reasons:
            continue
        r = REMEDY_DB[n]
        func_benefic = any(lord_of_house(c, h) == n for h in (1, 5, 9)) and not any(lord_of_house(c, h) == n for h in (6, 8, 12))
        out.append({"planet": n, "reasons": reasons, "gemstone": r["gem"] if func_benefic else None, "gem_note": "Gemstone advisable — planet is a functional benefic." if func_benefic else "Gemstone NOT advised (would strengthen a functional malefic); prefer mantra/charity.",
                    "metal": r["metal"], "finger": r["finger"], "mantra": r["mantra"], "mantra_count": r["count"], "day": r["day"], "charity": r["charity"], "ritual": r["ritual"], "deity": r["deity"]})
    return out


DASHA_THEMES = {
    "Sun": "Authority, recognition and dealings with government or father come to the fore. Good for leadership; watch ego and heart/eye health.",
    "Moon": "Emotional life, home, mother and public interaction dominate. Travel and changes of residence are common; mind fluctuates with Moon's strength.",
    "Mars": "Drive, competition, property and technical work. Bold initiatives succeed; avoid conflicts, accidents and haste.",
    "Rahu": "Ambition, unconventional paths, foreign links and technology. Sudden rises possible; guard against illusion and shortcuts.",
    "Jupiter": "Expansion through learning, children, mentors and wealth. Spiritual inclination and good counsel; avoid over-indulgence.",
    "Saturn": "Long-term building through discipline and hard work. Delays test patience but reward perseverance; health of joints and nerves.",
    "Mercury": "Commerce, communication, study and networking. Intellectual growth and multiple income streams; watch nervous stress.",
    "Ketu": "Detachment, research, spirituality and endings. Material focus loosens; sudden breaks lead to inner insight.",
    "Venus": "Relationships, comforts, arts, vehicles and luxury. Marriage and creative success likely; avoid excess.",
}


def dasha_interpretation(c: dict, lord: str, sub: str | None = None) -> str:
    p = P(c, lord)
    ruled = [h for h in range(1, 13) if lord_of_house(c, h) == lord]
    txt = f"{DASHA_THEMES[lord]} In this chart {lord} is in house {p['house']} ({p['sign']}, {DIG_WORD[p['dignity']]})"
    txt += f" and rules house(s) {', '.join(map(str, ruled))}, so {', '.join(HOUSE_SIG[h][0].split(',')[0].lower() for h in ruled + [p['house']])} are emphasised." if ruled else f", activating {HOUSE_SIG[p['house']][0].lower()}."
    if sub and sub != lord:
        rel = house_from(P(c, sub)["sign_index"], p["sign_index"])
        txt += f" Sub-period of {sub} ({'harmonious' if rel in (1, 3, 5, 9, 10, 11) else 'testing'} placement {rel} from {lord}) colours it with {PLANET_NATURE[sub]}."
    return txt


# ---------- transits ----------
GOCHAR_GOOD = {"Sun": {3, 6, 10, 11}, "Moon": {1, 3, 6, 7, 10, 11}, "Mars": {3, 6, 11}, "Mercury": {2, 4, 6, 8, 10, 11}, "Jupiter": {2, 5, 7, 9, 11}, "Venus": {1, 2, 3, 4, 5, 8, 9, 11, 12}, "Saturn": {3, 6, 11}, "Rahu": {3, 6, 11}, "Ketu": {3, 6, 11}}


def gochar(c: dict | None, when: datetime | None = None, moon_sign: int | None = None, ayanamsa: str = "lahiri") -> dict:
    when = when or datetime.now(UTC)
    ay = c["settings"]["ayanamsa"] if c else ayanamsa
    pos = planet_positions(jd_from_dt(when), ay)
    ms = moon_sign if moon_sign is not None else P(c, "Moon")["sign_index"]
    asc = c["ascendant"]["sign_index"] if c else ms
    out = []
    for n in NINE:
        s = sign_of(pos[n]["lon"])
        hm = house_from(s, ms)
        good = hm in GOCHAR_GOOD[n]
        item = {"name": n, "sign": SIGNS[s], "degree": dms(pos[n]["lon"] % 30), "nakshatra": nakshatra(pos[n]["lon"])["name"], "retrograde": pos[n]["speed"] < 0 and n not in ("Rahu", "Ketu"),
                "house_from_moon": hm, "house_from_lagna": house_from(s, asc), "favourable": good,
                "effect": f"{n} transiting {hm}{_ord(hm)} from Moon: {'supportive' if good else 'challenging'} for {HOUSE_SIG[hm][0].split(',')[0].lower()} and {PLANET_NATURE[n].split(',')[0]} matters."}
        if c:
            natal_hits = [p["name"] for p in c["planets"] if p["sign_index"] == s and p["name"] != n]
            if natal_hits:
                item["conjunct_natal"] = natal_hits
        out.append(item)
    return {"date": when.isoformat(), "reference_moon_sign": SIGNS[ms], "planets": out, "score": round(100 * sum(1 for i in out if i["favourable"]) / 9)}


def _ord(n: int) -> str:
    return "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def rashi_horoscope(sign_index: int, period: str = "daily", when: datetime | None = None) -> dict:
    when = when or datetime.now(UTC)
    span = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}[period]
    samples = [when + timedelta(days=span * f) for f in ((0,) if span == 1 else (0, 0.5, 1))]
    tr = [gochar(None, t, sign_index) for t in samples]
    score = round(sum(t["score"] for t in tr) / len(tr))
    weights = {"daily": ["Moon", "Sun", "Mercury", "Venus", "Mars"], "weekly": ["Moon", "Sun", "Mercury", "Venus", "Mars"], "monthly": ["Sun", "Mercury", "Venus", "Mars", "Jupiter"], "yearly": ["Jupiter", "Saturn", "Rahu", "Ketu", "Mars"]}[period]
    first = {p["name"]: p for p in tr[0]["planets"]}
    lines = [first[w]["effect"] for w in weights]
    areas = {}
    for area, hs in {"career": (10, 6, 11), "love": (5, 7), "money": (2, 11), "health": (1, 6, 8)}.items():
        g = sum(1 for p in tr[0]["planets"] if p["house_from_moon"] in hs and p["favourable"]) - sum(1 for p in tr[0]["planets"] if p["house_from_moon"] in hs and not p["favourable"])
        areas[area] = max(1, min(5, 3 + g))
    lucky = REMEDY_DB[SIGN_LORD[sign_index]]
    return {"sign": SIGNS[sign_index], "period": period, "from": when.date().isoformat(), "to": (when + timedelta(days=span)).date().isoformat(), "score": score,
            "overview": ("A favourable phase" if score >= 60 else "A mixed phase" if score >= 40 else "A demanding phase") + f" for {SIGNS[sign_index]} Moon sign based on Gochar from the Moon.",
            "highlights": lines, "areas": areas, "lucky": {"day": lucky["day"], "deity": lucky["deity"], "gem": lucky["gem"]}}


# ---------- Panchang ----------
TITHIS = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi"]
YOGAS27 = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
KARANA_MOV = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
LUNAR_MONTHS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
RAHU_PART = [8, 2, 7, 5, 6, 4, 3]
GULIKA_PART = [7, 6, 5, 4, 3, 2, 1]
YAMA_PART = [5, 4, 3, 2, 1, 7, 6]


def tithi_name(i: int) -> tuple[str, str]:
    paksha = "Shukla" if i < 15 else "Krishna"
    k = i % 15
    if k == 14:
        return ("Purnima" if i < 15 else "Amavasya"), paksha
    return TITHIS[k], paksha


def karana_name(i: int) -> str:
    if i == 0:
        return "Kimstughna"
    if i >= 57:
        return ["Shakuni", "Chatushpada", "Naga"][i - 57]
    return KARANA_MOV[(i - 1) % 7]


def sun_rise_set(d: date, lat: float, lon: float, tz: str) -> tuple[float, float]:
    start = jd_from_dt(datetime.combine(d, datetime.min.time(), tzinfo=ZoneInfo(tz)))
    geo = (lon, lat, 0)
    rflag = swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION if False else 0
    r = swe.rise_trans(start, swe.SUN, swe.CALC_RISE | rflag, geo, 0, 0, BASE_FLAGS)
    s = swe.rise_trans(start, swe.SUN, swe.CALC_SET | rflag, geo, 0, 0, BASE_FLAGS)
    return r[1][0], s[1][0]


def _angles(jd: float) -> tuple[float, float]:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    s = swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]
    m = swe.calc_ut(jd, swe.MOON, FLAGS)[0][0]
    return norm(s), norm(m)


def _end_time(jd: float, fn, step_deg: float, cur: int, limit_days: float = 2.0) -> float:
    lo, hi = jd, jd + limit_days
    t = jd
    while t < hi and fn(t) == cur:
        t += 0.05
    lo, hi = t - 0.05, t
    for _ in range(30):
        mid = (lo + hi) / 2
        if fn(mid) == cur:
            lo = mid
        else:
            hi = mid
    return hi


def panchang(d: date, lat: float = 22.5726, lon: float = 88.3639, tz: str = "Asia/Kolkata") -> dict:
    rise, sett = sun_rise_set(d, lat, lon, tz)
    nxt_rise, _ = sun_rise_set(d + timedelta(days=1), lat, lon, tz)
    s, m = _angles(rise)
    ti = int(((m - s) % 360) // 12)
    nk = nakshatra(m)
    yi = int(((s + m) % 360) // NAK_SPAN)
    ki = int(((m - s) % 360) // 6)
    f_t = lambda j: int(((_angles(j)[1] - _angles(j)[0]) % 360) // 12)
    f_n = lambda j: int(_angles(j)[1] // NAK_SPAN)
    f_y = lambda j: int((sum(_angles(j)) % 360) // NAK_SPAN)
    f_k = lambda j: int(((_angles(j)[1] - _angles(j)[0]) % 360) // 6)
    tn, paksha = tithi_name(ti)
    weekday = (d.weekday() + 1) % 7
    day_len = sett - rise
    part = day_len / 8

    def seg(idx):
        a = rise + (idx - 1) * part
        return {"start": dt_from_jd(a, tz).strftime("%H:%M"), "end": dt_from_jd(a + part, tz).strftime("%H:%M")}

    mid = rise + day_len / 2
    muh = day_len / 15
    elong_new = ((m - s) % 360)
    nm_jd = rise - elong_new / 12.19
    sun_at_nm = sign_of(_angles(nm_jd)[0])
    month = LUNAR_MONTHS[(sun_at_nm - 11) % 12]
    fmt = lambda j: dt_from_jd(j, tz).strftime("%d %b %H:%M")
    brahma = rise - 2 * (24 / 30) / 24
    return {
        "date": d.isoformat(), "location": {"lat": lat, "lon": lon, "timezone": tz}, "vara": VARAS[weekday],
        "sunrise": dt_from_jd(rise, tz).strftime("%H:%M"), "sunset": dt_from_jd(sett, tz).strftime("%H:%M"),
        "tithi": {"name": tn, "paksha": paksha, "number": ti % 15 + 1, "ends": fmt(_end_time(rise, f_t, 12, ti))},
        "nakshatra": {"name": nk["name"], "pada": nk["pada"], "lord": nk["lord"], "ends": fmt(_end_time(rise, f_n, NAK_SPAN, nk["index"]))},
        "yoga": {"name": YOGAS27[yi], "ends": fmt(_end_time(rise, f_y, NAK_SPAN, yi))},
        "karana": {"name": karana_name(ki), "ends": fmt(_end_time(rise, f_k, 6, ki))},
        "moon_sign": SIGNS[sign_of(m)], "sun_sign": SIGNS[sign_of(s)], "lunar_month_amanta": month,
        "rahu_kaal": seg(RAHU_PART[weekday]), "gulika_kaal": seg(GULIKA_PART[weekday]), "yamaghanta": seg(YAMA_PART[weekday]),
        "abhijit_muhurta": None if weekday == 3 else {"start": dt_from_jd(mid - muh / 2, tz).strftime("%H:%M"), "end": dt_from_jd(mid + muh / 2, tz).strftime("%H:%M")},
        "brahma_muhurta": {"start": dt_from_jd(brahma, tz).strftime("%H:%M"), "end": dt_from_jd(brahma + 48 / 1440, tz).strftime("%H:%M")},
        "_raw": {"tithi_index": ti, "nak_index": nk["index"], "yoga_index": yi, "weekday": weekday, "month_index": (sun_at_nm - 11) % 12, "sun_sign": sign_of(s)},
    }


# ---------- Muhurta ----------
MUHURTA_RULES = {
    "marriage": {"nak": {3, 4, 9, 11, 12, 14, 16, 18, 20, 21, 25, 26}, "vara": {1, 3, 4, 5}, "avoid_tithi": {3, 7, 8, 13, 14, 29}},
    "travel": {"nak": {0, 4, 6, 7, 12, 16, 21, 22, 26}, "vara": {1, 3, 4, 5}, "avoid_tithi": {3, 5, 7, 8, 11, 13, 14, 29}},
    "business": {"nak": {0, 3, 7, 11, 12, 13, 16, 20, 21, 25, 26}, "vara": {3, 4, 5}, "avoid_tithi": {3, 7, 8, 13, 14, 29}},
    "housewarming": {"nak": {3, 4, 11, 13, 16, 20, 21, 22, 23, 25, 26}, "vara": {1, 3, 4, 5}, "avoid_tithi": {3, 7, 8, 13, 14, 29}},
    "vehicle": {"nak": {0, 4, 6, 7, 12, 13, 14, 16, 21, 22, 23, 26}, "vara": {1, 3, 4, 5}, "avoid_tithi": {3, 7, 8, 13, 14, 29}},
    "education": {"nak": {0, 4, 6, 7, 12, 13, 14, 21, 22, 23, 26}, "vara": {0, 3, 4, 5}, "avoid_tithi": {3, 7, 8, 13, 14, 29}},
}
BAD_YOGAS = {0, 5, 8, 9, 12, 14, 16, 18, 26}


def muhurta(event: str, start: date, days: int, lat: float, lon: float, tz: str) -> list[dict]:
    rules = MUHURTA_RULES[event]
    res = []
    for k in range(min(days, 120)):
        d = start + timedelta(days=k)
        pc = panchang(d, lat, lon, tz)
        r = pc["_raw"]
        score, why = 0, []
        if r["nak_index"] in rules["nak"]:
            score += 40
            why.append(f"auspicious nakshatra {pc['nakshatra']['name']}")
        if r["weekday"] in rules["vara"]:
            score += 20
            why.append(f"favourable {pc['vara']}")
        if r["tithi_index"] not in rules["avoid_tithi"]:
            score += 20
            why.append(f"suitable tithi {pc['tithi']['name']}")
        if r["yoga_index"] not in BAD_YOGAS:
            score += 10
            why.append(f"benign yoga {pc['yoga']['name']}")
        if pc["karana"]["name"] != "Vishti":
            score += 10
        else:
            why.append("Vishti (Bhadra) karana — avoid")
        if score >= 70:
            res.append({"date": d.isoformat(), "vara": pc["vara"], "score": score, "reasons": why, "tithi": pc["tithi"]["name"], "nakshatra": pc["nakshatra"]["name"],
                        "best_window": pc["abhijit_muhurta"], "avoid": {"rahu_kaal": pc["rahu_kaal"], "yamaghanta": pc["yamaghanta"]}})
    return sorted(res, key=lambda x: (-x["score"], x["date"]))


# ---------- Festivals ----------
FESTIVALS = [  # (month_index amanta, tithi_index 0..29, name)
    (0, 0, "Chaitra Navratri begins / Ugadi / Gudi Padwa"), (0, 8, "Ram Navami"), (0, 14, "Hanuman Jayanti"), (1, 2, "Akshaya Tritiya"), (1, 14, "Buddha Purnima"),
    (3, 14, "Guru Purnima"), (4, 4, "Nag Panchami"), (4, 14, "Raksha Bandhan"), (4, 22, "Krishna Janmashtami"), (5, 3, "Ganesh Chaturthi"),
    (6, 0, "Sharad Navratri begins"), (6, 7, "Durga Ashtami"), (6, 9, "Dussehra (Vijayadashami)"), (6, 14, "Sharad Purnima"), (6, 18, "Karva Chauth"), (6, 27, "Dhanteras"), (6, 29, "Diwali (Lakshmi Puja)"),
    (7, 0, "Govardhan Puja"), (7, 1, "Bhai Dooj"), (7, 5, "Chhath Puja"), (7, 14, "Kartik Purnima / Dev Deepawali"), (10, 4, "Vasant Panchami"), (10, 28, "Maha Shivaratri"), (11, 14, "Holika Dahan"),
]
VRATS = {10: "Ekadashi", 25: "Ekadashi", 12: "Pradosh Vrat", 27: "Pradosh Vrat", 14: "Purnima", 29: "Amavasya", 18: "Sankashti Chaturthi", 3: "Vinayaka Chaturthi"}


def festival_calendar(year: int, month: int | None, lat: float, lon: float, tz: str) -> list[dict]:
    start = date(year, month or 1, 1)
    end = date(year + (1 if (month or 12) == 12 else 0), ((month or 12) % 12) + 1, 1) if month else date(year + 1, 1, 1)
    out, d = [], start
    prev_sun = None
    while d < end:
        pc = panchang(d, lat, lon, tz)
        r = pc["_raw"]
        for mi, ti, name in FESTIVALS:
            if r["month_index"] == mi and r["tithi_index"] == ti:
                out.append({"date": d.isoformat(), "name": name, "type": "festival", "tithi": pc["tithi"]["name"], "paksha": pc["tithi"]["paksha"]})
        if r["tithi_index"] in VRATS:
            out.append({"date": d.isoformat(), "name": VRATS[r["tithi_index"]], "type": "vrat", "tithi": pc["tithi"]["name"], "paksha": pc["tithi"]["paksha"]})
        if prev_sun is not None and r["sun_sign"] != prev_sun:
            out.append({"date": d.isoformat(), "name": "Makar Sankranti" if r["sun_sign"] == 9 else f"{SIGNS[r['sun_sign']]} Sankranti", "type": "sankranti" if r["sun_sign"] != 9 else "festival", "tithi": pc["tithi"]["name"], "paksha": pc["tithi"]["paksha"]})
        prev_sun = r["sun_sign"]
        d += timedelta(days=1)
    # dedupe consecutive same-name (tithi spanning two sunrises is rare; keep first)
    seen, uniq = set(), []
    for e in out:
        key = (e["name"], e["date"][:7]) if e["type"] == "festival" else (e["name"], e["date"])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    return uniq


# ---------- Ashtakoota ----------
VASHYA_TABLE = [[2, 1, 1, 0.5, 1], [1, 2, 0.5, 0, 1], [1, 0.5, 2, 1, 1], [0.5, 0, 1, 2, 0], [1, 1, 1, 0, 2]]
YONI = ["Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant"]
YONI_ENEMY = {frozenset(x) for x in (("Horse", "Buffalo"), ("Elephant", "Lion"), ("Sheep", "Monkey"), ("Serpent", "Mongoose"), ("Dog", "Deer"), ("Cat", "Rat"), ("Cow", "Tiger"))}
YONI_FRIEND = {frozenset(x) for x in (("Horse", "Deer"), ("Elephant", "Sheep"), ("Cow", "Buffalo"), ("Monkey", "Mongoose"), ("Lion", "Tiger"), ("Dog", "Cat"))}
GANA = "DMRMDMDDRRMMDRDRDRRMMDRRMMD"  # by nakshatra
NADI = ["Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi"]


def _vashya(sign: int, deg: float) -> int:
    if sign in (0, 1) or (sign == 8 and deg >= 15) or (sign == 9 and deg < 15):
        return 0
    if sign in (2, 5, 6, 10) or (sign == 8 and deg < 15):
        return 1
    if sign in (3, 11) or (sign == 9 and deg >= 15):
        return 2
    if sign == 4:
        return 3
    return 4


def guna_milan(boy_moon: float, girl_moon: float, boy_chart: dict | None = None, girl_chart: dict | None = None) -> dict:
    bs, gs = sign_of(boy_moon), sign_of(girl_moon)
    bn, gn = nakshatra(boy_moon)["index"], nakshatra(girl_moon)["index"]
    K = []
    varna_rank = lambda s: {3: 4, 7: 4, 11: 4, 0: 3, 4: 3, 8: 3, 1: 2, 5: 2, 9: 2}.get(s, 1)
    VN = {4: "Brahmin", 3: "Kshatriya", 2: "Vaishya", 1: "Shudra"}
    v = 1 if varna_rank(bs) >= varna_rank(gs) else 0
    K.append({"koota": "Varna", "max": 1, "score": v, "boy": VN[varna_rank(bs)], "girl": VN[varna_rank(gs)], "meaning": "Spiritual/ego compatibility"})
    VSN = ["Chatushpada", "Manava", "Jalachara", "Vanachara", "Keeta"]
    bv, gv = _vashya(bs, boy_moon % 30), _vashya(gs, girl_moon % 30)
    K.append({"koota": "Vashya", "max": 2, "score": VASHYA_TABLE[bv][gv], "boy": VSN[bv], "girl": VSN[gv], "meaning": "Mutual attraction and control"})
    t1 = ((bn - gn) % 27) % 9 + 1
    t2 = ((gn - bn) % 27) % 9 + 1
    tara = (0 if t1 in (3, 5, 7) else 1.5) + (0 if t2 in (3, 5, 7) else 1.5)
    K.append({"koota": "Tara", "max": 3, "score": tara, "boy": f"Tara {t2}", "girl": f"Tara {t1}", "meaning": "Destiny and well-being"})
    by, gy = YONI[bn], YONI[gn]
    pair = frozenset((by, gy))
    yo = 4 if by == gy else 0 if pair in YONI_ENEMY else 3 if pair in YONI_FRIEND else 2
    K.append({"koota": "Yoni", "max": 4, "score": yo, "boy": by, "girl": gy, "meaning": "Physical/intimate compatibility"})
    lb, lg = SIGN_LORD[bs], SIGN_LORD[gs]
    r1, r2 = relation(lb, lg), relation(lg, lb)
    rs = sorted([r1, r2])
    gm = 5 if lb == lg or rs == ["friend", "friend"] else 4 if rs == ["friend", "neutral"] else 3 if rs == ["neutral", "neutral"] else 1 if rs == ["enemy", "friend"] else 0.5 if rs == ["enemy", "neutral"] else 0
    K.append({"koota": "Graha Maitri", "max": 5, "score": gm, "boy": lb, "girl": lg, "meaning": "Mental wavelength, friendship"})
    GN = {"D": "Deva", "M": "Manushya", "R": "Rakshasa"}
    bg, gg = GANA[bn], GANA[gn]
    gt = {("D", "D"): 6, ("D", "M"): 6, ("D", "R"): 1, ("M", "D"): 5, ("M", "M"): 6, ("M", "R"): 0, ("R", "D"): 1, ("R", "M"): 0, ("R", "R"): 6}
    K.append({"koota": "Gana", "max": 6, "score": gt[(bg, gg)], "boy": GN[bg], "girl": GN[gg], "meaning": "Temperament"})
    dist = house_from(bs, gs)
    bh = 0 if dist in (2, 12, 5, 9, 6, 8) else 7
    bh_cancel = bh == 0 and (lb == lg or rs == ["friend", "friend"])
    K.append({"koota": "Bhakoot", "max": 7, "score": 7 if bh_cancel else bh, "boy": SIGNS[bs], "girl": SIGNS[gs], "meaning": "Love, family welfare, finances", "note": "Bhakoot dosha cancelled (same/friendly lords)" if bh_cancel else ("Bhakoot dosha" if bh == 0 else None)})
    bnd, gnd = NADI[bn % 6], NADI[gn % 6]
    nadi_cancel = bnd == gnd and (bn == gn and nakshatra(boy_moon)["pada"] != nakshatra(girl_moon)["pada"] or (bs == gs and bn != gn))
    nd = 8 if bnd != gnd or nadi_cancel else 0
    K.append({"koota": "Nadi", "max": 8, "score": nd, "boy": bnd, "girl": gnd, "meaning": "Health, genetics, progeny", "note": "Nadi dosha cancelled" if nadi_cancel else ("Nadi dosha" if nd == 0 else None)})
    total = sum(k["score"] for k in K)
    manglik = None
    if boy_chart and girl_chart:
        bm = next(d for d in boy_chart["doshas"] if d["name"].startswith("Manglik"))
        gmk = next(d for d in girl_chart["doshas"] if d["name"].startswith("Manglik"))
        ok = bm["present"] == gmk["present"] or (bm["present"] and bm["cancellations"]) or (gmk["present"] and gmk["cancellations"])
        manglik = {"boy": bm["present"], "girl": gmk["present"], "boy_severity": bm["severity"], "girl_severity": gmk["severity"], "compatible": bool(ok),
                   "note": "Both Manglik or both non-Manglik — dosha neutralised." if bm["present"] == gmk["present"] else ("One partner Manglik; cancellation present." if ok else "One partner Manglik without cancellation — remedies advised.")}
    verdict = "Excellent match" if total >= 32 else "Very good match" if total >= 25 else "Acceptable match" if total >= 18 else "Not recommended"
    rec = {"Excellent match": "Highly compatible; proceed with confidence.", "Very good match": "Strong compatibility; minor differences manageable.", "Acceptable match": "Average compatibility; review weak kootas and doshas with remedies.", "Not recommended": "Below 18 gunas; traditional guidance advises against unless strong cancellations exist."}[verdict]
    if any(k.get("note") in ("Nadi dosha", "Bhakoot dosha") for k in K):
        rec += " Major dosha present (" + ", ".join(k["note"] for k in K if k.get("note") in ("Nadi dosha", "Bhakoot dosha")) + ") — consult remedies."
    return {"kootas": K, "total": total, "max": 36, "percentage": round(total / 36 * 100), "verdict": verdict, "recommendation": rec, "manglik": manglik}


# ---------- Numerology ----------
PYTH = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
CHALDEAN = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [1, 2, 3, 4, 5, 8, 3, 5, 1, 1, 2, 3, 4, 5, 7, 8, 1, 2, 3, 4, 6, 6, 6, 5, 1, 7]))
NUM_MEANING = {1: ("Sun", "Leader, independent, pioneering"), 2: ("Moon", "Diplomat, sensitive, cooperative"), 3: ("Jupiter", "Creative, expressive, optimistic"), 4: ("Rahu", "Builder, practical, disciplined"),
               5: ("Mercury", "Free spirit, adaptable, communicator"), 6: ("Venus", "Nurturer, harmonious, artistic"), 7: ("Ketu", "Seeker, analytical, spiritual"), 8: ("Saturn", "Executive, ambitious, karmic"),
               9: ("Mars", "Humanitarian, courageous, compassionate"), 11: ("Master", "Intuitive illuminator"), 22: ("Master", "Master builder"), 33: ("Master", "Master teacher")}


def _reduce(n: int, keep_master=True) -> int:
    while n > 9 and not (keep_master and n in (11, 22, 33)):
        n = sum(int(x) for x in str(n))
    return n


def numerology(name: str, dob: date) -> dict:
    letters = [c for c in name.upper() if c.isalpha()]
    vowels = [c for c in letters if c in "AEIOU"]
    cons = [c for c in letters if c not in "AEIOU"]
    lp = _reduce(_reduce(dob.day) + _reduce(dob.month) + _reduce(sum(int(x) for x in str(dob.year))))
    res = {"life_path": lp, "birth_number": _reduce(dob.day, False), "destiny": _reduce(sum(PYTH[c] for c in letters)), "soul_urge": _reduce(sum(PYTH[c] for c in vowels)),
           "personality": _reduce(sum(PYTH[c] for c in cons)), "chaldean_name": _reduce(sum(CHALDEAN[c] for c in letters), False),
           "personal_year": _reduce(_reduce(dob.day) + _reduce(dob.month) + _reduce(sum(int(x) for x in str(date.today().year))), False)}
    return {"numbers": res, "meanings": {k: {"number": v, "planet": NUM_MEANING[v][0], "meaning": NUM_MEANING[v][1]} for k, v in res.items()},
            "lucky": {"numbers": sorted({res["birth_number"], res["life_path"] if res["life_path"] < 10 else _reduce(res["life_path"], False)}), "day": REMEDY_DB[NUM_MEANING[res["birth_number"]][0] if NUM_MEANING[res["birth_number"]][0] in REMEDY_DB else "Sun"]["day"]}}
