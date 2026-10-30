from collections.abc import Iterator

import enum
import logging
import math

import dask.array as da
import dask_image.ndinterp
import numpy as np

from volsegtools._downsampling.common import calculate_steps
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.channel import Channel
from volsegtools.abc import DownsamplingStrategy

vst_logger = logging.getLogger("volsegtools")


class SplineOrder(enum.IntEnum):
    """The order of spline used for the interpolation."""

    TRILINEAR = 1
    TRICUBIC = 3
    TRIQUINTIC = 5


class InterpolationBased(DownsamplingStrategy[Channel]):
    """Base class for downsampling methods based on spline interpolation."""

    def __init__(self, order: SplineOrder, zoom: float):
        """
        Parameters
        ----------
        order
            Order of spline used for interpolation.
        zoom
            Goal zoom level of the method.

        Raises
        ------
        RuntimeError
            If the ``zoom`` is close to 0.
            If unknown spline order was provided.
        """

        if math.isclose(zoom, 0):
            raise RuntimeError("Zoom has to be bigger than 0")

        if order not in SplineOrder:
            raise RuntimeError("Unknown polynomial factor for interpolation")

        self.order = order
        self.zoom = 1 / zoom

    def execute(self, data: Channel, context: PipelineContext) -> Iterator[Channel]:
        match self.order:
            case 1:
                vst_logger.info("Using the 'Trilinear' downsampling strategy")
            case 3:
                vst_logger.info("Using the 'Tricubic' downsampling strategy")
            case 5:
                vst_logger.info("Using the 'Triquintic' downsampling strategy")

        current_data = data.handle.get_lattice(DaskBackend)
        original_dtype = current_data.dtype
        steps = calculate_steps(data, context.size_threshold)

        for _ in range(steps):
            # This calculation is similar to `scipy.zoom` which is the default
            # method used in cupy.
            output_shape = tuple(round(n / self.zoom) for n in current_data.shape)
            output_chunks = tuple(max(c // self.zoom, 1) for c in current_data.chunksize)

            # Higher orders of spline interpolation require prefiltering.
            # However, dask-image is supporting the pre-filtering only with the
            # 'constant' mode which is producing higher error.
            #
            # Therefore, we have to do the padding ourselves before-hand
            border = self.zoom * (self.order + 1) if self.order > 1 else 0
            if border:
                current_data = da.pad(current_data, border, mode="symmetric")

            voxel_center_offset = (self.zoom - 1) / 2 + border

            current_data = dask_image.ndinterp.affine_transform(
                current_data,
                matrix=np.diag([float(self.zoom)] * current_data.ndim),
                offset=voxel_center_offset,
                output_shape=output_shape,
                output_chunks=output_chunks,
                order=self.order,
                mode="constant" if self.order > 1 else "nearest",
                prefilter=self.order > 1,
            )

            # We have to cast the type for higher order interpolation, because
            # the filtering is silently casting the data to 'float64'.
            if np.issubdtype(current_data.dtype, np.integer):
                info = np.iinfo(current_data.dtype)
                # rounding and saturating the resulting value.
                current_data = da.clip(da.rint(current_data), info.min, info.max)

            if current_data.dtype != original_dtype:
                current_data = current_data.astype(original_dtype)

            yield current_data


class TrilinearInterpolation(InterpolationBased):
    def __init__(self, zoom=0.5):
        super().__init__(SplineOrder.TRILINEAR, zoom)


class TricubicInterpolation(InterpolationBased):
    def __init__(self, zoom=0.5):
        super().__init__(SplineOrder.TRICUBIC, zoom)


class TriquinticInterpolation(InterpolationBased):
    def __init__(self, zoom=0.5):
        super().__init__(SplineOrder.TRIQUINTIC, zoom)
