import uuid

import pytest
from fastapi import HTTPException

from app.domain.models import Role, Tenant
from app.services.auth import authenticate_user, create_user


def test_authentication_respects_tenant(db_session):
    tenant_a = Tenant(id=uuid.uuid4(), name="TenantA")
    tenant_b = Tenant(id=uuid.uuid4(), name="TenantB")
    db_session.add_all([tenant_a, tenant_b])
    db_session.flush()

    create_user(db_session, tenant_id=str(tenant_a.id), email="user@example.com", password="secret123", role=Role.admin)
    db_session.commit()

    with pytest.raises(HTTPException):
        authenticate_user(db_session, tenant_id=str(tenant_b.id), email="user@example.com", password="secret123")
