import pytest
from app.core.validators import validate_regon


@pytest.mark.validators
def test_validate_regon():
    """
    Test for regon validator
    """

    result = validate_regon("146108856")
    assert result == "146108856"


@pytest.mark.validators
def test_validate_regon_wrong_length():
    """
    Test for regon validator.
    Length != 9
    """

    with pytest.raises(ValueError) as error:
        validate_regon("14610885116")

    assert "REGON must be 9 digits" in str(error.value)


@pytest.mark.validators
def test_validate_regon_invalid():
    """
    Test for regon validator.
    Invalid number
    """

    with pytest.raises(ValueError) as error:
        validate_regon("123456789")

    assert "REGON is not valid" in str(error.value)
