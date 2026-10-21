Processing steps
================

.. currentmodule:: volsegtools

Steps run after conversion or after downsampling. Add them with :meth:`ProcessingPipelineBuilder.add_post_conversion_step` or :meth:`ProcessingPipelineBuilder.add_post_process_step`.

.. autosummary::
   :toctree: generated
   :nosignatures:

   SmoothingStep
   ErrorEvaluationStep
   ErrorEvaluationMultiStep
   SizeEvaluationStep
   JSONSizeReporter
   StdoutSizeReporter
