import asyncio
import hashlib
import secrets
import sys
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

# pyrefly: ignore[missing-import]
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel, ConfigDict, Field

# Support running directly (e.g. `python backend/app/main.py`) or as a module
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from backend.app import database
    from backend.app import crypto
    from backend.app.ai import build_prompt, query_gemini
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
    from .ai import build_prompt, query_gemini
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
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"pbkdf2_sha256$100000${salt}${dk.hex()}"


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
    db = await require_db()
    if not token:
        raise HTTPException(status_code=401, detail="Sign in to use this workspace.")
    try:
        now = datetime.now(UTC)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        session = await db.sessions.find_one(
            {"token_hash": token_hash, "expires_at": {"$gt": now}}, {"_id": 0}
        )
        if not session:
            await db.sessions.delete_one({"token_hash": token_hash})
            raise HTTPException(status_code=401, detail="Your session expired. Please sign in again.")
        user = await db.users.find_one(
            {"id": session["user_id"]}, {"_id": 0, "password_hash": 0}
        )
        if not user:
            await db.sessions.delete_one({"token_hash": token_hash})
            raise HTTPException(status_code=401, detail="Your account session is no longer valid.")
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not verify your session. Please try again.") from exc


def public_user(user: dict) -> dict:
    return {"id": user["id"], "username": crypto.decrypt_value(user["username"])}


async def issue_session(db, user_id: str, request: Request, response: Response):
    old_token = request.cookies.get(SESSION_COOKIE)
    if old_token:
        await db.sessions.delete_one(
            {"token_hash": hashlib.sha256(old_token.encode()).hexdigest()}
        )
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
    await issue_session(db, user_id, request, response)
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
    await issue_session(db, user["id"], request, response)
    return {"user": public_user(user)}


@app.post("/api/auth/signout")
async def signout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token and await database.ensure_connected():
        await database.db.sessions.delete_one(
            {"token_hash": hashlib.sha256(token.encode()).hexdigest()}
        )
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
    if not token or not await database.ensure_connected():
        return {"user": None}
    token_hash = hashlib.sha256(token.encode()).hexdigest()
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
            "calculation": calculation,
        }
        await db.kundli_records.insert_one(record, session=session)
        await db.planetary_calculations.insert_one(
            {
                "id": str(uuid4()),
                "owner_id": user["id"],
                "profile_id": profile_id,
                "kundli_record_id": record_id,
                "created_at": now,
                "calculation": calculation,
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
    if calc.get("dasha") and "analysis" not in calc:  # older records: derive analysis on read
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


@app.post("/api/assistant")
async def assistant(payload: AssistantQuestion, user: dict = Depends(authenticated_user)):
    if AI_PROVIDER.lower() != "gemini":
        raise HTTPException(
            status_code=503,
            detail=f"AI_PROVIDER '{AI_PROVIDER}' is not implemented. Configure AI_PROVIDER=gemini.",
        )

    profile = None
    calculation = None

    if payload.profile_id:
        db = await require_db()
        profile = await db.profiles.find_one(
            {"id": payload.profile_id, "owner_id": user["id"]}, {"_id": 0}
        )
        if not profile:
            raise HTTPException(status_code=404, detail="That saved profile was not found.")
        latest_record = await db.kundli_records.find_one(
            {"profile_id": payload.profile_id, "owner_id": user["id"]},
            sort=[("created_at", -1)],
        )
        if not latest_record:
            raise HTTPException(
                status_code=409,
                detail="This profile has no saved calculation yet. Create a Kundli before asking chart-specific questions.",
            )
        calculation = latest_record.get("calculation") or latest_record.get("chart")
        if not calculation:
            raise HTTPException(
                status_code=409,
                detail="The saved record has no verified calculation output to provide as context.",
            )

    prompt = build_prompt(payload.question, calculation=calculation)
    history = [turn.model_dump() for turn in payload.history]
    try:
        answer = await run_in_threadpool(query_gemini, prompt, history)
        return {
            "answer": answer,
            "profile_id": payload.profile_id,
            "context_used": bool(calculation),
        }
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc


if __name__ == "__main__":
    # pyrefly: ignore[missing-import]
    import uvicorn

    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True, reload_dirs=[str(Path(__file__).parent)])
