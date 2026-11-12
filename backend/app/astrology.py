"""Thin adapter: full Vedic chart via the jyotish engine."""
from .jyotish import EPHE, build_chart
from .schemas import BirthInput

EPHEMERIS_FILES_AVAILABLE = EPHE


def calculate_kundli(birth: BirthInput) -> dict:
    chart = build_chart(birth.birth_date, birth.birth_time, birth.timezone, birth.latitude, birth.longitude,
                        birth.ayanamsa, birth.node_type, birth.house_system)
    chart["settings"]["chart_style"] = birth.chart_style
    chart["house_system"] = birth.house_system
    return chart
