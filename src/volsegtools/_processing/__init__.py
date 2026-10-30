"""
Contains classes and functions related to high-level processing.

It serves as an aggregate of all other processing steps.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .dask_backend import DaskBackend
from .error_evaluation_step import (
    HFEN,
    MAE,
    MSE,
    PSNR,
    RMSE,
    SSIM,
    VFM,
    ConsoleErrorReporter,
    ErrorEvaluationStep,
    ErrorFunction,
    ErrorRecord,
    ErrorReporter,
    JSONErrorReporter,
    UpsamplingQualityLevel,
)
from .mesh_backend import MeshBackend
from .numpy_backend import NumPyBackend
from .processing_pipeline import ProcessingPipeline
from .processing_pipeline_builder import ProcessingPipelineBuilder, create_builder
from .size_evaluation_step import (
    ConsoleSizeReporter,
    JSONSizeReporter,
    SizeEvaluationStep,
    SizeReporter,
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
    "ConsoleErrorReporter",
    "ConsoleSizeReporter",
    "DaskBackend",
    "ErrorEvaluationStep",
    "ErrorFunction",
    "ErrorRecord",
    "ErrorReporter",
    "JSONErrorReporter",
    "JSONSizeReporter",
    "MeshBackend",
    "NumPyBackend",
    "ProcessingPipeline",
    "ProcessingPipelineBuilder",
    "SizeEvaluationStep",
    "SizeReporter",
    "SmoothingStep",
    "UpsamplingQualityLevel",
    "create_builder",
]
