from pathlib import Path
from typing import Protocol

from volsegtools._model import PipelineContext
from volsegtools._storage import DataSet


class Serializer(Protocol):
    """Serializes the provided array-like data into some data format."""

    async def serialize(
        self,
        data_set: DataSet,
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]:
        """Serialize given dataset.

        Some output formats do not support holding several resolutions in
        a single file, therefore, we have to create multiple files for each
        resolution and/or time frame or channel.

        Parameters
        ----------
        data_set
            Data that will be serialized.
        output_path
            Output directory for the serialized files.
        context
            Context of the pipeline executing this serializer.

        Returns
        -------
        list[Path]
            List of serialized files.
        """
        ...
