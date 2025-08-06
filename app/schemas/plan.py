from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.models import PricingModel


class PricingTier(BaseModel):
    up_to: int = Field(..., description="Inclusive quantity for the tier")
    unit_amount: float


class PlanCreate(BaseModel):
    name: str = Field(..., min_length=1)
    product_name: str | None = None
    product_id: str | None = None
    pricing_model: PricingModel
    currency: str = "USD"
    price: float = 0
    tiers: Optional[List[PricingTier]] = None


class PlanOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    pricing_model: PricingModel
    currency: str
    price: float
    tiers: Optional[list[dict]] = None
