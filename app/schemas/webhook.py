from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel

from app.domain.models import WebhookDeliveryStatus


class WebhookEventCreate(BaseModel):
    tenant_id: str
    type: str
    payload: Dict[str, Any]


class WebhookDeliveryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    status: WebhookDeliveryStatus
    attempts: int
    next_attempt_at: datetime | None = None
    last_error: str | None = None
