from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional


def _to_decimal(value) -> Decimal:
    return Decimal(str(value))


def _round_currency(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_flat(price: float | Decimal, quantity: int | float) -> Decimal:
    total = _to_decimal(price) * _to_decimal(quantity)
    return _round_currency(total)


def calculate_tiered(tiers: List[dict], quantity: int | float) -> Decimal:
    remaining = _to_decimal(quantity)
    total = Decimal("0")
    previous_cap: Optional[Decimal] = Decimal("0")
    for tier in sorted(tiers, key=lambda t: t.get("up_to") or float("inf")):
        cap = _to_decimal(tier.get("up_to") or remaining + previous_cap)
        tier_units = min(remaining, cap - previous_cap)
        if tier_units <= 0:
            previous_cap = cap
            continue
        total += tier_units * _to_decimal(tier["unit_amount"])
        remaining -= tier_units
        previous_cap = cap
        if remaining <= 0:
            break
    return _round_currency(total)


def calculate_volume(tiers: List[dict], quantity: int | float) -> Decimal:
    applicable = None
    qty = _to_decimal(quantity)
    for tier in sorted(tiers, key=lambda t: t.get("up_to") or float("inf")):
        cap = tier.get("up_to")
        if cap is None or qty <= _to_decimal(cap):
            applicable = tier
            break
    if applicable is None:
        applicable = tiers[-1]
    total = qty * _to_decimal(applicable["unit_amount"])
    return _round_currency(total)
