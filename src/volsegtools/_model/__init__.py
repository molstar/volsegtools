"""
Contains classes, functions and models related to the data that are used
through this project.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .metadata import (
    ChannelMetadata,
    DataSetMetadata,
    DescriptiveStatistics,
    MeshMetadata,
    ResolutionMetadata,
    TimeFrameMetadata,
)
from .pipeline_state import (
    PipelineContext,
    PipelineStageKind,
    PipelineState,
    PipelineStateManager,
)
from .storing_parameters import StoringParameters

__all__ = [
    "ChannelMetadata",
    "DataSetMetadata",
    "DescriptiveStatistics",
    "MeshMetadata",
    "PipelineContext",
    "PipelineStageKind",
    "PipelineState",
    "PipelineStateManager",
    "ResolutionMetadata",
    "StoringParameters",
    "TimeFrameMetadata",
]
