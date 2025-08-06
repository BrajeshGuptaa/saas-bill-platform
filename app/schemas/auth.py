from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    tenant_id: str = Field(..., examples=["tenant-uuid"])
    email: str
    password: str
