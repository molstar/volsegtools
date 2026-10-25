from pathlib import Path

import logging

import numpy as np

from volsegtools._core import AxisValues, DataKind
from volsegtools._model import DataSetMetadata, PipelineContext, ResolutionMetadata
from volsegtools._processing import NumPyBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")


class NumpyConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["txt", "csv", "npy", "npz"]

    @property
    def supports_compression(self) -> bool:
        return False

    def is_suffix_supported(self, suffix: str):
        return suffix in self.supported_suffixes

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        data = np.load(input_path)

        if len(data.shape) != 3:
            raise RuntimeError("Numpy data has to be 3D")

        data_set_info = DataSetMetadata(
            filename=input_path.name,
            id=input_path.stem,
            kind=DataKind.VOLUME,
        )
        data_set = DataSet(context.working_store, data_set_info)

        resolution_info = ResolutionMetadata(
            cell_size=AxisValues(1, 1, 1),
            lattice_shape=AxisValues(
                data.shape[0],
                data.shape[1],
                data.shape[2],
            ),
        )
        resolution = data_set.add_resolution(resolution_info)

        frame = resolution.add_time_frame()
        channel = frame.add_channel(0)
        channel.set_data(data, NumPyBackend)

        return [data_set] if data_set is not None else []

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        data_sets = await self.convert_volume(input_path, context)
        for ds in data_sets:
            ds.metadata.kind = DataKind.SEGMENTATION_VOLUME
        return data_sets

    async def collect_annotations(self, input_path, context) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path, context) -> None:
        raise NotImplementedError
