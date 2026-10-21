from pydantic import Field

import pydantic

from volsegtools._core import AxisValues, DataKind, UnitKind


class DataSetInfo(pydantic.BaseModel):
    """Metadata related to the data set.

    Attributes
    ----------
    filename
        File name of the input data.
    axis_order
        Axis order of the data held by the dataset.
    origin
        Origin of the coordinate system of the dataset.
    id
        Name of the dataset.
    kind
        Kind of the data held by the dataset.
    unit
        Unit of the dataset.
    """

    filename: str = "Unknown File"
    axis_order: AxisValues = Field(default_factory=AxisValues)
    origin: AxisValues = Field(default_factory=AxisValues)
    id: str = "Unknown"
    kind: DataKind = DataKind.VOLUME
    unit: UnitKind = UnitKind.UNKNOWN


class ResolutionInfo(pydantic.BaseModel):
    id: int = -1
    cell_size: AxisValues
    lattice_shape: AxisValues


class TimeFrameInfo(pydantic.BaseModel):
    """Metadata related to a single time frame.

    Attributes
    ----------
    id
        Unique identifier of the time frame in its parent dataset.
    """

    id: int = -1


@pydantic.dataclasses.dataclass
class DescriptiveStatistics:
    """Statistics about the data that might be required for serialization.

    Attributes
    ----------
    mean
        Mean of the whole channel (one layer of data).
    std
        Standard deviation of the whole channel.
    min
        Minimum value in the channel.
    max
        Maximum value in the channel.
    """

    mean: float = 0.0
    std: float = 0.0
    max: float = 0.0
    min: float = 0.0


class ChannelInfo(pydantic.BaseModel):
    """Metadata related to a single data channel.

    Attributes
    ----------
    id
        Unique identifier in its parent time frame.
    statistics
        Statistics related to this channel.
    """

    id: int = -1
    statistics: DescriptiveStatistics = Field(default_factory=DescriptiveStatistics)


class MeshInfo(pydantic.BaseModel):
    """Metadata related to a mesh data.

    Attributes
    ----------
    id
        Unique identifier in its parent time frame.
    """

    id: int = -1
