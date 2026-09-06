# recipescale

A small library and CLI for scaling recipe ingredient lists up or down.

Doubling a recipe sounds trivial until the ingredient list has mixed
fractions, unicode vulgar fractions someone pasted from a food blog, units
spelled three different ways, and the occasional "a pinch of salt" with no
number in front of it at all. Naively multiplying strings or eyeballing
decimals gets these wrong in ways that are easy to miss until the dough
doesn't come together.

recipescale parses each ingredient line into a quantity (as an exact
`fractions.Fraction`, never a float), an optional unit, and a name, then
scales the quantity and renders it back as a clean mixed number.

By default it's strict: a line either parses cleanly or the whole run stops
with an error telling you which line and why. Real recipe text you copy from
somewhere is often messier than that (ranges like "2-3 cloves", a line with
no quantity, an unfamiliar unit), so there's a `--lenient` flag that relaxes
the parser instead of silently guessing by default.

## Install

Standard library only, no dependencies. Clone it and run it in place, or
install it locally:

```
pip install -e .
```

## Usage

Given `pasta.txt`:

```
1 1/2 cups flour
2 large eggs
1/2 tsp salt
¼ cup olive oil
```

Double it:

```
$ recipescale pasta.txt --factor 2
3 cups flour
4 large eggs
1 tsp salt
1/2 cup olive oil
```

Scale from 4 servings to 6:

```
$ recipescale pasta.txt --servings 4:6
2 1/4 cups flour
3 large eggs
3/4 tsp salt
3/8 cup olive oil
```

Messy input fails loudly by default:

```
$ recipescale messy.txt --factor 2
error: no leading quantity in 'a pinch of salt' (use --lenient to assume 1)
(pass --lenient to skip lines like this instead of failing)
```

Add `--lenient` to get a best-effort scale instead:

```
$ recipescale messy.txt --factor 2 --lenient
2 pinch of salt
```

## Library

```python
from recipescale import parse_line, scale_ingredients, scale_factor

ingredients = [parse_line(line) for line in open("pasta.txt")]
factor = scale_factor(from_servings=4, to_servings=6)
for ing in scale_ingredients(ingredients, factor):
    print(ing.render())
```

## Status

Early skeleton. Volume/weight unit conversion, a recipe file format with a
servings header, and a test suite are not built yet -- see the issues for
what's next.
