"""Conversion between volume units used in ingredient lines.

US customary volume units (tsp/tbsp/cup) are defined here as exact fractions
of a liter, derived from the US gallon (3.785411784 L, itself exact under the
international inch definition) -- so these conversions never introduce
rounding error, unlike converting through floating point mL/oz tables.
"""

from __future__ import annotations

from fractions import Fraction

VOLUME_UNITS = {"tsp", "tbsp", "cup", "ml", "l"}

_ALIASES = {
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "cup": "cup", "cups": "cup",
    "ml": "ml", "milliliter": "ml", "milliliters": "ml",
    "millilitre": "ml", "millilitres": "ml",
    "l": "l", "liter": "l", "liters": "l", "litre": "l", "litres": "l",
}

_GALLON_ML = Fraction("3785.411784")

# Milliliters per unit -- the common base every conversion routes through.
_ML_PER_UNIT = {
    "tsp": _GALLON_ML / 768,
    "tbsp": _GALLON_ML / 256,
    "cup": _GALLON_ML / 16,
    "ml": Fraction(1),
    "l": Fraction(1000),
}


class UnitError(ValueError):
    """Raised when a unit name or conversion can't be understood."""


def is_volume_unit(unit: str) -> bool:
    """Return True if `unit` (any known alias) names a volume unit."""
    return unit.lower() in _ALIASES


def normalize_volume_unit(unit: str) -> str:
    """Map a unit alias (e.g. "tablespoons") to its canonical form ("tbsp")."""
    try:
        return _ALIASES[unit.lower()]
    except KeyError:
        raise UnitError(f"not a volume unit: {unit!r}") from None


def convert_volume(quantity: Fraction, from_unit: str, to_unit: str) -> Fraction:
    """Convert `quantity` from one volume unit to another, exactly.

    Accepts any known alias for either unit, e.g. convert_volume(3, "tsp",
    "tablespoons") works the same as convert_volume(3, "tsp", "tbsp").
    """
    from_canon = normalize_volume_unit(from_unit)
    to_canon = normalize_volume_unit(to_unit)
    milliliters = quantity * _ML_PER_UNIT[from_canon]
    return milliliters / _ML_PER_UNIT[to_canon]
