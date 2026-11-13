"""Public Jyotish computation endpoints (no persistence)."""
from datetime import UTC, date, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from . import jyotish as J
from .schemas import BirthInput

router = APIRouter(prefix="/api")
LOC = dict(lat=22.5726, lon=88.3639, tz="Asia/Kolkata")


def _chart(b: BirthInput) -> dict:
    try:
        c = J.build_chart(b.birth_date, b.birth_time, b.timezone, b.latitude, b.longitude, b.ayanamsa, b.node_type, b.house_system)
    except (ValueError, OverflowError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    c["settings"]["chart_style"] = b.chart_style
    return c


@router.post("/kundli/preview")
async def kundli_preview(birth: BirthInput):
    return await run_in_threadpool(_chart, birth)


class MatchInput(BaseModel):
    boy: BirthInput
    girl: BirthInput


@router.post("/match")
async def match(payload: MatchInput):
    b, g = await run_in_threadpool(_chart, payload.boy), await run_in_threadpool(_chart, payload.girl)
    bm, gm = J.P(b, "Moon")["absolute_longitude"], J.P(g, "Moon")["absolute_longitude"]
    res = J.guna_milan(bm, gm, b, g)
    slim = lambda c: {k: c[k] for k in ("ascendant", "planets", "houses", "moon_sign", "birth_nakshatra", "settings")} | {"D9": c["vargas"]["D9"]}
    return res | {"boy_chart": slim(b), "girl_chart": slim(g)}


@router.get("/panchang")
async def get_panchang(d: date | None = None, lat: float = Query(LOC["lat"], ge=-66, le=66), lon: float = Query(LOC["lon"], ge=-180, le=180), tz: str = LOC["tz"]):
    try:
        res = await run_in_threadpool(J.panchang, d or datetime.now(J.ZoneInfo(tz)).date(), lat, lon, tz)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Panchang unavailable: {exc}") from exc
    res.pop("_raw", None)
    return res


@router.get("/muhurta")
async def get_muhurta(event: Literal["marriage", "travel", "business", "housewarming", "vehicle", "education"], start: date | None = None, days: int = Query(60, ge=1, le=120),
                      lat: float = Query(LOC["lat"], ge=-66, le=66), lon: float = LOC["lon"], tz: str = LOC["tz"]):
    return {"event": event, "results": await run_in_threadpool(J.muhurta, event, start or date.today(), days, lat, lon, tz)}


@router.get("/festivals")
async def get_festivals(year: int = Query(..., ge=1900, le=2100), month: int | None = Query(None, ge=1, le=12), lat: float = LOC["lat"], lon: float = LOC["lon"], tz: str = LOC["tz"]):
    return {"year": year, "month": month, "events": await run_in_threadpool(J.festival_calendar, year, month, lat, lon, tz),
            "note": "Amanta lunar months; Adhika masa not separately flagged. Observance may shift a day by local custom."}


@router.get("/horoscope/{sign}")
async def horoscope(sign: str, period: Literal["daily", "weekly", "monthly", "yearly"] = "daily"):
    names = [s.lower() for s in J.SIGNS]
    if sign.lower() not in names:
        raise HTTPException(status_code=404, detail="Unknown rashi")
    return await run_in_threadpool(J.rashi_horoscope, names.index(sign.lower()), period)


@router.get("/transits")
async def transits(moon_sign: int = Query(0, ge=0, le=11), ayanamsa: str = "lahiri"):
    return await run_in_threadpool(J.gochar, None, None, moon_sign, ayanamsa)


class MoonSignInput(BaseModel):
    birth_date: date
    birth_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    timezone: str = "Asia/Kolkata"


@router.post("/moon-sign")
async def moon_sign(p: MoonSignInput):
    from datetime import time
    h, m = map(int, p.birth_time.split(":"))
    jd, _, _ = J.jd_from_local(p.birth_date, time(h, m), p.timezone)
    moon = J.planet_positions(jd)["Moon"]["lon"]
    nk = J.nakshatra(moon)
    return {"moon_sign": J.SIGNS[J.sign_of(moon)], "sign_index": J.sign_of(moon), "sign_lord": J.SIGN_LORD[J.sign_of(moon)], "nakshatra": nk["name"], "pada": nk["pada"], "nakshatra_lord": nk["lord"], "degree": J.dms(moon % 30)}


class NumerologyInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    birth_date: date


@router.post("/numerology")
async def numerology(p: NumerologyInput):
    return J.numerology(p.name, p.birth_date)


class DashaInterpretInput(BaseModel):
    birth: BirthInput
    lord: str
    sub: str | None = None


@router.post("/dasha/interpret")
async def dasha_interpret(p: DashaInterpretInput):
    if p.lord not in J.DASHA_ORDER or (p.sub and p.sub not in J.DASHA_ORDER):
        raise HTTPException(status_code=422, detail="Unknown dasha lord")
    c = await run_in_threadpool(_chart, p.birth)
    return {"lord": p.lord, "sub": p.sub, "interpretation": J.dasha_interpretation(c, p.lord, p.sub)}


@router.get("/reference")
async def reference():
    return {"signs": J.SIGNS, "nakshatras": J.NAKSHATRAS, "vargas": [{"d": n, "name": J.VARGA_NAMES[n], "signifies": J.VARGA_AREA[n]} for n in J.VARGAS],
            "ayanamsas": list(J.AYANAMSA), "house_systems": list(J.HOUSE_CODES), "houses": {k: {"name": v[1], "significations": v[0]} for k, v in J.HOUSE_SIG.items()},
            "planets": J.PLANET_NATURE, "remedies": J.REMEDY_DB, "dasha_years": J.DASHA_YEARS, "now": datetime.now(UTC).isoformat()}


_tzf = None


@router.get("/timezone")
async def timezone_at(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    """Resolve IANA zone for coordinates (offline polygon lookup)."""
    global _tzf
    try:
        if _tzf is None:
            # pyrefly: ignore[missing-import]
            from timezonefinder import TimezoneFinder
            _tzf = TimezoneFinder(in_memory=True)
        tz = _tzf.timezone_at(lng=lon, lat=lat) or _tzf.certain_timezone_at(lng=lon, lat=lat)
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="timezonefinder is not installed on the backend.") from exc
    return {"timezone": tz, "latitude": lat, "longitude": lon}


_geo_cache: dict[str, list[dict]] = {}
_reverse_cache: dict[str, str | None] = {}


@router.get("/location/search")
async def location_search(q: str = Query(..., min_length=2)):
    """Fast geocoding search using Open-Meteo with OpenStreetMap Nominatim fallback."""
    q_norm = q.strip().lower()
    if q_norm in _geo_cache:
        return {"places": _geo_cache[q_norm]}

    def _fetch():
        import urllib.parse
        import requests
        headers = {"User-Agent": "JyotishStudioApp/1.0 (admin@jyotish.app)", "Accept-Language": "en"}
        out = []

        # 1. Open-Meteo Geocoding API: ultra-fast, worldwide coverage
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(q)}&count=8&language=en&format=json"
            r = requests.get(url, headers=headers, timeout=3)
            if r.status_code == 200:
                data = r.json().get("results", [])
                for d in data:
                    name = d.get("name", "Unknown place")
                    details = [d.get("admin2"), d.get("admin1"), d.get("country")]
                    detail = ", ".join(filter(None, details))
                    out.append({
                        "name": name,
                        "detail": detail,
                        "lat": float(d["latitude"]),
                        "lon": float(d["longitude"]),
                        "kind": d.get("feature_code", "city"),
                    })
                if out:
                    return out
        except Exception:
            pass

        # 2. Fallback to OpenStreetMap Nominatim
        try:
            url = f"https://nominatim.openstreetmap.org/search?format=json&limit=8&q={urllib.parse.quote(q)}"
            r = requests.get(url, headers=headers, timeout=3.5)
            if r.status_code == 200:
                for d in r.json():
                    parts = d.get("display_name", "").split(", ")
                    name = parts[0] if parts else d.get("name", "Unknown place")
                    detail = ", ".join(parts[1:]) if len(parts) > 1 else ""
                    out.append({
                        "name": name,
                        "detail": detail,
                        "lat": float(d["lat"]),
                        "lon": float(d["lon"]),
                        "kind": d.get("type", "place"),
                    })
        except Exception:
            pass

        return out

    places = await run_in_threadpool(_fetch)
    if places:
        _geo_cache[q_norm] = places
        if len(_geo_cache) > 2000:
            _geo_cache.clear()
    return {"places": places}


@router.get("/location/reverse")
async def location_reverse(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    """Reverse geocode coordinates to location display name."""
    key = f"{lat:.4f},{lon:.4f}"
    if key in _reverse_cache:
        return {"name": _reverse_cache[key]}

    def _fetch():
        import requests
        headers = {"User-Agent": "JyotishStudioApp/1.0 (admin@jyotish.app)", "Accept-Language": "en"}
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14"
        try:
            r = requests.get(url, headers=headers, timeout=4)
            if r.status_code == 200:
                d = r.json()
                return d.get("display_name")
        except Exception:
            pass
        return None

    name = await run_in_threadpool(_fetch)
    _reverse_cache[key] = name
    if len(_reverse_cache) > 2000:
        _reverse_cache.clear()
    return {"name": name}

