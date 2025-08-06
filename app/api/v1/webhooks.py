from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.domain.models import Tenant
from app.schemas.webhook import WebhookDeliveryOut, WebhookEventCreate
from app.services.webhooks import create_webhook_event, deliver_webhook

router = APIRouter()


@router.post("/webhooks/payment", response_model=WebhookDeliveryOut, status_code=status.HTTP_202_ACCEPTED)
def handle_payment_webhook(payload: WebhookEventCreate, db: Session = Depends(get_db)):
    tenant: Tenant | None = db.get(Tenant, payload.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    delivery = create_webhook_event(db, tenant_id=payload.tenant_id, event_type=payload.type, payload=payload.payload)
    if tenant.webhook_url:
        delivery = deliver_webhook(db, str(delivery.id), tenant.webhook_url)
    db.commit()
    return WebhookDeliveryOut.model_validate(delivery)
