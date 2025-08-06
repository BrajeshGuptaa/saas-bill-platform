from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.invoice import InvoiceOut
from app.services.invoices import run_invoicing

router = APIRouter()


@router.post("/tenants/{tenant_id}/invoices/run", response_model=list[InvoiceOut])
def run_invoices_endpoint(
    tenant_id: str = Path(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if str(user.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")
    invoices = run_invoicing(db, tenant_id)
    db.commit()
    results: list[InvoiceOut] = []
    for inv in invoices:
        results.append(
            {
                "id": str(inv.id),
                "total": float(inv.total),
                "currency": inv.currency,
                "period_start": inv.period_start,
                "period_end": inv.period_end,
                "status": inv.status,
                "items": [
                    {
                        "id": str(item.id),
                        "description": item.description,
                        "quantity": item.quantity,
                        "unit_amount": float(item.unit_amount),
                        "amount": float(item.amount),
                    }
                    for item in inv.items
                ],
            }
        )
    return results
