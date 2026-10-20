from typing import Any

from zarr.abc.codec import BytesBytesCodec
from zarr.codecs import BloscCodec

import numpy as np
import pydantic

from volsegtools._core.chunking_mode import ChunkingMode
from volsegtools._core.data_kind import DataKind


class StoringParameters(pydantic.BaseModel):
    """Parameters used for storing a volume or a segmentation.

    Attributes
    ----------
    is_compression_enabled
        Whether the compression is enabled.
    chunking_mode
        Which chunking mode is used for this particular entry.
    storage_dtype
        What is the type of data stored in this entry.
    resolution_level
        Of which resolution level is this entry.
    time_frame
        Which time frame is this entry.
    channel
        Which channel is this entry.
    compressor
        Which compression codec is going to be used.
    """

    is_compression_enabled: bool = False
    chunking_mode: ChunkingMode = ChunkingMode.AUTO
    storage_dtype: Any = pydantic.Field(default_factory=lambda: np.float64)
    resolution_level: pydantic.NonNegativeInt = 0
    time_frame: pydantic.NonNegativeInt = 0
    channel: pydantic.NonNegativeInt = 0
    compressor: BytesBytesCodec = BloscCodec()
    lattice_kind: DataKind = DataKind.VOLUME

    def __str__(self) -> str:
        return f"""Storing Paramaters:
        is_compression_enabled {self.is_compression_enabled}
        chunking_mode {self.chunking_mode}
        storage_dtype {self.storage_dtype}
        resolution_level {self.resolution_level}
        time_frame {self.time_frame}
        channel {self.channel}
        compressor {self.compressor}"""
