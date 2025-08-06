from datetime import datetime, timezone
import uuid

from fastapi import HTTPException, status
from redis import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.domain.models import Subscription, UsageEvent

settings = get_settings()


def ingest_usage_event(
    db: Session,
    tenant_id: str,
    subscription_id: str,
    metric: str,
    quantity: float,
    ts: datetime | None,
    idempotency_key: str,
    redis_client: Redis | None = None,
) -> tuple[UsageEvent | None, bool]:
    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key required")

    tenant_uuid = uuid.UUID(str(tenant_id))
    subscription_uuid = uuid.UUID(str(subscription_id))

    subscription = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_uuid, Subscription.tenant_id == tenant_uuid)
        .first()
    )
    if subscription is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    redis_key = f"idemp:{idempotency_key}"
    if redis_client:
        try:
            inserted = redis_client.setnx(redis_key, "1")
            if not inserted:
                return None, True
        except Exception:
            redis_client = None

    event = UsageEvent(
        tenant_id=tenant_uuid,
        subscription_id=subscription_uuid,
        metric=metric,
        quantity=quantity,
        ts=ts or datetime.now(timezone.utc),
        idempotency_key=idempotency_key,
    )
    db.add(event)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return None, True

    if redis_client:
        try:
            redis_client.expire(redis_key, settings.idempotency_ttl_seconds)
        except Exception:
            pass
    return event, False
