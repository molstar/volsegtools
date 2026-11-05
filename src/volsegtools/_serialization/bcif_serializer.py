from collections.abc import Collection
from pathlib import Path

import logging

from ciftools.binary.encoder import (
    BYTE_ARRAY,
    DELTA,
    INTEGER_PACKING,
    ComposeEncoders,
    FixedPoint,
)
from ciftools.binary.writer import RUN_LENGTH
from ciftools.models.writer import CIFCategoryDesc as CategoryDesc, CIFFieldDesc as Field

import ciftools
import ciftools.serialization
import numpy as np

from volsegtools._core import CompressionLevel
from volsegtools._model import PipelineContext
from volsegtools._processing import DaskBackend
from volsegtools._storage import Channel, DataSet, create_file_name
from volsegtools.abc import Serializer

vst_logger = logging.getLogger("volsegtools")


class BCIFSerializer(Serializer):
    def __init__(
        self,
        level: CompressionLevel = CompressionLevel.LOSSLESS,
    ):
        """Construct BinaryCIF Serializer.

        Parameters
        ----------
        level
            The level of compression aggresiveness, the higher it is the more
            lossful compression schemes can be applied to the data.
        """
        self.level = level

    @staticmethod
    def _continuous_volume_encoder(
        level: CompressionLevel, channel: Channel
    ) -> ComposeEncoders:
        """Create encoder for continuous (float) volume."""
        match level:
            case CompressionLevel.LOW:
                return ComposeEncoders(FixedPoint(1000), DELTA, INTEGER_PACKING)
            case CompressionLevel.MEDIUM:
                return ComposeEncoders(
                    FixedPoint(100), DELTA, RUN_LENGTH, INTEGER_PACKING
                )
            case CompressionLevel.HIGH | CompressionLevel.MAXIMUM:
                return ComposeEncoders(FixedPoint(10), DELTA, RUN_LENGTH, INTEGER_PACKING)
            case _:
                return ComposeEncoders(BYTE_ARRAY)

    @staticmethod
    def _discrete_volume_encoder(
        level: CompressionLevel, channel: Channel
    ) -> ComposeEncoders:
        if (
            channel.handle.dtype in (np.int64, np.uint64)
            and level != CompressionLevel.LOSSLESS
        ):
            vst_logger.warning("non-lossless compression turns 64-bit to 32-bit!")

        match level:
            case CompressionLevel.LOSSLESS:
                return ComposeEncoders(INTEGER_PACKING)
            case CompressionLevel.MAXIMUM:
                return ComposeEncoders(DELTA, RUN_LENGTH, INTEGER_PACKING)
            case _:
                return ComposeEncoders(DELTA, RUN_LENGTH, INTEGER_PACKING)

    @staticmethod
    def _choose_encoder(level: CompressionLevel, channel: Channel):
        if np.issubdtype(channel.handle.dtype, np.integer):
            return BCIFSerializer._discrete_volume_encoder(level, channel)
        return BCIFSerializer._continuous_volume_encoder(level, channel)

    async def serialize(
        self,
        data_set: DataSet,
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]:
        # This is currently working only for volumes!
        output_files = []
        for channel in data_set.flat_channel_iter():
            writer = ciftools.serialization.create_binary_writer()

            # We have to create the SERVER category, because it is required, we
            # just have to say that it is a box
            writer.start_data_block("SERVER")
            writer.write_category(_DensityServerResultDesc(), [np.arange(0)])

            data = channel.handle.get_lattice(DaskBackend)
            data = data.transpose(data_set.metadata.axis_order.to_tuple(dtype=int))
            data = np.ravel(data.compute(), order="F")

            writer.start_data_block("EM")
            writer.write_category(_VolumeData3DInfoDesc(), [channel])

            encoder = self._choose_encoder(self.level, channel)
            writer.write_category(_VolumeData3DDesc(encoder), [data])

            file_name = create_file_name(channel, ".bcif")

            output_file_path = output_path / file_name
            output_file_path.write_bytes(writer.encode())
            output_files.append(output_file_path)
        return output_files


class _VolumeData3DInfoDesc(CategoryDesc):
    name = "volume_data_3d_info"

    @staticmethod
    def get_row_count(_) -> int:
        return 1

    @staticmethod
    def get_field_descriptors(channel: Channel) -> Collection[Field]:
        def volume_server_encoder(_):
            return BYTE_ARRAY

        data_set = channel.data_set
        resolution = channel.resolution

        return [
            Field.strings(
                name="name",
                value=lambda d, i: str(data_set.metadata.id),
            ),
            Field.numbers(
                name="axis_order[0]",
                value=lambda d, i: data_set.metadata.axis_order.x,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="axis_order[1]",
                value=lambda d, i: data_set.metadata.axis_order.y,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="axis_order[2]",
                value=lambda d, i: data_set.metadata.axis_order.z,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="origin[0]",
                value=lambda d, i: data_set.metadata.origin.x,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="origin[1]",
                value=lambda d, i: data_set.metadata.origin.y,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="origin[2]",
                value=lambda d, i: data_set.metadata.origin.z,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="dimensions[0]",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="dimensions[1]",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="dimensions[2]",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_rate",
                value=lambda d, i: 2**resolution.metadata.id,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[0]",
                value=lambda d, i: resolution.metadata.lattice_shape.x,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[1]",
                value=lambda d, i: resolution.metadata.lattice_shape.y,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[2]",
                value=lambda d, i: resolution.metadata.lattice_shape.z,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="spacegroup_number",
                value=lambda d, i: 1,
                encoder=volume_server_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="spacegroup_cell_size[0]",
                value=lambda d, i: resolution.metadata.cell_size.x,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_size[1]",
                value=lambda d, i: resolution.metadata.cell_size.y,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_size[2]",
                value=lambda d, i: resolution.metadata.cell_size.z,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[0]",
                value=lambda d, i: 90,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[1]",
                value=lambda d, i: 90,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[2]",
                value=lambda d, i: 90,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="mean_source",
                value=lambda d, i: channel.metadata.statistics.mean,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="mean_sampled",
                value=lambda d, i: channel.metadata.statistics.mean,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="sigma_source",
                value=lambda d, i: channel.metadata.statistics.std,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="sigma_sampled",
                value=lambda d, i: channel.metadata.statistics.std,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="min_source",
                value=lambda d, i: channel.metadata.statistics.min,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="min_sampled",
                value=lambda d, i: channel.metadata.statistics.min,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="max_source",
                value=lambda d, i: channel.metadata.statistics.max,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="max_sampled",
                value=lambda d, i: channel.metadata.statistics.max,
                encoder=volume_server_encoder,
                dtype="f8",
            ),
        ]


class _DensityServerResultDesc(CategoryDesc):
    name = "density_server_result"

    @staticmethod
    def get_row_count(_) -> int:
        return 1

    @staticmethod
    def get_field_descriptors(data) -> Collection[Field]:
        return [
            Field.strings(name="query_type", value=lambda d, i: "box"),
        ]


class _VolumeData3DDesc(CategoryDesc):
    def encoder_fn(self):
        return BYTE_ARRAY

    name = "volume_data_3d"

    def __init__(self, encoder):
        _VolumeData3DDesc.encoder_fn = lambda _: encoder

    @staticmethod
    def get_row_count(data: np.ndarray) -> int:
        return data.size

    @staticmethod
    def get_field_descriptors(data: np.ndarray) -> Collection[Field]:
        return [
            Field.number_array(
                name="values",
                array=lambda volume: volume,
                encoder=_VolumeData3DDesc.encoder_fn,
                dtype=data.dtype,
            ),
        ]
