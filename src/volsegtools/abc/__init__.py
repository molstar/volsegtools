"""
Contains abstract interface to core classes that are used in the processing pipeline.
"""

from volsegtools._core.computation_backend import ComputationBackend
from volsegtools._core.kernel import ConvolutionKernel

from .bundler import Bundler
from .converter import Converter
from .downsampling_strategy import DataType, DownsamplingStrategy, TData
from .post_conversion_step import PostConversionStep
from .post_processing_step import PostProcessingStep
from .processing_pipeline import ProcessingPipeline
from .serializer import Serializer

__all__ = [
    "Bundler",
    "ComputationBackend",
    "Converter",
    "ConvolutionKernel",
    "DataType",
    "DownsamplingStrategy",
    "PostConversionStep",
    "PostProcessingStep",
    "ProcessingPipeline",
    "Serializer",
    "TData",
]

import inspect as _inspect

for _name in __all__:
    _obj = globals().get(_name)
    if _inspect.isclass(_obj) or _inspect.isfunction(_obj):
        _obj.__module__ = __name__
