from datetime import date, time
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# pyrefly: ignore[missing-import]
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class BirthInput(BaseModel):
    """Validated input for the supported D1 birth-chart calculation."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    profile_id: str | None = Field(default=None, max_length=100)
    birth_date: date
    birth_time: time
    birthplace: str = Field(default="", max_length=250)
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    timezone: str = Field(min_length=1, max_length=100)
    ayanamsa: Literal["lahiri", "raman", "kp", "yukteshwar", "fagan_bradley"] = "lahiri"
    house_system: Literal["whole_sign", "equal", "placidus", "kp"] = "whole_sign"
    chart_style: Literal["north", "south", "east"] = "north"
    node_type: Literal["true", "mean"] = "true"
    description: str = Field(default="", max_length=1000)

    @field_validator("birthplace", "description", mode="before")
    @classmethod
    def coerce_none_and_str(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("profile_id", mode="before")
    @classmethod
    def coerce_empty_profile_id(cls, value: object) -> str | None:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return str(value).strip()

    @field_validator("ayanamsa", "chart_style", "node_type", "house_system", mode="before")
    @classmethod
    def lowercase_enums(cls, value: object) -> object:
        if isinstance(value, str):
            return value.lower().strip()
        return value

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def coerce_coords(cls, value: object) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            val = value.strip()
            if not val:
                raise ValueError("Geographical coordinate must be a valid number.")
            return float(val)
        return value

    @field_validator("birth_date")
    @classmethod
    def reasonable_birth_date(cls, value: date) -> date:
        if value.year < 1600:
            raise ValueError(
                "Birth dates before 1600 are not supported by this calculation setup."
            )
        return value

    @field_validator("birth_time")
    @classmethod
    def local_wall_clock_time_only(cls, value: time) -> time:
        if value.tzinfo is not None and value.utcoffset() is not None:
            raise ValueError(
                "Enter the local wall-clock birth time; select its IANA time zone separately."
            )
        return value

    @field_validator("timezone")
    @classmethod
    def valid_iana_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Enter a valid IANA time zone, such as Asia/Kolkata.") from exc
        return value


class AssistantTurn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class AssistantQuestion(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    question: str = Field(min_length=1, max_length=8000)
    profile_id: str | None = Field(default=None, min_length=1, max_length=100)
    history: list[AssistantTurn] = Field(default_factory=list, max_length=10)


class Credentials(BaseModel):
    """Username plus password; the password remains exact and is redacted in repr."""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]{3,32}$")
    password: SecretStr = Field(min_length=10, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def trim_username(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value
