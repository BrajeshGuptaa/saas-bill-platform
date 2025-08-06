from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.models import Plan, PricingModel, Product


def get_or_create_product(db: Session, tenant_id: str, name: str, description: str | None = None) -> Product:
    product = (
        db.query(Product)
        .filter(Product.tenant_id == tenant_id)
        .filter(Product.name == name)
        .first()
    )
    if product:
        return product
    product = Product(tenant_id=tenant_id, name=name, description=description)
    db.add(product)
    db.flush()
    return product


def create_plan(
    db: Session,
    tenant_id: str,
    name: str,
    pricing_model: PricingModel,
    currency: str,
    price: float,
    tiers: list[dict] | None,
    product_id: str | None = None,
    product_name: str | None = None,
) -> Plan:
    if product_id:
        product = (
            db.query(Product)
            .filter(Product.id == product_id, Product.tenant_id == tenant_id)
            .first()
        )
    elif product_name:
        product = get_or_create_product(db, tenant_id=tenant_id, name=product_name)
    else:
        raise ValueError("product_id or product_name required")

    if product is None:
        raise ValueError("Product not found for tenant")

    plan = Plan(
        tenant_id=tenant_id,
        product_id=product.id,
        name=name,
        pricing_model=pricing_model,
        currency=currency,
        price=price,
        tiers=[dict(t) for t in tiers] if tiers else None,
    )
    db.add(plan)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ValueError("Plan name already exists for this tenant")
    return plan
