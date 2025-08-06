from datetime import datetime

from pydantic import BaseModel


class UsageEventCreate(BaseModel):
    subscription_id: str
    metric: str
    quantity: float
    ts: datetime | None = None


class UsageEventOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    subscription_id: str
    metric: str
    quantity: float
    ts: datetime
    idempotency_key: str
