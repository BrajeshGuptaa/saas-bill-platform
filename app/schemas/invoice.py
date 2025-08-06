from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.domain.models import InvoiceStatus


class InvoiceItemOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    description: str
    quantity: int
    unit_amount: float
    amount: float


class InvoiceOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    total: float
    currency: str
    period_start: datetime
    period_end: datetime
    status: InvoiceStatus
    items: List[InvoiceItemOut] = []
