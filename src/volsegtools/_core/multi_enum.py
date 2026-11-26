"""
We have to support Python 3.12 due to the VRML. In that version there is no
official class for multi-value enums. So we have to roll our own, simple
version.
"""

import enum


class MultiValueStrEnum(enum.StrEnum):
    """Represents multiple string values via a single label."""

    def __new__(cls, value, *aliases):
        self = str.__new__(cls, value)
        self._value_ = value
        self._aliases_ = aliases
        return self

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if value in member._aliases_:
                return member
        return None
