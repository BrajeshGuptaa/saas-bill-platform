import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.models import Role, Tenant, User
from app.security import create_access_token, get_password_hash, verify_password


def create_tenant_with_admin(
    db: Session, name: str, admin_email: str, admin_password: str, webhook_url: str | None = None
) -> tuple[Tenant, User, str]:
    # guard duplicate names early to avoid IntegrityError bubbling as 500
    existing = db.query(Tenant).filter(Tenant.name == name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant name already exists")
    tenant = Tenant(name=name, webhook_url=webhook_url)
    db.add(tenant)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant name already exists")

    admin_user = User(
        tenant_id=tenant.id,
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        role=Role.admin,
    )
    db.add(admin_user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin email already exists")
    token = create_access_token(str(admin_user.id), str(tenant.id))
    return tenant, admin_user, token


def create_user(db: Session, tenant_id: str, email: str, password: str, role: Role) -> User:
    tenant_uuid = uuid.UUID(str(tenant_id))
    user = User(
        tenant_id=tenant_uuid,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
    )
    db.add(user)
    db.flush()
    return user


def authenticate_user(db: Session, tenant_id: str, email: str, password: str) -> str:
    tenant_uuid = uuid.UUID(str(tenant_id))
    user: User | None = (
        db.query(User)
        .filter(User.tenant_id == tenant_uuid)
        .filter(User.email == email)
        .first()
    )
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    token = create_access_token(str(user.id), str(tenant_uuid))
    return token
