"""Conversion between weight units used in ingredient lines.

Ounces and pounds are defined here as exact fractions of a gram, using the
international avoirdupois definitions (1 lb = 453.59237 g exactly, 1 oz =
1/16 lb) -- so these conversions never introduce rounding error, same
approach as the volume conversions in units.py.
"""

from __future__ import annotations

from fractions import Fraction

WEIGHT_UNITS = {"g", "oz", "lb", "kg"}

_ALIASES = {
    "g": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
}

_LB_GRAMS = Fraction("453.59237")

# Grams per unit -- the common base every conversion routes through.
_G_PER_UNIT = {
    "g": Fraction(1),
    "kg": Fraction(1000),
    "lb": _LB_GRAMS,
    "oz": _LB_GRAMS / 16,
}


class UnitError(ValueError):
    """Raised when a unit name or conversion can't be understood."""


def is_weight_unit(unit: str) -> bool:
    """Return True if `unit` (any known alias) names a weight unit."""
    return unit.lower() in _ALIASES


def normalize_weight_unit(unit: str) -> str:
    """Map a unit alias (e.g. "pounds") to its canonical form ("lb")."""
    try:
        return _ALIASES[unit.lower()]
    except KeyError:
        raise UnitError(f"not a weight unit: {unit!r}") from None


def convert_weight(quantity: Fraction, from_unit: str, to_unit: str) -> Fraction:
    """Convert `quantity` from one weight unit to another, exactly.

    Accepts any known alias for either unit, e.g. convert_weight(1, "lb",
    "ounces") works the same as convert_weight(1, "lb", "oz").
    """
    from_canon = normalize_weight_unit(from_unit)
    to_canon = normalize_weight_unit(to_unit)
    grams = quantity * _G_PER_UNIT[from_canon]
    return grams / _G_PER_UNIT[to_canon]
