import uuid
from datetime import datetime, timezone

from app.domain.models import PricingModel, Subscription, Tenant, Plan, Product
from app.services.usage import ingest_usage_event


def test_usage_idempotency_single_row(db_session):
    tenant = Tenant(id=uuid.uuid4(), name="T1")
    now = datetime.now(timezone.utc)
    product = Product(id=uuid.uuid4(), tenant_id=tenant.id, name="API", created_at=now)
    plan = Plan(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        product_id=product.id,
        name="Pro",
        pricing_model=PricingModel.flat,
        currency="USD",
        price=10,
        created_at=now,
    )
    subscription = Subscription(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        plan_id=plan.id,
        quantity=1,
        current_period_start=now,
        current_period_end=now,
    )
    db_session.add_all([tenant, product, plan, subscription])
    db_session.commit()

    key = "abc-123"
    event, duplicate = ingest_usage_event(
        db_session,
        tenant_id=str(tenant.id),
        subscription_id=str(subscription.id),
        metric="api_calls",
        quantity=5,
        ts=None,
        idempotency_key=key,
        redis_client=None,
    )
    db_session.commit()
    assert event is not None
    assert duplicate is False

    event2, duplicate2 = ingest_usage_event(
        db_session,
        tenant_id=str(tenant.id),
        subscription_id=str(subscription.id),
        metric="api_calls",
        quantity=5,
        ts=None,
        idempotency_key=key,
        redis_client=None,
    )
    db_session.commit()
    assert duplicate2 is True
    assert db_session.query(type(event)).count() == 1
