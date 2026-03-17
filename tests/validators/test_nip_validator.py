import pytest
from app.core.validators import validate_nip


@pytest.mark.validators
def test_validate_nip():
    """
    Test for nip validator
    """

    result = validate_nip("5272184991")
    assert result == "5272184991"


@pytest.mark.validators
def test_validate_nip_wrong_length():
    """
    Test for nip validator.
    ValueError trigger.
    """

    with pytest.raises(ValueError) as error:
        validate_nip("12345678")

    assert "NIP must be 10 digits" in str(error.value)


@pytest.mark.validators
def test_validate_nip_ValueError():
    """
    Test for nip validator.
    ValueError trigger.
    """

    with pytest.raises(ValueError) as error:
        validate_nip("1234567899")

    assert "Entered NIP is not valid number" in str(error.value)
    
