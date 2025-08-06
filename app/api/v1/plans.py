from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_tenant_admin
from app.schemas.plan import PlanCreate, PlanOut
from app.services.plans import create_plan

router = APIRouter()


@router.post("/tenants/{tenant_id}/plans", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
def create_plan_endpoint(
    payload: PlanCreate,
    tenant_id: str = Path(...),
    db: Session = Depends(get_db),
    admin=Depends(require_tenant_admin),
):
    if str(admin.tenant_id) != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan name is required")
    product_name = (payload.product_name or "").strip() if payload.product_name else None
    if payload.pricing_model in {"tiered", "volume"} and not payload.tiers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tiers are required for tiered/volume pricing")
    try:
        plan = create_plan(
            db=db,
            tenant_id=tenant_id,
            name=name,
            pricing_model=payload.pricing_model,
            currency=payload.currency,
            price=payload.price,
            tiers=[tier.model_dump() for tier in payload.tiers] if payload.tiers else None,
            product_id=payload.product_id,
            product_name=product_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    return {
        "id": str(plan.id),
        "name": plan.name,
        "pricing_model": plan.pricing_model,
        "currency": plan.currency,
        "price": float(plan.price),
        "tiers": plan.tiers,
    }
