from pathlib import Path

import ngff_zarr as nz

from volsegtools._core import AxisValues, DataKind
from volsegtools._core.axis_values import create_reorder_permutation
from volsegtools._model import DataSetMetadata, PipelineContext, ResolutionMetadata
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage import DataSet
from volsegtools.abc import Converter


class NGFFConverter(Converter):
    @property
    def supported_suffixes(self):
        return ["zarr", "ome.zarr"]

    @property
    def supports_compression(self) -> bool:
        return False

    async def convert_volume(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        return NGFFConverter._convert(input_path, context, DataKind.VOLUME)

    async def convert_segmentation(
        self,
        input_path: Path,
        context: PipelineContext,
    ) -> list[DataSet]:
        return NGFFConverter._convert(input_path, context, DataKind.SEGMENTATION_VOLUME)

    @staticmethod
    def _convert(input_path: Path, context: PipelineContext, kind: DataKind):
        pyramid = nz.from_ngff_zarr(input_path)

        if not pyramid.images:
            raise RuntimeError(f"No OME-NGFF images found in {input_path}")

        original_res_img = pyramid.images[0]
        dim_labels = [str(ax).lower() for ax in original_res_img.dims]
        order = tuple(dim_labels.index(ax) for ax in "xyz")
        new_order = create_reorder_permutation(order)
        array = original_res_img.data.transpose(new_order)

        shape = dict(zip(["x", "y", "z"], array.shape, strict=False))
        spacing = original_res_img.scale
        translation = tuple(original_res_img.translation[ax] for ax in "xyz")
        cell_size = tuple(shape[ax] * spacing[ax] for ax in "xyz")

        if ".ome" in input_path.suffixes:
            dataset_id = Path(".".join(str(input_path).split(".")[:-2])).stem
        else:
            dataset_id = input_path.stem

        info = DataSetMetadata(
            filename=str(input_path),
            axis_order=AxisValues(*order),
            origin=AxisValues(*translation),
            id=dataset_id,
            kind=kind,
        )
        dataset = DataSet(context.working_store, info)

        if "t" not in dim_labels:
            array = array[None, ...]
        if "c" not in dim_labels:
            array = array[:, None, ...]

        resolution_info = ResolutionMetadata(
            cell_size=AxisValues(*cell_size),
            lattice_shape=AxisValues(*array.shape),
        )
        resolution = dataset.add_resolution(resolution_info)

        for frame_data in array:
            frame = resolution.add_time_frame()
            for idx, channel_data in enumerate(frame_data):
                channel = frame.add_channel(idx)
                channel.set_data(channel_data.rechunk("auto"), DaskBackend)

        return [dataset]

    async def collect_annotations(self, input_path, context) -> None:
        raise NotImplementedError

    async def collect_metadata(self, input_path, context) -> None:
        raise NotImplementedError
