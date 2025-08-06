from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import LoginRequest, Token
from app.services.auth import authenticate_user

router = APIRouter()


@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = authenticate_user(db, payload.tenant_id, payload.email, payload.password)
    db.commit()
    return Token(access_token=token)
