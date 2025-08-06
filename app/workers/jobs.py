from app.database import SessionLocal
from app.services.invoices import run_invoicing
from app.services.webhooks import deliver_webhook


def invoice_run_job(tenant_id: str) -> list[str]:
    """Background job to run invoices for a tenant."""
    with SessionLocal() as db:  # type: Session
        invoices = run_invoicing(db, tenant_id)
        db.commit()
        return [str(inv.id) for inv in invoices]


def webhook_delivery_job(delivery_id: str, webhook_url: str) -> str:
    with SessionLocal() as db:
        delivery = deliver_webhook(db, delivery_id, webhook_url)
        db.commit()
        return str(delivery.id) if delivery else ""
