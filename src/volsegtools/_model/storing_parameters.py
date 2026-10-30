from typing import Any

from zarr.abc.codec import BytesBytesCodec
from zarr.codecs import BloscCodec

import numpy as np
import pydantic

from volsegtools._core.chunking_mode import ChunkingMode
from volsegtools._core.data_kind import DataKind


class StoringParameters(pydantic.BaseModel):
    """Parameters used for storing a volume or a segmentation."""

    model_config = pydantic.ConfigDict(use_attribute_docstrings=True)

    is_compression_enabled: bool = False
    """
    Whether the compression is enabled.
    """
    chunking_mode: ChunkingMode = ChunkingMode.AUTO
    """
    Which chunking mode is used for this particular entry.
    """
    storage_dtype: Any = pydantic.Field(default_factory=lambda: np.float64)
    """
    What is the type of data stored in this entry.
    """
    resolution_level: pydantic.NonNegativeInt = 0
    """
    Of which resolution level is this entry.
    """
    time_frame: pydantic.NonNegativeInt = 0
    """
    Which time frame is this entry.
    """
    channel: pydantic.NonNegativeInt = 0
    """
    Which channel is this entry.
    """
    compressor: BytesBytesCodec = BloscCodec()
    """
    Which compression codec is going to be used.
    """
    lattice_kind: DataKind = DataKind.VOLUME
    """
    The kind of lattice that we wish to store.
    """

    def __str__(self) -> str:
        return f"""Storing Paramaters:
        is_compression_enabled {self.is_compression_enabled}
        chunking_mode {self.chunking_mode}
        storage_dtype {self.storage_dtype}
        resolution_level {self.resolution_level}
        time_frame {self.time_frame}
        channel {self.channel}
        compressor {self.compressor}"""
