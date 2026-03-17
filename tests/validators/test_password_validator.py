import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate


@pytest.mark.validators
def test_password_no_lowercase():
    with pytest.raises(ValidationError) as error:
        UserCreate(email="test@test.com", password="TESTING.123!")

    assert "Password must contain at least one lowercase letter" in str(error.value)


@pytest.mark.validators
def test_password_no_uppercase():
    with pytest.raises(ValidationError) as error:
        UserCreate(email="test@test.com", password="testing.123!")

    assert "Password must contain at least one uppercase letter" in str(error.value)


@pytest.mark.validators
def test_password_no_digit():
    with pytest.raises(ValidationError) as error:
        UserCreate(email="test@test.com", password="Testing!")

    assert "Password must contain at least one digit" in str(error.value)


@pytest.mark.validators
def test_password_no_special():
    with pytest.raises(ValidationError) as error:
        UserCreate(email="test@test.com", password="Testing123")

    assert "Password must contain at least one special character" in str(error.value)