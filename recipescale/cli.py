"""A thin command-line wrapper around the recipescale library."""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from typing import List, Optional

from .ingredient import IngredientError, convert_unit, parse_line
from .quantities import QuantityError
from .scaling import scale_factor, scale_ingredients
from .units import UnitError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recipescale",
        description="Scale a plain-text ingredient list up or down.",
    )
    parser.add_argument(
        "recipe",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="path to an ingredient list, one item per line (default: stdin)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--factor",
        type=str,
        help="multiply every quantity by this number, e.g. 1.5 or 3/2",
    )
    group.add_argument(
        "--servings",
        type=str,
        metavar="FROM:TO",
        help="scale from one serving count to another, e.g. 4:6",
    )
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="tolerate messy input (ranges, missing quantities, odd units) "
        "instead of failing on the first line that doesn't parse",
    )
    parser.add_argument(
        "--to-unit",
        type=str,
        metavar="UNIT",
        help="convert ingredients measured in the same category to this "
        "unit after scaling: volume (tsp/tbsp/cup/ml/l) or weight "
        "(g/oz/lb/kg); ingredients in other units are left as-is",
    )
    return parser


def _resolve_factor(args: argparse.Namespace) -> Fraction:
    if args.factor is not None:
        try:
            return Fraction(args.factor)
        except (ValueError, ZeroDivisionError) as exc:
            raise SystemExit(f"invalid --factor {args.factor!r}: {exc}")

    from_str, sep, to_str = args.servings.partition(":")
    if not sep:
        raise SystemExit(f"invalid --servings {args.servings!r}, expected FROM:TO")
    try:
        from_servings = float(from_str)
        to_servings = float(to_str)
    except ValueError:
        raise SystemExit(f"invalid --servings {args.servings!r}, expected FROM:TO")
    return scale_factor(from_servings=from_servings, to_servings=to_servings)


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    factor = _resolve_factor(args)

    lines = [line for line in args.recipe.read().splitlines() if line.strip()]
    if args.recipe is not sys.stdin:
        args.recipe.close()

    ingredients = []
    for line in lines:
        try:
            ingredients.append(parse_line(line, lenient=args.lenient))
        except (IngredientError, QuantityError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            if not args.lenient:
                print(
                    "(pass --lenient to skip lines like this instead of failing)",
                    file=sys.stderr,
                )
                return 1
            continue

    scaled = scale_ingredients(ingredients, factor)
    if args.to_unit:
        try:
            scaled = [convert_unit(ing, args.to_unit) for ing in scaled]
        except UnitError as exc:
            raise SystemExit(f"invalid --to-unit: {exc}")

    for ing in scaled:
        print(ing.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
