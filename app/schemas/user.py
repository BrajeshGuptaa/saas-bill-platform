from pydantic import BaseModel, EmailStr

from app.domain.models import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.read_only


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: EmailStr
    role: Role
