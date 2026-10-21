Error Evaluation
================

Each downsampling methods is producing some degree of error, because we are
effectively reducing the data into a grid with smaller resolution.

Different downsampling methods produce varying degree of this error and in
different parts of the image (e.g., methods that are using smoothing are
generally better in regards of surface smoothness, but they are destroying
high-frequency details.).

For this reason ``volsegtools`` makes it possible to evaluate the error in
a post-processing step using :class:`~volsegtools.ErrorEvaluationStep` that
you might add in the builder like this:

.. code-block:: python

   # This shall evaluate the results with the MSE function and report the
   # results into the 'err.json' file.
   builder.add_post_process_step(vst.ErrorEvaluation("mse", "err.json", "name"))

There are multiple already implemented error functions/metrics that are
summarized in the table below:

.. list-table::
   :header-rows: 1

   * - Name
     - Abbreviation
     - Class
     - Use-case
   * - Mean Square Error (MSE)
     - "mse"
     - :class:`~volsegtools.MSE`
     - The most common error evaluation function.
   * - Mean Absolute Error (MAE)
     - "mae"
     - :class:`~volsegtools.MAE`
     - Alternative to MSE that is not so sensitive to outliers.
   * - Root Mean Square Error (RMSE)
     - "rmse"
     - :class:`~volsegtools.RMSE`
     - Alternative to MSE that is using the units of the measured data.
   * - High-Frequency Error Norm
     - "hfen"
     - :class:`~volsegtools.HFEN`
     - Great for detection of destruction of high-frequency signals.
   * - Peak Signal-to-Noise Ratio (PSNR)
     - "psnr"
     - :class:`~volsegtools.PSNR`
     - Standardized evalution metric in signal processing.
   * - Structural Similarity Index Measure (SSIM)
     - "ssim"
     - :class:`~volsegtools.SSIM`
     - Great for evaluation of surfaces.

From our measurements for molecular data it seems that the ``HFEN`` is the most
important metric.

.. warning:: The HFEN is based on calculation is similar to smoothing the data.
             Thus, if the used downsampling method is destroying the data via
             smoothing, HFEN won't be able to detect it.

The evaluation process is as follows: (1) we upscale the downsampled data into
the original resolution (but the signal is still distorted) and then (2) we
evaluate the target metric.

.. warning:: As the data has to be interpolated into higher resolution this
             operation might be very expensive and time-consuming (especially
             for huge datasets).


Evaluation of multiple metrics
------------------------------

Using the :class:`~volsegtools.ErrorEvaluationStep` the data is upscaled for
each individual step. So constructions like this are undesirable:

.. code-block:: python

   # DO NOT DO THIS (if you do not have good reason for it)!
   builder.add_post_process_step(vst.ErrorEvaluation("mse", "err.json", "name"))
   builder.add_post_process_step(vst.ErrorEvaluation("mae", "err.json", "name"))

This would lead to doing the costly upscaling of the twice! If you want to
evaluate multiple metrics on the same data it is better to use dedicated step
called :class:`~volsegtools.ErrorEvaluationMultiStep` designed exactly for this
type of situations:

.. code-block:: python

   builder.add_post_process_step(vst.ErrorEvaluationMultiStep(
        ["mse", "mae"],
        "err.json",
        "name"
   ))

Adding your own metrics
-----------------------

If you want to add your own metric, i.e., error function, you have to implement
the :class:`~volsegtools.ErrorFunction` interface.

.. code-block:: python

   # This shall evaluate the results with the MSE function and report the
   # results into the 'errors.json' file.
   builder.add_post_process_step(vst.ErrorEvaluation("mse", "errors.json", "run_name"))
