from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.domain.models import Plan, Subscription, SubscriptionStatus


DEFAULT_PERIOD_DAYS = 30


def period_end(start: datetime, days: int = DEFAULT_PERIOD_DAYS) -> datetime:
    return start + timedelta(days=days)


def create_subscription(
    db: Session, tenant_id: str, plan_id: str, quantity: int, trial_days: int | None = None
) -> Subscription:
    now = datetime.now(timezone.utc)
    plan: Plan | None = db.query(Plan).filter(Plan.id == plan_id, Plan.tenant_id == tenant_id).first()
    if plan is None:
        raise ValueError("Plan not found for tenant")
    current_end = period_end(now)
    status = SubscriptionStatus.trialing if trial_days else SubscriptionStatus.active
    trial_end = now + timedelta(days=trial_days) if trial_days else None
    subscription = Subscription(
        tenant_id=tenant_id,
        plan_id=plan_id,
        status=status,
        quantity=quantity,
        current_period_start=now,
        current_period_end=current_end,
        trial_end=trial_end,
        needs_proration=False,
    )
    db.add(subscription)
    db.flush()
    return subscription


def mark_proration_required(db: Session, subscription: Subscription) -> None:
    subscription.needs_proration = True
    db.add(subscription)
