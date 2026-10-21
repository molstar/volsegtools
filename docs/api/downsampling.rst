Downsampling
============

.. currentmodule:: volsegtools

Downsampling strategies create lower-resolution levels. Set one with :meth:`ProcessingPipelineBuilder.set_downsampling_strategy`.

.. autosummary::
   :toctree: generated
   :nosignatures:

   TricubicInterpolation
   TrilinearInterpolation
   TriquinticInterpolation
   AveragePooling
   MaxPooling
   MinPooling
   NearestNeighbor
   Smoothing
   StridedSmoothing
   SeparatedSmoothing
   Null
   InterpolationBased
   PoolingDownsamplingStrategy
