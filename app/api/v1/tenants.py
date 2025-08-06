from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_tenant_admin
from app.domain.models import Role
from app.schemas.tenant import TenantBootstrapResponse, TenantCreate, TenantUserCreate
from app.schemas.user import UserOut
from app.services.auth import create_tenant_with_admin, create_user

router = APIRouter()


@router.post("/tenants", response_model=TenantBootstrapResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    tenant, admin, token = create_tenant_with_admin(
        db, name=payload.name, admin_email=payload.admin_email, admin_password=payload.admin_password, webhook_url=payload.webhook_url
    )
    db.commit()
    return {
        "tenant": {"id": str(tenant.id), "name": tenant.name, "webhook_url": tenant.webhook_url},
        "admin": {"id": str(admin.id), "email": admin.email, "role": admin.role},
        "token": token,
    }


@router.post("/tenants/{tenant_id}/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_tenant_user(
    payload: TenantUserCreate,
    tenant_id: str = Path(..., alias="tenant_id"),
    db: Session = Depends(get_db),
    admin=Depends(require_tenant_admin),
):
    if str(admin.tenant_id) != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    role = Role(payload.role) if isinstance(payload.role, str) else payload.role
    user = create_user(db, tenant_id=tenant_id, email=payload.email, password=payload.password, role=role)
    db.commit()
    return UserOut.model_validate(user)
