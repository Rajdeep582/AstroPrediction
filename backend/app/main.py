import asyncio
import json
import hashlib
import secrets
import sys
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

# pyrefly: ignore[missing-import]
from fastapi import Depends, FastAPI, HTTPException, Request, Response

# pyrefly: ignore[missing-import]
from fastapi.concurrency import run_in_threadpool

# pyrefly: ignore[missing-import]
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse

# pyrefly: ignore[missing-import]
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel, ConfigDict, Field

# Support running directly (e.g. `python backend/app/main.py`) or as a module
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from backend.app import database
    from backend.app import crypto
    from backend.app import ai as ai_mod
    from backend.app.astrology import calculate_kundli
    from backend.app.config import (
        AI_PROVIDER,
        API_HOST,
        API_PORT,
        FRONTEND_ORIGINS,
        SESSION_HTTPS_ONLY,
    )
    from backend.app.schemas import AssistantQuestion, BirthInput, Credentials
    from backend.app.routes import router as jyotish_router
else:
    from . import database
    from . import crypto
    from . import ai as ai_mod
    from .astrology import calculate_kundli
    from .config import (
        AI_PROVIDER,
        API_HOST,
        API_PORT,
        FRONTEND_ORIGINS,
        SESSION_HTTPS_ONLY,
    )
    from .schemas import AssistantQuestion, BirthInput, Credentials
    from .routes import router as jyotish_router

# Password hashing with Argon2id (via pwdlib) and PBKDF2 fallback
try:
    # pyrefly: ignore[missing-import]
    from pwdlib import PasswordHash
    from pwdlib.hashers.argon2 import Argon2Hasher

    # Lighten Argon2 cost for snappy response on cloud instances (1 pass, 19MB, 1 thread)
    _pwd_hasher = PasswordHash((Argon2Hasher(time_cost=1, memory_cost=19456, parallelism=1),))
except Exception:
    try:
        from pwdlib import PasswordHash
        _pwd_hasher = PasswordHash.recommended()
    except Exception:
        _pwd_hasher = None


def hash_password(password: str) -> str:
    if _pwd_hasher is not None:
        try:
            return _pwd_hasher.hash(password)
        except Exception:
            pass
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 25_000
    )
    return f"pbkdf2_sha256$25000${salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    if _pwd_hasher is not None and hashed.startswith("$argon2"):
        try:
            return _pwd_hasher.verify(password, hashed)
        except Exception:
            return False
    if hashed.startswith("pbkdf2_sha256$"):
        try:
            parts = hashed.split("$")
            if len(parts) == 4:
                iterations = int(parts[1])
                salt = parts[2]
                expected_hex = parts[3]
                dk = hashlib.pbkdf2_hmac(
                    "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
                )
                return secrets.compare_digest(dk.hex(), expected_hex)
        except Exception:
            return False
    if _pwd_hasher is not None:
        try:
            return _pwd_hasher.verify(password, hashed)
        except Exception:
            return False
    return False


DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(24))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect in the background so a slow/unreachable cluster never blocks server startup.
    task = asyncio.create_task(database.ensure_connected(min_interval=0))
    yield
    task.cancel()
    await database.close_database()


app = FastAPI(title="Jyotish Studio API", version="0.2.0", lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jyotish_router)

SESSION_COOKIE = "jyotish_session"
SESSION_LIFETIME = 60 * 60 * 24 * 14
COOKIE_SAMESITE = "none" if SESSION_HTTPS_ONLY else "lax"
SESSION_CACHE_TTL = 60.0  # cache active sessions in-memory for 60s to avoid redundant Atlas roundtrips
_session_cache: dict[str, tuple[float, dict]] = {}


def invalidate_session(token_hash: str | None = None, user_id: str | None = None):
    if token_hash:
        _session_cache.pop(token_hash, None)
    if user_id:
        to_del = [k for k, (_, u) in _session_cache.items() if u.get("id") == user_id]
        for k in to_del:
            _session_cache.pop(k, None)


async def require_db():
    await database.ensure_connected()
    if database.db is None:
        raise HTTPException(
            status_code=503,
            detail="MongoDB is not connected. Check the backend environment and Atlas network access.",
        )
    return database.db


def serialize(document: dict) -> dict:
    return {key: value for key, value in document.items() if key != "_id"}


async def authenticated_user(request: Request) -> dict:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Sign in to use this workspace.")
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # Instant in-memory cache check: eliminates roundtrip DB lookups for active users
    cached = _session_cache.get(token_hash)
    if cached is not None:
        exp, user = cached
        if time.monotonic() < exp:
            return user
        _session_cache.pop(token_hash, None)

    db = await require_db()
    try:
        now = datetime.now(UTC)
        session = await db.sessions.find_one(
            {"token_hash": token_hash, "expires_at": {"$gt": now}}, {"_id": 0}
        )
        if not session:
            await db.sessions.delete_one({"token_hash": token_hash})
            _session_cache.pop(token_hash, None)
            raise HTTPException(status_code=401, detail="Your session expired. Please sign in again.")
        user = await db.users.find_one(
            {"id": session["user_id"]}, {"_id": 0, "password_hash": 0}
        )
        if not user:
            await db.sessions.delete_one({"token_hash": token_hash})
            _session_cache.pop(token_hash, None)
            raise HTTPException(status_code=401, detail="Your account session is no longer valid.")

        _session_cache[token_hash] = (time.monotonic() + SESSION_CACHE_TTL, user)
        if len(_session_cache) > 1000:
            now_m = time.monotonic()
            stale = [k for k, (e, _) in _session_cache.items() if e < now_m]
            for k in stale:
                _session_cache.pop(k, None)

        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not verify your session. Please try again.") from exc


def public_user(user: dict) -> dict:
    return {"id": user["id"], "username": crypto.decrypt_value(user["username"])}


async def issue_session(db, user_id: str, request: Request, response: Response, cached_user: dict | None = None):
    old_token = request.cookies.get(SESSION_COOKIE)
    if old_token:
        old_hash = hashlib.sha256(old_token.encode()).hexdigest()
        invalidate_session(token_hash=old_hash)
        await db.sessions.delete_one({"token_hash": old_hash})
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.now(UTC)
    await db.sessions.insert_one(
        {
            "token_hash": token_hash,
            "user_id": user_id,
            "created_at": now,
            "expires_at": now + timedelta(seconds=SESSION_LIFETIME),
        }
    )
    if cached_user:
        _session_cache[token_hash] = (time.monotonic() + SESSION_CACHE_TTL, cached_user)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_LIFETIME,
        path="/",
        secure=SESSION_HTTPS_ONLY,
        httponly=True,
        samesite=COOKIE_SAMESITE,
    )


@app.get("/api/health")
async def health():
    if not database.connecting:
        await database.ensure_connected(min_interval=5)
    return {
        "status": "ok",
        "database": "connected" if database.db is not None else ("connecting" if database.connecting else "unavailable"),
        "encryption": "enabled" if crypto.enabled() else "disabled",
        "database_error": database.last_error if database.db is None else None,
    }


@app.post("/api/auth/signup")
async def signup(credentials: Credentials, request: Request, response: Response):
    db = await require_db()
    username_normalized = crypto.blind_index(credentials.username.lower())
    user_id = str(uuid4())
    password = credentials.password.get_secret_value()
    if len(password) > 10:
        raise HTTPException(status_code=422, detail="Password must be 4 to 10 characters.")
    pw_hash = await run_in_threadpool(hash_password, password)
    user = {
        "id": user_id,
        "username": crypto.encrypt_value(credentials.username),
        "username_normalized": username_normalized,
        "password_hash": pw_hash,
        "created_at": datetime.now(UTC).isoformat(),
    }
    try:
        await db.users.insert_one(user)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409, detail="That username is already in use."
        ) from exc
    await issue_session(db, user_id, request, response, cached_user={k: v for k, v in user.items() if k not in ("password_hash", "_id")})
    return {"user": public_user(user)}


@app.post("/api/auth/signin")
async def signin(credentials: Credentials, request: Request, response: Response):
    db = await require_db()
    user = await db.users.find_one(
        {"username_normalized": crypto.blind_index(credentials.username.lower())}
    )
    candidate_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
    valid = await run_in_threadpool(
        verify_password, credentials.password.get_secret_value(), candidate_hash
    )
    if not user or not valid:
        raise HTTPException(
            status_code=401, detail="Username or password is incorrect."
        )
    await issue_session(db, user["id"], request, response, cached_user={k: v for k, v in user.items() if k not in ("password_hash", "_id")})
    return {"user": public_user(user)}


@app.post("/api/auth/signout")
async def signout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invalidate_session(token_hash=token_hash)
        if await database.ensure_connected():
            await database.db.sessions.delete_one({"token_hash": token_hash})
    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        secure=SESSION_HTTPS_ONLY,
        httponly=True,
        samesite=COOKIE_SAMESITE,
    )
    return {"signed_out": True}


@app.get("/api/auth/me")
async def session_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return {"user": None}
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    cached = _session_cache.get(token_hash)
    if cached is not None:
        exp, user = cached
        if time.monotonic() < exp:
            return {"user": public_user(user)}
        _session_cache.pop(token_hash, None)

    if not await database.ensure_connected():
        return {"user": None}
    session = await database.db.sessions.find_one(
        {"token_hash": token_hash, "expires_at": {"$gt": datetime.now(UTC)}}, {"_id": 0}
    )
    if not session:
        return {"user": None}
    user = await database.db.users.find_one(
        {"id": session["user_id"]}, {"_id": 0, "password_hash": 0}
    )
    if not user:
        await database.db.sessions.delete_one({"token_hash": token_hash})
        return {"user": None}
    _session_cache[token_hash] = (time.monotonic() + SESSION_CACHE_TTL, user)
    return {"user": public_user(user)}


@app.get("/api/profiles")
async def list_profiles(user: dict = Depends(authenticated_user)):
    try:
        cursor = (
            database.db.profiles.find({"owner_id": user["id"]}, {"_id": 0})
            .sort("updated_at", -1)
            .limit(200)
        )
        return [crypto.decrypt_profile(record) async for record in cursor]
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Saved profiles could not be loaded.") from exc


@app.post("/api/kundli/calculate")
async def create_kundli(birth: BirthInput, user: dict = Depends(authenticated_user)):
    db = await require_db()
    try:
        calculation = calculate_kundli(birth)
    except (ValueError, OverflowError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    now = datetime.now(UTC).isoformat()
    profile_id = birth.profile_id or str(uuid4())
    birthplace = (
        birth.birthplace or ""
    ).strip() or f"Coordinates ({birth.latitude:.4f}, {birth.longitude:.4f})"
    description = (birth.description or "").strip()

    profile = {
        "id": profile_id,
        "owner_id": user["id"],
        "name": birth.name,
        "birth_date": birth.birth_date.isoformat(),
        "birth_time": birth.birth_time.isoformat(),
        "birthplace": birthplace,
        "latitude": birth.latitude,
        "longitude": birth.longitude,
        "timezone": birth.timezone,
        "description": description,
        "updated_at": now,
        "created_at": now,
    }

    record_id = str(uuid4())
    # Store lean documents: the analysis text is regenerated on read (~30 ms), and the positions
    # collection only needs the raw placements. Halves write size and speeds up reads.
    stored_calc = {k: v for k, v in calculation.items() if k != "analysis"}
    positions_only = {k: calculation[k] for k in ("planets", "ascendant", "settings", "ayanamsa_degrees", "engine") if k in calculation}

    async def persist_chart(session):
        existing = await db.profiles.find_one(
            {"id": profile_id, "owner_id": user["id"]}, {"_id": 0}, session=session
        )
        if existing:
            profile["created_at"] = existing.get("created_at", now)
            await db.profiles.update_one(
                {"id": profile_id, "owner_id": user["id"]},
                {"$set": crypto.encrypt_profile(profile)},
                session=session,
            )
        else:
            await db.profiles.insert_one(crypto.encrypt_profile(profile), session=session)

        record = {
            "id": record_id,
            "owner_id": user["id"],
            "profile_id": profile_id,
            "created_at": now,
            "input": crypto.encrypt_value(birth.model_dump(mode="json")),
            "calculation": stored_calc,
        }
        await db.kundli_records.insert_one(record, session=session)
        await db.planetary_calculations.insert_one(
            {
                "id": str(uuid4()),
                "owner_id": user["id"],
                "profile_id": profile_id,
                "kundli_record_id": record_id,
                "created_at": now,
                "calculation": positions_only,
            },
            session=session,
        )

    try:
        if database.client is None:
            raise RuntimeError("MongoDB client is not connected.")
        async with database.client.start_session().bind() as session:
            await session.with_transaction(persist_chart)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The chart was calculated but could not be saved. Please retry.") from exc

    return {"profile": serialize(profile), "record_id": record_id, **calculation}


SUMMARY_FIELDS = ("ascendant", "moon_sign", "birth_nakshatra", "settings", "engine")


def summarize(calc: dict) -> dict:
    out = {k: calc[k] for k in SUMMARY_FIELDS if k in calc}
    if "dasha" in calc:
        out["dasha"] = {"current": calc["dasha"].get("current", [])}
    if "moon_sign" not in out:
        moon = next((p for p in calc.get("planets", []) if p.get("name") == "Moon"), None)
        if moon:
            out["moon_sign"] = moon.get("sign")
    out["full"] = "dasha" in calc
    return out


@app.get("/api/kundli/history")
async def kundli_history(user: dict = Depends(authenticated_user)):
    """Lightweight list; open a record with /api/kundli/records/{id}."""
    db = await require_db()
    projection = {"_id": 0, "id": 1, "profile_id": 1, "created_at": 1, "calculation.planets.name": 1, "calculation.planets.sign": 1, "calculation.dasha.current": 1}
    for field in SUMMARY_FIELDS:
        projection[f"calculation.{field}"] = 1
    try:
        cursor = db.kundli_records.find({"owner_id": user["id"]}, projection).sort("created_at", -1).limit(200)
        records = [record async for record in cursor]
        profile_ids = list({r.get("profile_id") for r in records if r.get("profile_id")})
        profiles = {
            p["id"]: crypto.decrypt_profile(p)
            async for p in db.profiles.find({"owner_id": user["id"], "id": {"$in": profile_ids}}, {"_id": 0, "id": 1, "name": 1})
        }
        return [
            {
                "record_id": r.get("id"),
                "profile_id": r.get("profile_id"),
                "profile_name": profiles.get(r.get("profile_id"), {}).get("name", "Deleted profile"),
                "created_at": r.get("created_at"),
                "calculation": summarize(r.get("calculation", {})),
            }
            for r in records
        ]
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Saved chart history could not be loaded.") from exc


@app.get("/api/kundli/records/{record_id}")
async def kundli_record(record_id: str, user: dict = Depends(authenticated_user)):
    db = await require_db()
    record = await db.kundli_records.find_one({"id": record_id, "owner_id": user["id"]}, {"_id": 0, "owner_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Saved reading not found.")
    profile = await db.profiles.find_one({"id": record.get("profile_id"), "owner_id": user["id"]}, {"_id": 0, "owner_id": 0})
    calc = record.get("calculation") or {}
    if calc.get("dasha") and (calc.get("analysis") or {}).get("version", 0) < 2:  # older records: (re)derive analysis on read
        try:
            from .analysis import build_analysis
            calc["analysis"] = build_analysis(calc)
        except Exception:
            pass
    record["calculation"] = calc
    return {"record_id": record["id"], "profile": crypto.decrypt_profile(profile), "input": crypto.decrypt_value(record.get("input")), "created_at": record.get("created_at"), **(record.get("calculation") or {})}


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=100)
    birthplace: str | None = Field(default=None, max_length=250)
    description: str | None = Field(default=None, max_length=1000)


@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: str, user: dict = Depends(authenticated_user)):
    db = await require_db()
    profile = await db.profiles.find_one({"id": profile_id, "owner_id": user["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return crypto.decrypt_profile(profile)


@app.patch("/api/profiles/{profile_id}")
async def update_profile(profile_id: str, payload: ProfileUpdate, user: dict = Depends(authenticated_user)):
    db = await require_db()
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Nothing to update.")
    changes = crypto.encrypt_profile(changes)
    changes["updated_at"] = datetime.now(UTC).isoformat()
    result = await db.profiles.find_one_and_update(
        {"id": profile_id, "owner_id": user["id"]}, {"$set": changes},
        projection={"_id": 0}, return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return crypto.decrypt_profile(result)


@app.delete("/api/kundli/records/{record_id}")
async def delete_record(record_id: str, user: dict = Depends(authenticated_user)):
    db = await require_db()
    result = await db.kundli_records.delete_one({"id": record_id, "owner_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved reading not found.")
    await db.planetary_calculations.delete_many({"kundli_record_id": record_id, "owner_id": user["id"]})
    return {"deleted": True}


@app.delete("/api/auth/account")
async def delete_account(request: Request, response: Response, user: dict = Depends(authenticated_user)):
    db = await require_db()
    for name in await db.list_collection_names():
        if name in ("users", "sessions", "knowledge_sources", "knowledge_chunks"):
            continue
        await db[name].delete_many({"owner_id": user["id"]})
    await db.sessions.delete_many({"user_id": user["id"]})
    await db.users.delete_one({"id": user["id"]})
    invalidate_session(user_id=user["id"])
    response.delete_cookie(key=SESSION_COOKIE, path="/", secure=SESSION_HTTPS_ONLY, httponly=True, samesite=COOKIE_SAMESITE)
    return {"deleted": True}


@app.delete("/api/profiles/{profile_id}")
async def delete_profile(profile_id: str, user: dict = Depends(authenticated_user)):
    db = await require_db()
    async def delete_saved_data(session):
        existing = await db.profiles.find_one({"id": profile_id, "owner_id": user["id"]}, {"_id": 1})
        if not existing:
            raise HTTPException(status_code=404, detail="Profile not found.")
        for collection in (
            "kundli_records",
            "planetary_calculations",
            "divisional_charts",
            "dasha_records",
            "palmistry_sessions",
            "palm_images",
            "palm_features",
            "palm_reports",
            "combined_reports",
            "conversations",
            "messages",
            "saved_reports",
        ):
            await db[collection].delete_many(
                {"owner_id": user["id"], "profile_id": profile_id}, session=session
            )

        result = await db.profiles.delete_one(
            {"id": profile_id, "owner_id": user["id"]}, session=session
        )
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        if database.client is None:
            raise RuntimeError("MongoDB client is not connected.")
        async with database.client.start_session().bind() as session:
            await session.with_transaction(delete_saved_data)
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The profile could not be fully deleted. Please retry.") from exc


# ───────── AI Astrologer ─────────
_ctx_cache: dict[tuple[str, str], tuple[float, str, dict]] = {}
CTX_TTL = 1800.0


async def _chart_context(user: dict, profile_id: str) -> tuple[str, dict]:
    """Load the latest saved chart for a profile and build the AI briefing (cached 30 min)."""
    key = (user["id"], profile_id)
    hit = _ctx_cache.get(key)
    if hit and time.monotonic() < hit[0]:
        return hit[1], hit[2]
    db = await require_db()
    profile, record = await asyncio.gather(
        db.profiles.find_one({"id": profile_id, "owner_id": user["id"]}, {"_id": 0, "name": 1}),
        db.kundli_records.find_one({"profile_id": profile_id, "owner_id": user["id"]}, {"_id": 0, "calculation": 1}, sort=[("created_at", -1)]),
    )
    if not profile:
        raise HTTPException(status_code=404, detail="That saved profile was not found.")
    calc = (record or {}).get("calculation")
    if not calc or not calc.get("dasha"):
        raise HTTPException(status_code=409, detail="This profile has no full Kundli yet. Create one in the Kundli studio first.")
    if (calc.get("analysis") or {}).get("version", 0) < 2:
        from .analysis import build_analysis
        calc["analysis"] = await run_in_threadpool(build_analysis, calc)
    name = crypto.decrypt_value(profile.get("name"))
    context = await run_in_threadpool(ai_mod.build_context, calc, name)
    cur = calc["dasha"].get("current") or []
    summary = {
        "name": name, "lagna": calc["ascendant"]["sign"], "moon": calc.get("moon_sign"),
        "nakshatra": calc["birth_nakshatra"]["name"],
        "dasha": " / ".join(d["lord"] for d in cur[:2]),
        "yogas": sum(1 for y in calc.get("yogas", []) if y.get("present")),
        "facts": len(context.splitlines()),
    }
    _ctx_cache[key] = (time.monotonic() + CTX_TTL, context, summary)
    if len(_ctx_cache) > 500:
        _ctx_cache.clear()
    return context, summary


class AssistantPrepare(BaseModel):
    profile_id: str = Field(min_length=1, max_length=100)


@app.post("/api/assistant/prepare")
async def assistant_prepare(payload: AssistantPrepare, user: dict = Depends(authenticated_user)):
    """Study the chart up-front so questions answer immediately."""
    _, summary = await _chart_context(user, payload.profile_id)
    return {"ready": True, "summary": summary}


@app.post("/api/assistant/stream")
async def assistant_stream(payload: AssistantQuestion, user: dict = Depends(authenticated_user)):
    context = (await _chart_context(user, payload.profile_id))[0] if payload.profile_id else None
    history = [t.model_dump() for t in payload.history]
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def worker():
        try:
            for chunk in ai_mod.stream_answer(payload.question, context, history):
                loop.call_soon_threadsafe(queue.put_nowait, ("t", chunk))
        except Exception as exc:  # surfaced to the client as an error event
            loop.call_soon_threadsafe(queue.put_nowait, ("e", str(exc)))
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, ("end", ""))

    loop.run_in_executor(None, worker)

    async def events():
        while True:
            kind, val = await queue.get()
            if kind == "end":
                yield "data: [DONE]\n\n"
                return
            yield f"data: {json.dumps({kind: val})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/assistant")
async def assistant(payload: AssistantQuestion, user: dict = Depends(authenticated_user)):
    context = (await _chart_context(user, payload.profile_id))[0] if payload.profile_id else None
    history = [t.model_dump() for t in payload.history]
    try:
        text = await run_in_threadpool(ai_mod.answer, payload.question, context, history)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"answer": text, "profile_id": payload.profile_id, "context_used": bool(context)}


if __name__ == "__main__":
    # pyrefly: ignore[missing-import]
    import uvicorn

    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True, reload_dirs=[str(Path(__file__).parent)])
