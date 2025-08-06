from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.health import usage_events_counter
from app.dependencies import get_current_user, get_db, get_redis_client
from app.schemas.usage import UsageEventCreate, UsageEventOut
from app.services.usage import ingest_usage_event

router = APIRouter()


@router.post("/tenants/{tenant_id}/usage", response_model=dict, status_code=status.HTTP_201_CREATED)
def ingest_usage(
    payload: UsageEventCreate,
    tenant_id: str = Path(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    redis_client=Depends(get_redis_client),
):
    if str(user.tenant_id) != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    event, duplicate = ingest_usage_event(
        db=db,
        tenant_id=tenant_id,
        subscription_id=payload.subscription_id,
        metric=payload.metric,
        quantity=payload.quantity,
        ts=payload.ts,
        idempotency_key=idempotency_key or "",
        redis_client=redis_client,
    )
    db.commit()
    if duplicate:
        return JSONResponse(content={"duplicate": True}, status_code=status.HTTP_200_OK)
    usage_events_counter.inc()
    return {
        "id": str(event.id),
        "subscription_id": str(event.subscription_id),
        "metric": event.metric,
        "quantity": float(event.quantity),
        "ts": event.ts,
        "idempotency_key": event.idempotency_key,
    }
