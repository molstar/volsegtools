"""
Contains classes and functions related to high-level processing.

It serves as an aggregate of all other processing steps.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .dask_backend import DaskBackend
from .mesh_backend import MeshBackend
from .error_evaluation_step import (
    HFEN,
    MAE,
    MSE,
    PSNR,
    RMSE,
    SSIM,
    VFM,
    ErrorEvaluationStep,
    ErrorFunction,
    JSONErrorReporter,
    StdoutErrorReporter,
)
from .numpy_backend import NumPyBackend
from .processing_pipeline import ProcessingPipeline
from .processing_pipeline_builder import ProcessingPipelineBuilder, create_builder
from .size_evaluation_step import (
    JSONSizeReporter,
    SizeEvaluationStep,
    StdoutSizeReporter,
)
from .smoothing_step import SmoothingStep

__all__ = [
    "HFEN",
    "MAE",
    "MSE",
    "PSNR",
    "RMSE",
    "SSIM",
    "VFM",
    "DaskBackend",
    "ErrorEvaluationStep",
    "ErrorFunction",
    "JSONErrorReporter",
    "JSONSizeReporter",
    "MeshBackend",
    "NumPyBackend",
    "ProcessingPipeline",
    "ProcessingPipelineBuilder",
    "SizeEvaluationStep",
    "SmoothingStep",
    "StdoutErrorReporter",
    "StdoutSizeReporter",
    "create_builder",
]
