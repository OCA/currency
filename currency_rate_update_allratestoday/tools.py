# Copyright 2026 AllRatesToday (https://allratestoday.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Pure helpers (no Odoo import) for the AllRatesToday table shape.

A table is a list of rows ``{"base": "EUR", "quote": "USD", "type":
"reference", "value": 1.17}`` where ``value`` is always *quote units per 1
base unit*. Publishers differ in which side their home currency sits on
(the ECB prints foreign per 1 EUR, the RBI prints INR per 1 foreign unit),
so the table is first normalised to units per 1 pivot (home) currency and
then rebased to the company currency.
"""

from collections import Counter

# Rate-type labels the feed emits, most general first. Breaks ties when a
# bank prints several series (buy/sell/middle) for the same pair.
RATE_TYPE_PREFERENCE = (
    "reference",
    "middle",
    "indicative",
    "monthly",
    "monthly_average",
    "quarterly",
    "close",
    "informational",
    "buy",
    "sell",
)


def pick_pivot(rows, preferred=()):
    """Currency code shared by the most rows: the publisher's home currency."""
    counts = Counter()
    for row in rows:
        counts[row["base"]] += 1
        counts[row["quote"]] += 1
    if not counts:
        return None
    preferred = set(preferred)
    return min(counts, key=lambda c: (-counts[c], c not in preferred, c))


def _type_rank(rate_type):
    try:
        return RATE_TYPE_PREFERENCE.index(rate_type)
    except ValueError:
        return len(RATE_TYPE_PREFERENCE)


def per_pivot(rows, rate_type=None, preferred_pivots=()):
    """``{code: units of code per 1 pivot}`` with the pivot itself at 1.0."""
    pivot = pick_pivot(rows, preferred_pivots)
    if pivot is None:
        return {}
    best = {}
    for row in rows:
        row_type = row.get("type")
        if rate_type and row_type != rate_type:
            continue
        value = row.get("value")
        if not isinstance(value, int | float) or value <= 0:
            continue
        if row["base"] == pivot:
            other, rate = row["quote"], float(value)
        elif row["quote"] == pivot:
            other, rate = row["base"], 1.0 / float(value)
        else:
            continue
        if other == pivot:
            continue
        rank = _type_rank(row_type)
        if other not in best or rank < best[other][0]:
            best[other] = (rank, rate)
    result = {code: rate for code, (_rank, rate) in best.items()}
    result[pivot] = 1.0
    return result


def rebase(per_pivot_rates, base_currency, currencies):
    """``{code: units of code per 1 base_currency}`` for the requested codes.

    Raises ``KeyError`` when the base currency is not in the table.
    """
    base_rate = per_pivot_rates[base_currency]
    return {
        code: rate / base_rate
        for code, rate in per_pivot_rates.items()
        if code in currencies and code != base_currency
    }
