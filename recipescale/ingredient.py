"""Parsing whole ingredient lines into structured quantity/unit/name."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from .quantities import QuantityError, format_quantity, parse_quantity

# Units we recognize by name. Anything else in the second token position is
# treated as the start of the ingredient name (so "2 large eggs" works fine
# without "large" needing to be in this table).
KNOWN_UNITS = {
    "tsp", "teaspoon", "teaspoons",
    "tbsp", "tablespoon", "tablespoons",
    "cup", "cups",
    "oz", "ounce", "ounces",
    "lb", "lbs", "pound", "pounds",
    "g", "gram", "grams",
    "kg", "kilogram", "kilograms",
    "ml", "milliliter", "milliliters", "millilitre", "millilitres",
    "l", "liter", "liters", "litre", "litres",
    "pinch", "pinches",
    "dash", "dashes",
    "clove", "cloves",
    "can", "cans",
    "stick", "sticks",
}


class IngredientError(ValueError):
    """Raised when an ingredient line can't be understood in strict mode."""


@dataclass
class Ingredient:
    quantity: Fraction
    unit: Optional[str]
    name: str
    raw: str

    def formatted_quantity(self) -> str:
        return format_quantity(self.quantity)

    def render(self) -> str:
        parts = [self.formatted_quantity()]
        if self.unit:
            parts.append(self.unit)
        parts.append(self.name)
        return " ".join(parts)


def parse_line(line: str, *, lenient: bool = False) -> Ingredient:
    """Parse a line like "1 1/2 cups flour" into an Ingredient.

    Strict mode requires an explicit leading quantity and a non-empty name.
    Lenient mode assumes a quantity of 1 when none is present, and leans on
    parse_quantity's lenient handling of ranges and noisy numbers.
    """
    raw = line.strip()
    if not raw:
        raise IngredientError("blank line")

    tokens = raw.split()
    quantity: Optional[Fraction] = None
    consumed = 0

    # Try a two-token mixed number first ("1 1/2 cups flour").
    if len(tokens) >= 2:
        try:
            quantity = parse_quantity(f"{tokens[0]} {tokens[1]}", lenient=lenient)
            consumed = 2
        except QuantityError:
            quantity = None

    if quantity is None:
        try:
            quantity = parse_quantity(tokens[0], lenient=lenient)
            consumed = 1
        except QuantityError:
            if not lenient:
                raise IngredientError(
                    f"no leading quantity in {raw!r} (use --lenient to assume 1)"
                ) from None
            quantity = Fraction(1)
            consumed = 0

    rest = tokens[consumed:]
    unit = None
    if rest:
        candidate = rest[0].lower().rstrip(".,")
        if candidate in KNOWN_UNITS:
            unit = candidate
            rest = rest[1:]

    name = " ".join(rest).strip()
    if not name:
        if lenient:
            name = raw
        else:
            raise IngredientError(f"no ingredient name in {raw!r}")

    return Ingredient(quantity, unit, name, raw)
