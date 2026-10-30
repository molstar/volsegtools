from pydantic import Field

import pydantic

from volsegtools._core import AxisValues, DataKind, UnitKind


class DataSetMetadata(pydantic.BaseModel):
    """Metadata related to the data set."""

    filename: str = "Unknown File"
    """
    File name of the input data.
    """
    axis_order: AxisValues = Field(default_factory=AxisValues)
    """
    Axis order of the data held by the dataset.
    """
    origin: AxisValues = Field(default_factory=AxisValues)
    """
    Origin of the coordinate system of the dataset.
    """
    id: str = "Unknown"
    """
    Name of the dataset.
    """
    kind: DataKind = DataKind.VOLUME
    """
    Kind of the data held by the dataset.
    """
    unit: UnitKind = UnitKind.UNKNOWN
    """
    Unit of the dataset.
    """


class ResolutionMetadata(pydantic.BaseModel):
    """Metadata related to a single resolution."""

    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    id: int = -1
    """
    Unique identifier of the resolution in its parent dataset.
    """
    cell_size: AxisValues = Field(default_factory=AxisValues)
    """
    Cell size of all data held by this resolution.
    """
    lattice_shape: AxisValues = Field(default_factory=AxisValues)
    """
    Shape of the data lattice held by this resolution. All time frames and
    channel have the same lattice dimensions.
    """


class TimeFrameMetadata(pydantic.BaseModel):
    """Metadata related to a single time frame."""

    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    id: int = -1
    """
    Unique identifier of the time frame in its parent resolution.
    """


class DescriptiveStatistics(pydantic.BaseModel):
    """Statistics about the data that might be required for serialization."""

    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    mean: float = 0.0
    """
    Mean of the whole channel (one layer of data).
    """
    std: float = 0.0
    """
    Standard deviation of the whole channel.
    """
    max: float = 0.0
    """
    Minimum value in the channel.
    """
    min: float = 0.0
    """
    Maximum value in the channel.
    """

    # We need this as a workaround so that we can use init function as we are
    # accustomed from dataclasses, but we retain the semantics of a base model.
    def __init__(
        self, mean: float = 0.0, std: float = 0.0, max: float = 0.0, min: float = 0.0
    ) -> None:
        super().__init__(mean=mean, std=std, max=max, min=min)


class ChannelMetadata(pydantic.BaseModel):
    """Metadata related to a single data channel."""

    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    id: int = -1
    """
    Unique identifier in its parent time frame.
    """
    statistics: DescriptiveStatistics = Field(default_factory=DescriptiveStatistics)
    """
    Statistics related to this channel.
    """


class MeshMetadata(pydantic.BaseModel):
    """Metadata related to a mesh data."""

    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    id: int = -1
    """
    Unique identifier in its parent time frame.
    """
