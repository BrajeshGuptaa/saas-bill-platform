from datetime import datetime

from pydantic import BaseModel

from app.domain.models import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    plan_id: str
    quantity: int = 1
    trial_days: int | None = None


class SubscriptionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    plan_id: str
    status: SubscriptionStatus
    quantity: int
    current_period_start: datetime
    current_period_end: datetime
    trial_end: datetime | None = None
    
    
