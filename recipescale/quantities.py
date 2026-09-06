"""Parsing and formatting for the numeric part of an ingredient line."""

from __future__ import annotations

import re
from fractions import Fraction


class QuantityError(ValueError):
    """Raised when a quantity string can't be understood in strict mode."""


# Unicode vulgar fractions people actually paste into recipes.
_UNICODE_FRACTIONS = {
    "¼": Fraction(1, 4), "½": Fraction(1, 2), "¾": Fraction(3, 4),
    "⅓": Fraction(1, 3), "⅔": Fraction(2, 3),
    "⅕": Fraction(1, 5), "⅖": Fraction(2, 5), "⅗": Fraction(3, 5), "⅘": Fraction(4, 5),
    "⅙": Fraction(1, 6), "⅚": Fraction(5, 6),
    "⅛": Fraction(1, 8), "⅜": Fraction(3, 8), "⅝": Fraction(5, 8), "⅞": Fraction(7, 8),
}

_MIXED_ASCII_RE = re.compile(r"^(\d+)\s+(\d+)/(\d+)$")
_SIMPLE_ASCII_RE = re.compile(r"^(\d+)/(\d+)$")
_DECIMAL_RE = re.compile(r"^\d+\.\d+$")
_INT_RE = re.compile(r"^\d+$")
_MIXED_UNICODE_RE = re.compile(r"^(\d+)\s*([¼½¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])$")
_RANGE_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)$")
_FIRST_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?(?:/\d+)?")


def parse_quantity(text: str, *, lenient: bool = False) -> Fraction:
    """Parse a quantity like "2", "1/2", "1 1/2", or "¾" into a Fraction.

    In strict mode (the default) anything outside those forms is rejected.
    In lenient mode, ranges ("2-3") are averaged and noisy strings have their
    first number-like token pulled out instead of failing outright.
    """
    raw = text.strip()
    if not raw:
        raise QuantityError("empty quantity")

    if raw in _UNICODE_FRACTIONS:
        return _UNICODE_FRACTIONS[raw]

    match = _MIXED_UNICODE_RE.match(raw)
    if match:
        whole, frac_char = match.groups()
        return int(whole) + _UNICODE_FRACTIONS[frac_char]

    match = _MIXED_ASCII_RE.match(raw)
    if match:
        whole, num, den = (int(x) for x in match.groups())
        if den == 0:
            raise QuantityError(f"zero denominator in {text!r}")
        return whole + Fraction(num, den)

    match = _SIMPLE_ASCII_RE.match(raw)
    if match:
        num, den = (int(x) for x in match.groups())
        if den == 0:
            raise QuantityError(f"zero denominator in {text!r}")
        return Fraction(num, den)

    if _DECIMAL_RE.match(raw):
        return Fraction(raw)

    if _INT_RE.match(raw):
        return Fraction(int(raw))

    if lenient:
        match = _RANGE_RE.match(raw)
        if match:
            low, high = (Fraction(x) for x in match.groups())
            return (low + high) / 2

        found = _FIRST_NUMBER_RE.search(raw)
        if found:
            try:
                return parse_quantity(found.group(0), lenient=False)
            except QuantityError:
                pass

    raise QuantityError(f"cannot parse quantity {text!r}")


def format_quantity(value: Fraction) -> str:
    """Render a Fraction as a mixed number, e.g. Fraction(3, 2) -> "1 1/2"."""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    whole, remainder = divmod(value.numerator, value.denominator)
    if whole:
        return f"{whole} {remainder}/{value.denominator}"
    return f"{value.numerator}/{value.denominator}"
