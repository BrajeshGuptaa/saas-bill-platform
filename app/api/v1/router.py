from fastapi import APIRouter

from app.api.v1 import auth, health, invoices, metrics, plans, subscriptions, tenants, usage, webhooks

api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(plans.router)
api_router.include_router(subscriptions.router)
api_router.include_router(usage.router)
api_router.include_router(invoices.router)
api_router.include_router(webhooks.router)
api_router.include_router(metrics.router)
