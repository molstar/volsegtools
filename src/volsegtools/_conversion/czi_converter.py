from pathlib import Path

import logging

from pylibCZIrw import czi

import dask.array as da

from volsegtools._core import AxisValues, DataKind, create_reorder_permutation
from volsegtools._model import DataSetMetadata, PipelineContext, ResolutionMetadata
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Converter

vst_logger = logging.getLogger("volsegtools")


class CZIConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["czi"]

    @property
    def supports_compression(self) -> bool:
        return False

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info(f"... converting '{input_path}'")

        datasets = []
        input_name = Path(str(input_path).strip("".join(input_path.suffixes))).stem

        with czi.open_czi(str(input_path)) as czidoc:
            metadata = czidoc.metadata["ImageDocument"]["Metadata"]
            items = metadata["Scaling"]["Items"]["Distance"]
            scale = {d["@Id"]: float(d["Value"]) * 1e6 for d in items}

            physical_size = AxisValues(*tuple(scale.get(ax, 1.0) for ax in "XYZ"))
            lattice_shape = AxisValues(
                int(metadata["Information"]["Image"]["SizeX"]),
                int(metadata["Information"]["Image"]["SizeY"]),
                int(metadata["Information"]["Image"]["SizeZ"]),
            )
            cell_size = AxisValues(
                physical_size.x * lattice_shape.x,
                physical_size.y * lattice_shape.y,
                physical_size.z * lattice_shape.z,
            )

            dataset_info = DataSetMetadata(
                filename=str(input_path),
                axis_order=AxisValues(0, 1, 2),
                origin=AxisValues(0, 0, 0),
                id=input_name,
                kind=DataKind.VOLUME,
            )
            dataset = DataSet(context.working_store, dataset_info)
            resolution = dataset.add_resolution(
                ResolutionMetadata(
                    cell_size=cell_size,
                    lattice_shape=lattice_shape,
                )
            )

            bbox = czidoc.total_bounding_box
            for frame_idx in range(*bbox["T"]):
                frame = resolution.add_time_frame()
                for channel_idx in range(*bbox["C"]):
                    channel_planes = []
                    for plane_idx in range(*bbox["Z"]):
                        channel_planes.append(
                            da.from_array(
                                czidoc.read(
                                    plane={
                                        "T": frame_idx,
                                        "C": channel_idx,
                                        "Z": plane_idx,
                                    }
                                )
                            )
                        )
                    array = da.concatenate(channel_planes, axis=2)
                    array = array.transpose(create_reorder_permutation((0, 1, 2)))
                    channel = frame.add_channel()
                    channel.set_data(array, DaskBackend)
            datasets.append(dataset)

        return datasets

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
