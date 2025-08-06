from datetime import timedelta
from decimal import Decimal
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models import (
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    PricingModel,
    Subscription,
    SubscriptionStatus,
    TenantRevenueMV,
    UsageEvent,
)
from app.services.pricing import calculate_flat, calculate_tiered, calculate_volume
from app.api.v1.health import invoice_generation_duration


def _invoice_amount(plan, subscription: Subscription, usage_quantity: Decimal) -> Decimal:
    if plan.pricing_model == PricingModel.flat:
        return calculate_flat(plan.price, subscription.quantity)
    if plan.pricing_model == PricingModel.tiered:
        return calculate_tiered(plan.tiers or [], usage_quantity)
    return calculate_volume(plan.tiers or [], usage_quantity)


def generate_invoice_for_subscription(db: Session, subscription: Subscription) -> Invoice:
    plan = subscription.plan
    usage_quantity = db.query(func.coalesce(func.sum(UsageEvent.quantity), 0)).filter(
        UsageEvent.subscription_id == subscription.id,
        UsageEvent.ts >= subscription.current_period_start,
        UsageEvent.ts < subscription.current_period_end,
    ).scalar()
    usage_quantity = Decimal(str(usage_quantity or 0))
    amount = _invoice_amount(plan, subscription, usage_quantity)

    invoice = Invoice(
        tenant_id=subscription.tenant_id,
        subscription_id=subscription.id,
        currency=plan.currency,
        period_start=subscription.current_period_start,
        period_end=subscription.current_period_end,
        total=amount,
        status=InvoiceStatus.sent,
    )
    item_description = f"{plan.name} ({plan.pricing_model})"
    item = InvoiceItem(
        description=item_description,
        quantity=int(subscription.quantity),
        unit_amount=plan.price,
        amount=amount,
    )
    invoice.items.append(item)
    db.add(invoice)
    db.flush()
    # Move subscription forward
    subscription.current_period_start = subscription.current_period_end
    subscription.current_period_end = subscription.current_period_end + timedelta(days=30)
    subscription.needs_proration = False
    db.add(subscription)
    _refresh_revenue_mv(db, subscription.tenant_id)
    return invoice


def run_invoicing(db: Session, tenant_id: str) -> List[Invoice]:
    with invoice_generation_duration.time():
        active_subs = (
            db.query(Subscription)
            .filter(Subscription.tenant_id == tenant_id)
            .filter(Subscription.status == SubscriptionStatus.active)
            .all()
        )
        invoices: List[Invoice] = []
        for sub in active_subs:
            invoices.append(generate_invoice_for_subscription(db, sub))
        return invoices


def _refresh_revenue_mv(db: Session, tenant_id: str) -> None:
    total_mrr = (
        db.query(func.coalesce(func.sum(Invoice.total), 0))
        .filter(Invoice.tenant_id == tenant_id, Invoice.status.in_([InvoiceStatus.sent, InvoiceStatus.paid]))
        .scalar()
    )
    annual = Decimal(str(total_mrr)) * Decimal("12")
    mv = db.query(TenantRevenueMV).filter(TenantRevenueMV.tenant_id == tenant_id).first()
    if mv is None:
        mv = TenantRevenueMV(
            tenant_id=tenant_id,
            monthly_recurring_revenue=total_mrr,
            annual_run_rate=annual,
        )
    else:
        mv.monthly_recurring_revenue = total_mrr
        mv.annual_run_rate = annual
    db.add(mv)
    db.flush()
