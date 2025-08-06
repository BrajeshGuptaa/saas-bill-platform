from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.api.v1.health import webhook_retry_counter
from app.domain.models import WebhookDelivery, WebhookDeliveryStatus, WebhookEvent

MAX_ATTEMPTS = 5
BASE_DELAY_SECONDS = 5


def create_webhook_event(db: Session, tenant_id: str, event_type: str, payload: dict) -> WebhookDelivery:
    event = WebhookEvent(tenant_id=tenant_id, type=event_type, payload=payload)
    db.add(event)
    db.flush()
    delivery = WebhookDelivery(event_id=event.id)
    db.add(delivery)
    db.flush()
    return delivery


def deliver_webhook(db: Session, delivery_id: str, webhook_url: str) -> WebhookDelivery:
    delivery: WebhookDelivery | None = db.get(WebhookDelivery, delivery_id)
    if delivery is None:
        return None
    delivery.attempts += 1
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(webhook_url, json=delivery.event.payload)
            resp.raise_for_status()
        delivery.status = WebhookDeliveryStatus.delivered
        delivery.next_attempt_at = None
        delivery.last_error = None
    except Exception as exc:  # noqa: BLE001
        if delivery.attempts >= MAX_ATTEMPTS:
            delivery.status = WebhookDeliveryStatus.dead_lettered
        else:
            delivery.status = WebhookDeliveryStatus.failed
            delay = BASE_DELAY_SECONDS * (2** (delivery.attempts - 1))
            delivery.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
            webhook_retry_counter.inc()
        delivery.last_error = str(exc)
    db.add(delivery)
    db.flush()
    return delivery
