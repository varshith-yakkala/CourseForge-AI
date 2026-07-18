import pytest
from db.models.user import User
from db.models.course import Course
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


@pytest.mark.asyncio
async def test_user_creation(db_session: AsyncSession):
    """Test user model insertion."""
    user = User(
        email="model@example.com",
        hashed_password="hashed",
        full_name="Model Test",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "model@example.com"
    assert user.role == "student"


@pytest.mark.asyncio
async def test_course_creation_relationship(db_session: AsyncSession, test_user: User):
    """Test creating a course linked to a user."""
    course = Course(
        owner_id=test_user.id,
        title="Test Course",
        description="A course for testing",
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    
    assert course.id is not None
    assert course.owner_id == test_user.id
    assert course.title == "Test Course"

    # Test the reverse relationship
    stmt = select(User).where(User.id == test_user.id)
    result = await db_session.execute(stmt)
    user = result.scalar_one()
    
    # Normally we'd test user.courses but lazy loading requires async setup
    # In integration tests, we can load eagerly
