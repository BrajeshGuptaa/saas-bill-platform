from pydantic import BaseModel, EmailStr

from app.schemas.user import UserOut


class TenantCreate(BaseModel):
    name: str
    admin_email: EmailStr
    admin_password: str
    webhook_url: str | None = None


class TenantOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    webhook_url: str | None = None


class TenantUserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "read_only"


class TenantWithAdmin(BaseModel):
    tenant: TenantOut
    admin: UserOut


class TenantBootstrapResponse(BaseModel):
    tenant: TenantOut
    admin: UserOut
    token: str
