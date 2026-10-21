from typing import Annotated

import enum

import pydantic

# It would be better to use StrEnum for this case, but we would need
# a multi-value enumeration for that. But that is better supported in 3.13+
# which we currently cannot support.


class UnitKind(enum.IntEnum):
    """Representation of the measurement unit of the data."""

    UNKNOWN = 0
    MICRO_METER = 1
    ANGSTROM = 2
    NANO_METER = 3


Unit = Annotated[
    UnitKind,
    pydantic.PlainSerializer(
        lambda v: v.name.lower(),
        return_type=str,
    ),
]


def unit_from_str(string: str) -> UnitKind:
    """Create a unit from a string.

    Parameters
    ----------
    string
        String representation of the unit name.

    Returns
    -------
    UnitKind
        Enum representation of the string.
    """
    match string:
        case "um" | "μm" | "micro":
            return UnitKind.MICRO_METER
        case "nm":
            return UnitKind.NANO_METER
        case "angstrom" | "Å":
            return UnitKind.ANGSTROM
        case _:
            return UnitKind.UNKNOWN


def to_angstrom(micrometers: float) -> float:
    """Turns micrometers into angstroms.

    Parameters
    ----------
    micrometers
        Number of micrometers.

    Returns
    -------
    float
        The same amount in angstroms.
    """
    return micrometers * 10_000


def to_micrometer(angstroms: float) -> float:
    """Turns angstroms into micrometers.

    Parameters
    ----------
    angstroms
        Number of angstroms.

    Returns
    -------
    float
        The same amount in micrometers.
    """
    return angstroms / 10_000
