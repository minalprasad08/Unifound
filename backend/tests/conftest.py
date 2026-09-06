import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token
from app.core.rate_limiter import (
    rate_limit_login,
    rate_limit_register,
    rate_limit_agent,
    rate_limit_upload,
    rate_limit_claim,
)

# Use an in-memory SQLite database with StaticPool for fast, isolated test runs
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset rate limiter state before each test to guarantee complete test isolation."""
    rate_limit_login.reset()
    rate_limit_register.reset()
    rate_limit_agent.reset()
    rate_limit_upload.reset()
    rate_limit_claim.reset()
    yield


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        email="student@campus.edu",
        hashed_password=get_password_hash("Password123!"),
        full_name="Alex Student",
        phone="+1 555-0100",
        department="Computer Science",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session: Session) -> User:
    admin = User(
        email="admin@campus.edu",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Sarah Administrator",
        phone="+1 555-0200",
        department="Campus Security",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user: User) -> str:
    return create_access_token(subject=test_user.id, role=test_user.role.value)


@pytest.fixture
def admin_token(test_admin: User) -> str:
    return create_access_token(subject=test_admin.id, role=test_admin.role.value)


@pytest.fixture
def user_headers(user_token: str) -> dict:
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}
