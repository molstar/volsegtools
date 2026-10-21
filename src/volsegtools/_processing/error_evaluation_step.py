"""
Implementation of the error evaluation for the pipeline.

The idea is simple:
    1. Take the original dataset and all resolution levels.
    2. Upsample the resolutions levels so that the lattice has the same shape
       as the original dataset.
    3. Evaluate all provide error functions over the original dataset lattice
       and upsampled resolution data.

To implement this idea the module has to be split into several sections:
    1. Interfaces and their adapters.
    2. Individual error functions.
    3. The particular error evaluation step.

Currently, we only take the evaluation via Dask into account. Therefore, we
try to maximize the number of shared computation nodes between error functions
so that are not doing any work twice.
"""

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol, cast

import datetime
import enum
import json
import logging
import math

from scipy.ndimage import gaussian_laplace
from skimage.metrics import structural_similarity as ssim

import dask.array as da
import numpy as np
import pydantic
import scipy
import yaml

from volsegtools._core.data_kind import SerializableDataKind
from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing.dask_backend import DaskBackend
from volsegtools._storage.channel import Channel
from volsegtools._storage.data_set import DataSet
from volsegtools.abc import PostProcessingStep

vst_logger = logging.getLogger("volsegtools")

# -----------------------------------------------------------------------------
# Interfaces and internal implementations
# -----------------------------------------------------------------------------


class ErrorFunction(Protocol):
    """An error metric built as a lazy Dask graph.

    Implementations must not call ``compute`` themselves. The evaluation step
    collects all results and computes them together, so shared parts of the
    graph (most importantly the upsampled candidate) are only evaluated once.

    The most important detail about the return value of the call of this
    functor is that it has to return the Dask array (that was not computed).
    This way we can apply the computation graph optimization.
    """

    name: str

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array: ...


ErrorFunctionLike = ErrorFunction | Callable[[da.Array, da.Array], da.Array]


class ErrorFunctionAdapter(ErrorFunction):
    """Adapts a plain ``(reference, candidate)`` callable to the protocol."""

    def __init__(
        self,
        name: str,
        fn: Callable[[da.Array, da.Array], da.Array],
    ):
        self.name = name
        self._fn = fn

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        return self._fn(reference, candidate, **kwargs)


def as_error_function(
    error_fn: ErrorFunctionLike,
    name: str | None = None,
) -> ErrorFunction:
    """Asserts that the incomming function is compatible with the
    ``ErrorFunction`` protocol.

    The input can be either known class implementing the ``ErrorFunction``
    protocol or an arbitrary function that is then adapted to it.

    If the user passes in valid ``ErrorFunction`` class with the name attribute
    and still provides the ``name`` parameter, then the class is going to be
    adapted.

    Parameters
    ----------
    error_fn
        Callable error function.
    name
        Custom name of the adapted error function.

    Raises
    ------
    TypeError
        If the provided ``error_fn`` is not callable.

    Returns
    -------
    ErrorFunction
        Adapted ``ErrorFunction`` class.
    """

    if not callable(error_fn):
        raise TypeError("The provided error function is not callable")

    if name is None and getattr(error_fn, "name", None) is not None:
        return cast("ErrorFunction", error_fn)

    function_name = str(
        name
        or getattr(error_fn, "name", None)
        or getattr(error_fn, "__name__", type(error_fn).__name__)
    )
    return ErrorFunctionAdapter(function_name, cast("Callable", error_fn))


class ErrorRecord(pydantic.BaseModel):
    """A single error evaluation result."""

    id: str
    """Name of the evaluated dataset."""

    resolution: int
    """ID of the currently evaluated resolution."""

    kind: SerializableDataKind
    """Type of the dataset."""

    channel_id: int
    """ID of the currently evaluated channel."""

    timestamp: str
    """Timestamp of creation of this record."""

    label: str
    """Custom label of the processing workflow."""

    error_method: str
    """Name of the used error evaluation method."""

    error: float
    """Value of the error."""


class ErrorReporter(Protocol):
    """Receives a batch of error records once they have been computed."""

    def report(self, records: Sequence[ErrorRecord]) -> None: ...


class StdoutErrorReporter:
    def report(self, records: Sequence[ErrorRecord]) -> None:
        serialized = [record.model_dump(mode="json") for record in records]

        print("--------------------------------------------------------------")
        print("Error Evalution Report")
        print("--------------------------------------------------------------")
        print(yaml.dump(serialized, sort_keys=False))


class JSONErrorReporter:
    def __init__(self, output_path: Path):
        self.output_path = output_path

    def report(self, records: Sequence[ErrorRecord]) -> None:
        existing: list = []
        if self.output_path.exists():
            with self.output_path.open() as file:
                existing = json.load(file)

        serialized = [record.model_dump(mode="json") for record in records]

        with self.output_path.open("w") as file:
            json.dump([*existing, *serialized], file, indent=2)


class UpsamplingQualityLevel(enum.IntEnum):
    """Denotes the quality of the upsampling used in the error evalution.

    The higher is the quality of upsampling the more precise would be the
    results. However, the time to fully upsample the data is also growing.
    """

    LOW = 1
    MEDIUM = 3
    HIGH = 5


# -----------------------------------------------------------------------------
# Individual error function implementations
# -----------------------------------------------------------------------------


class HFEN(ErrorFunction):
    name = "HFEN"

    def __init__(self, sigma: float = 1.5):
        self.sigma = sigma

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        sigma = self.sigma
        depth = int(np.ceil(4 * sigma))

        def block_laplace(block, sigma):
            return gaussian_laplace(block, sigma=sigma)

        log_reference = reference.map_overlap(
            block_laplace,
            depth=depth,
            boundary="reflect",
            dtype="float32",
            sigma=sigma,
        )
        log_candidate = candidate.map_overlap(
            block_laplace,
            depth=depth,
            boundary="reflect",
            dtype="float32",
            sigma=sigma,
        )

        diff = log_reference - log_candidate
        numerator = da.sqrt(da.sum(diff**2))
        denominator = da.sqrt(da.sum(log_reference**2))
        denominator = da.where(denominator == 0, 1e-10, denominator)

        return numerator / denominator


class VFM(ErrorFunction):
    name = "VFM"

    def __init__(self, threshold: float = 0.0):
        self.threshold = threshold

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        reference_empty_count = (reference < self.threshold).sum()
        candidate_empty_count = (candidate < self.threshold).sum()

        safe_reference_count = da.maximum(reference_empty_count, 1)
        return da.where(
            reference_empty_count == 0,
            np.nan,
            candidate_empty_count / safe_reference_count,
        )


class SSIM(ErrorFunction):
    name = "SSIM"

    def __init__(self, win_size: int = 5, mask_threshold: float = 0.0):
        self.win_size = win_size
        self.mask_threshold = mask_threshold

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        data_range = kwargs["data_range"]
        if data_range is None or data_range <= 0:
            data_range = 1.0

        def calculate_ssim(block1, block2):
            _, ssim_map = ssim(
                block1,
                block2,
                data_range=float(data_range),
                full=True,
                win_size=self.win_size,
            )
            return ssim_map

        results = da.map_overlap(
            calculate_ssim,
            reference.astype(np.float64),
            candidate.astype(np.float64),
            depth=self.win_size // 2,
            boundary="reflect",
            dtype="float64",
        )

        mask = reference > self.mask_threshold
        return da.nanmean(da.where(mask, results, np.nan))


class MSE(ErrorFunction):
    name = "MSE"

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        return da.mean((reference - candidate) ** 2)


class MAE(ErrorFunction):
    name = "MAE"

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        return da.mean(da.abs(reference - candidate))


class RMSE(ErrorFunction):
    name = "RMSE"

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        return da.sqrt(da.mean((reference - candidate) ** 2))


class PSNR(ErrorFunction):
    name = "PSNR"

    def __call__(
        self,
        reference: da.Array,
        candidate: da.Array,
        **kwargs,
    ) -> da.Array:
        data_range = kwargs["data_range"]
        if data_range is None:
            data_range = reference.max() - reference.min()

        safe_data_range = da.where(data_range == 0, 1.0, data_range)
        mse = da.mean((reference - candidate) ** 2)
        safe_mse = da.maximum(mse, 1e-30)
        psnr = 20 * da.log10(safe_data_range / da.sqrt(safe_mse))

        return da.where(mse == 0, np.inf, psnr)


# -----------------------------------------------------------------------------
# Step implementation
# -----------------------------------------------------------------------------


class ErrorEvaluationStep(PostProcessingStep):
    """Evaluates the of error between downsampled resolutions and the original.

    Multiple error functions can be passed into this step, and it the adviced
    approach, because then the library is able to optimize the computation
    graph leading to faster evaluation.

    The user can specify which error reporter do they wish to use.

    Proper error evaluation step should be accompanied with some label, this
    has to be provided by the user and it is used to distinguish between
    various run of the error evaluation.

    There are levels of the quality of evaluation: the higher the quality the
    more time is required for proper upsampling, but it is leading to more
    precise results. By default a middle-ground approach is taken.
    """

    def __init__(
        self,
        error_functions: Sequence[ErrorFunctionLike],
        *,
        reporter: ErrorReporter | None = None,
        label: str = "",
        upsample_quality: UpsamplingQualityLevel = UpsamplingQualityLevel.MEDIUM,
    ):
        if not error_functions:
            raise ValueError("At least one error function must be provided")

        self.error_functions = [as_error_function(fn) for fn in error_functions]
        if reporter is None:
            self.reporter = StdoutErrorReporter()
        else:
            self.reporter = reporter

        self._upsampling_order = int(upsample_quality)

        self.label = label

    # TODO is from elsewhere
    def calculate_new_chunks(self, channel, factor: float | tuple[float, ...]):
        if isinstance(factor, float):
            return tuple(
                tuple(math.ceil(ax * factor) for ax in axes) for axes in channel.chunks
            )
        if isinstance(factor, tuple):
            return tuple(
                tuple(math.ceil(ax * factor[idx]) for ax in axes)
                for idx, axes in enumerate(channel.chunks)
            )
        raise TypeError("Unsupported type for chunk calculation")

    def _upsample_data(self, original: da.Array, data: da.Array) -> da.Array:
        """Upsamples the downsampled data to the size of the original lattice.

        For evaluation of error functions it is required to have lattice of the
        same size.

        A tricubic interpolation is used for this upsampling. The higher order
        of the polynomial the higher is the precision of the error evalution,
        howerer, it is also taking much more time.

        Parameters
        ----------
        original
            The original data lattice.
        data
            The downsampled data lattice, it is presummed that it will be
            smaller than the original.

        Returns
        -------
        da.Array
            Upsampled data lattice to the shape of the original data.
        """
        zoom = tuple(x / y for x, y in zip(original.shape, data.shape, strict=False))

        def block_triquintic_zoom(block):
            return scipy.ndimage.zoom(
                block, zoom=zoom, order=self._upsampling_order, mode="reflect"
            )

        return da.map_blocks(
            block_triquintic_zoom,
            data,
            dtype=data.dtype,
            chunks=self.calculate_new_chunks(data, zoom),
        )

    @staticmethod
    def _data_range(channel: Channel) -> float | None:
        """Calculates the numerical range of the data held in the channel.

        Parameter
        ---------
        channel
            A source of the data lattice for which we want to know the data
            range.

        Returns
        -------
        float: optional
            The numerical data range, if there is any. If the data is somehow
            not well-defined then it returns ``None``.
        """
        statistics = channel.metadata.statistics
        value = float(statistics.max - statistics.min)
        if value > 0:
            return value
        return None

    def _make_record(
        self,
        channel: Channel,
        error_method_name: str,
    ) -> ErrorRecord:
        """Creates a new ``ErrorRecord`` from provide information.

        The record is created **without** the particular error value. It should
        be provided later, because we are deffering the actual calculation to
        later part of the program to take advantage of the compute graph
        optimization.

        Parameters
        ----------
        channel
            The main source of the information for the record.
        error_method_name
            Name of the used error evaluation method. Usually it is part of the
            ``ErrorFunction`` protocol. But for simple functions it might be
            a just the literal name of the function.

        Returns
        -------
        ErrorRecord
            A record holding all the information about the evaluation of
            current resolution with a particular method.
        """
        dataset = channel.data_set
        return ErrorRecord(
            id=dataset.metadata.id,
            resolution=channel.resolution.metadata.id,
            kind=dataset.metadata.kind,
            channel_id=channel.metadata.id,
            timestamp=str(datetime.datetime.now()),
            label=self.label,
            error_method=error_method_name,
            error=0.0,
        )

    def evaluate_for_dataset(
        self,
        dataset: DataSet,
        context: PipelineContext,
    ) -> list[ErrorRecord]:
        """Evaluates all resolutions of one logical data set against resolution 0.

        Parameters
        ----------
        dataset
            Dataset containing the resolution pyramid for evaluation.

        context
            see :doc:`~volsegtools.abc.PostProcessingStep`

        Returns
        -------
        list[ErrorRecord]
            List of error records for this particular dataset.
        """
        pending_evaluations: list[tuple[ErrorRecord, da.Array]] = []
        reference_channels = list(dataset[0].flat_channel_iter())

        if len(dataset.resolutions) < 2:
            vst_logger.warning("There was not resolution against which compare!")
            return []

        for resolution in dataset.resolutions[1:]:
            resolution_channels = list(resolution.flat_channel_iter())

            for reference, candidate in zip(
                reference_channels, resolution_channels, strict=False
            ):
                reference_lattice = reference.handle.get_lattice(DaskBackend)
                candidate_lattice = candidate.handle.get_lattice(DaskBackend)
                candidate_lattice = self._upsample_data(
                    reference_lattice,
                    candidate_lattice,
                )

                if candidate_lattice.shape != reference_lattice.shape:
                    vst_logger.warning(
                        "Shapes of reference %s and upsampled %s do not match, "
                        "skipping channel %s at resolution %s",
                        reference_lattice.shape,
                        candidate_lattice.shape,
                        candidate.metadata.id,
                        resolution.metadata.id,
                    )
                    continue

                vst_logger.info(
                    "... adding evaluation job for '%s-r%s-t%s-ch%s'",
                    dataset.metadata.id,
                    resolution.metadata.id,
                    candidate.parent.metadata.id,
                    candidate.metadata.id,
                )

                data_range = self._data_range(reference)
                for error_fn in self.error_functions:
                    pending_evaluations.append(
                        (
                            self._make_record(candidate, error_fn.name),
                            error_fn(
                                reference_lattice,
                                candidate_lattice,
                                data_range=data_range,
                            ),
                        ),
                    )

        # We did not calculate anything
        if not pending_evaluations:
            return []

        # A single compute call lets Dask share the reference lattice and the
        # upsampled candidate between all error functions and resolutions.
        values = da.compute(*(value for _, value in pending_evaluations))
        vst_logger.info("... evaluation complete")

        records: list[ErrorRecord] = []
        for (record, _), value in zip(pending_evaluations, values, strict=True):
            record.error = float(value)
            records.append(record)

        context.timer.push_event(f"Error evaluation of '{dataset.metadata.id}'")
        return records

    async def execute(
        self,
        datasets: list[DataSet],
        context: PipelineContext,
    ) -> list[DataSet]:
        """Evaluates all resolutions of all provided datasets.

        Parameters
        ----------
        datasets
            see :doc:`~volsegtools.abc.PostProcessingStep`

        context
            see :doc:`~volsegtools.abc.PostProcessingStep`

        Returns
        -------
        list[Dataset]
            Unchanged list of datasets with all resolutions. Error evalution
            does not change anything in the input.
        """
        vst_logger.info(
            "Started 'Error Evaluation' post-processing step with %s",
            ", ".join(error_fn.name for error_fn in self.error_functions),
        )

        records = []
        for dataset in datasets:
            records += self.evaluate_for_dataset(dataset, context)

        self.reporter.report(records)

        return datasets
