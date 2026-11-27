import pytest

import volsegtools as vst


class TestKind(vst.MultiValueStrEnum):
    FIRST = "first", "1.", "1st"
    SECOND = "second", "2.", "2nd"


@pytest.mark.parametrize(
    "value, kind",
    [
        ("first", TestKind.FIRST),
        ("1.", TestKind.FIRST),
        ("1st", TestKind.FIRST),
        ("second", TestKind.SECOND),
        ("2.", TestKind.SECOND),
        ("2nd", TestKind.SECOND),
    ],
)
def test_valid_values_for_multi_enum(value, kind):
    assert TestKind(value) == kind


@pytest.mark.parametrize("wrong_value", [None, "random", 42])
def test_invalid_values_for_multi_enum(wrong_value):
    with pytest.raises(ValueError):
        TestKind(wrong_value)
