from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.domain.models import TenantRevenueMV
from app.schemas.metrics import MRRResponse
from app.services.invoices import _refresh_revenue_mv

router = APIRouter()


@router.get("/tenants/{tenant_id}/metrics/mrr", response_model=MRRResponse)
def get_mrr(
    tenant_id: str = Path(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if str(user.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    mv = db.query(TenantRevenueMV).filter(TenantRevenueMV.tenant_id == tenant_id).first()
    if mv is None:
        _refresh_revenue_mv(db, tenant_id)
        mv = db.query(TenantRevenueMV).filter(TenantRevenueMV.tenant_id == tenant_id).first()
    db.commit()
    return MRRResponse(
        tenant_id=str(mv.tenant_id),
        monthly_recurring_revenue=float(mv.monthly_recurring_revenue),
        annual_run_rate=float(mv.annual_run_rate),
    )
