"""Turning a scale factor or a servings change into scaled ingredients."""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, List

from .ingredient import Ingredient


def scale_factor(*, from_servings: float, to_servings: float) -> Fraction:
    """Compute the multiplier that turns `from_servings` into `to_servings`."""
    if from_servings <= 0 or to_servings <= 0:
        raise ValueError("servings must be positive")
    from_frac = Fraction(from_servings).limit_denominator(1000)
    to_frac = Fraction(to_servings).limit_denominator(1000)
    return to_frac / from_frac


def scale_ingredients(ingredients: Iterable[Ingredient], factor: Fraction) -> List[Ingredient]:
    if factor <= 0:
        raise ValueError("scale factor must be positive")
    return [
        Ingredient(ing.quantity * factor, ing.unit, ing.name, ing.raw)
        for ing in ingredients
    ]
