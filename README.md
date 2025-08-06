# Usage-Based Billing Service

FastAPI service that supports multi-tenant subscriptions, usage ingestion, invoice generation, webhooks, and revenue metrics. The stack follows the provided build order: tenants/auth → plans/pricing → subscriptions → usage → invoices/worker → webhooks → metrics → observability → docker/CI.

## Quickstart

```bash
python3 -m poetry install
cp .env.example .env
python3 -m poetry run uvicorn app.main:app --reload
```

Run tests/lint:

```bash
python3 -m poetry run pytest
python3 -m poetry run ruff check .
```

Docker:

```bash
docker compose up --build
```

## Key Endpoints (all under `/v1`)

- `POST /tenants` – create tenant + admin token bootstrap.
- `POST /tenants/{tenant_id}/users` – add users (admin-only).
- `POST /auth/login` – JWT login.
- `POST /tenants/{tenant_id}/plans` – create plans (flat, tiered, volume).
- `POST /tenants/{tenant_id}/subscriptions` – create subscriptions with optional trial.
- `POST /tenants/{tenant_id}/usage` – idempotent usage ingestion (`Idempotency-Key` header).
- `POST /tenants/{tenant_id}/invoices/run` – generate invoices for active subs.
- `POST /webhooks/payment` – record/deliver payment webhooks.
- `GET /tenants/{tenant_id}/metrics/mrr` – tenant MRR/ARR materialized view.
- `GET /healthz`, `/readyz`, `/metrics` – health and Prometheus metrics.

## Design Notes

- Multi-tenant enforced by `tenant_id` on all tables/queries; auth payload carries tenant_id.
- Pricing engine implements `calculate_flat`, `calculate_tiered`, `calculate_volume`.
- Usage ingestion combines Redis `SETNX` TTL + DB unique constraint on `idempotency_key`.
- Invoice worker (RQ job) rolls active subscriptions forward, summarizes usage, updates revenue MV.
- Webhook delivery retries with exponential backoff and DLQ status tracking.
- Observability: Prometheus counters for usage, invoice duration, webhook retries; structured logs carry `tenant_id` and `request_id`.

## Migrations

Alembic is configured (`alembic.ini`, `migrations/`). To apply:

```bash
python3 -m poetry run alembic upgrade head
```

## CI

GitHub Actions workflow runs lint, mypy, and tests. Compose-friendly services (db, redis, app, worker, mock payment) are defined in `docker-compose.yml`.
