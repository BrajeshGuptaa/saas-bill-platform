from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.subscription import SubscriptionCreate, SubscriptionOut
from app.services.subscriptions import create_subscription

router = APIRouter()


@router.post("/tenants/{tenant_id}/subscriptions", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription_endpoint(
    payload: SubscriptionCreate,
    tenant_id: str = Path(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if str(user.tenant_id) != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    try:
        sub = create_subscription(
            db=db,
            tenant_id=tenant_id,
            plan_id=payload.plan_id,
            quantity=payload.quantity,
            trial_days=payload.trial_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    # Convert UUID/Decimal fields to plain JSON-friendly types
    return {
        "id": str(sub.id),
        "plan_id": str(sub.plan_id),
        "status": sub.status,
        "quantity": sub.quantity,
        "current_period_start": sub.current_period_start,
        "current_period_end": sub.current_period_end,
        "trial_end": sub.trial_end,
    }
