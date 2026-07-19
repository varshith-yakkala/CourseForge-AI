import pytest
from httpx import AsyncClient
from db.models.user import User
from core.security import verify_password


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session):
    """Test user registration."""
    db_session.execute.return_value.scalar_one_or_none.return_value = None
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_existing_user(client: AsyncClient, db_session, test_user):
    """Test registering an email that already exists."""
    db_session.execute.return_value.scalar_one_or_none.return_value = test_user
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "securepassword123",
            "full_name": "Another User"
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "A user with this email already exists."


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, db_session, test_user):
    """Test login with correct credentials."""
    db_session.execute.return_value.scalar_one_or_none.return_value = test_user
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session, test_user):
    """Test login with incorrect password."""
    db_session.execute.return_value.scalar_one_or_none.return_value = test_user
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
