"""Field-level encryption for personal data at rest (Fernet: AES-128-CBC + HMAC-SHA256)."""
import hashlib
import json
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from .config import DATA_ENCRYPTION_KEY

PREFIX = "enc:v1:"
_fernet = Fernet(DATA_ENCRYPTION_KEY.encode()) if DATA_ENCRYPTION_KEY else None

# Personal birth data on profiles that is encrypted at rest.
PROFILE_SECRET_FIELDS = ("name", "birth_date", "birth_time", "birthplace", "latitude", "longitude", "description")


def enabled() -> bool:
    return _fernet is not None


def encrypt_value(value: Any) -> Any:
    if _fernet is None or value is None:
        return value
    return PREFIX + _fernet.encrypt(json.dumps(value).encode()).decode()


def decrypt_value(value: Any) -> Any:
    if _fernet is None or not isinstance(value, str) or not value.startswith(PREFIX):
        return value
    try:
        return json.loads(_fernet.decrypt(value[len(PREFIX):].encode()))
    except (InvalidToken, ValueError):
        return None


def encrypt_fields(doc: dict, fields) -> dict:
    out = dict(doc)
    for f in fields:
        if f in out:
            out[f] = encrypt_value(out[f])
    return out


def decrypt_fields(doc: dict | None, fields) -> dict | None:
    if doc is None:
        return None
    out = dict(doc)
    for f in fields:
        if f in out:
            out[f] = decrypt_value(out[f])
    return out


def encrypt_profile(p: dict) -> dict:
    return encrypt_fields(p, PROFILE_SECRET_FIELDS)


def decrypt_profile(p: dict | None) -> dict | None:
    return decrypt_fields(p, PROFILE_SECRET_FIELDS)


def blind_index(value: str) -> str:
    """Deterministic keyed hash so encrypted values can still be looked up."""
    key = (DATA_ENCRYPTION_KEY or "jyotish").encode()
    return hashlib.blake2b(value.encode(), key=key[:64], digest_size=32).hexdigest()
