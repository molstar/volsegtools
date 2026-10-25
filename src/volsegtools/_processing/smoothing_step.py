from collections.abc import Callable

import logging

import numpy as np
import scipy

from volsegtools._core.data_kind import DataKind
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.data_set import DataSet
from volsegtools.abc import PostProcessingStep

vst_logger = logging.getLogger("volsegtools")


class SmoothingStep(PostProcessingStep):
    def __init__(
        self,
        appliable_kinds: list[DataKind] | None = None,
        filter_fn: Callable | None = None,
    ):
        if appliable_kinds is None:
            appliable_kinds = []
        self.appliable_kinds = appliable_kinds
        self.filter_fn = filter_fn

    # We cannot use the Gaussian3DKernel class here, because this convolution
    # is done separated -> we need 1D Gaussian kernel.
    def calculate_convolution_kernel(self):
        x = np.arange(-5, 5 + 1)
        kernel = np.exp(-(x**2) / (2 * 1**2))
        return kernel / kernel.sum()

    async def execute(
        self,
        datasets: list[DataSet],
        context: PipelineContext,
    ) -> list[DataSet]:
        vst_logger.info("Started 'Smoothing' post-processing step")

        kernel = self.calculate_convolution_kernel()

        def smooth_block(block, axis):
            return scipy.ndimage.convolve1d(
                block, weights=kernel, axis=axis, mode="mirror"
            )

        results = []

        for dataset in datasets:
            for channel in dataset.flat_channel_iter():
                vst_logger.info(
                    "... smoothing '%s-r%s-tf%s-c%s'",
                    channel.data_set.metadata.id,
                    channel.resolution.metadata.id,
                    channel.time_frame.metadata.id,
                    channel.metadata.id,
                )
                data = channel.handle.get_lattice(DaskBackend)
                for axis in [0, 1, 2]:
                    depth = {x: 5 if x == axis else 0 for x in range(3)}
                    smooth_data = data.map_overlap(
                        smooth_block,
                        axis=axis,
                        depth=depth,
                        boundary="reflect",
                        dtype=data.dtype,
                    )
                    channel.set_data(smooth_data, DaskBackend)
            context.timer.push_event(f"Smoothing of '{dataset.metadata.id}'")
            results.append(dataset)
        return results
