import enum


class CompressionLevel(enum.StrEnum):
    """Denotes how aggresive should the serialization be.

    The higher the strenght the more lossly methods can be used by a
    serializer, if it is supporting variance in quality. Therefore, it is
    completely optional.

    Default value for serializers should generally be set to low.
    """

    LOSSLESS = enum.auto()
    """This level is not altering the data in any way."""
    LOW = enum.auto()
    MEDIUM = enum.auto()
    HIGH = enum.auto()
    MAXIMUM = enum.auto()
    """This level is leading to drastic changes in data's type and/or precision."""
