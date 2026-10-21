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

Helper Functions
----------------

.. autosummary::
   :toctree: generated
   :nosignatures:

   calculate_approx_downsampled_sizes
   calculate_dimensions
   calculate_steps
   calculate_threshold_for_resolution


Other
-----

.. autosummary::
   :toctree: generated
   :nosignatures:

   SplineOrder
