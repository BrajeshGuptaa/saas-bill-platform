from pydantic import BaseModel


class MRRResponse(BaseModel):
    tenant_id: str
    monthly_recurring_revenue: float
    annual_run_rate: float
