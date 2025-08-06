from prometheus_client import Counter, Summary, generate_latest
from fastapi import APIRouter, Response

router = APIRouter()

usage_events_counter = Counter("usage_events_total", "Usage events ingested")
invoice_generation_duration = Summary("invoice_generation_duration_seconds", "Invoice generation duration")
webhook_retry_counter = Counter("webhook_retry_total", "Webhook delivery retries")


@router.get("/healthz")
def health():
    return {"status": "ok"}


@router.get("/readyz")
def ready():
    return {"ready": True}


@router.get("/metrics")
def metrics():
    content = generate_latest()
    return Response(content=content, media_type="text/plain")
