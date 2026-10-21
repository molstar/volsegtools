How to Measure Downsampling Error
---------------------------------

The choice of the best downsampling method is dependent on the data and we as
humans usually cannot be absolutely sure which method is the right one.

For this reason you can evaluate the error between the original resolution and
the current downsampled resolution.

Volsegtools has a whole builtin processing step for this called
:class:`~volsegtools.ErrorEvaluationStep`.

First, you have to choose one (or more) metrics for the evaluation (or you can
use roll out your own).

.. list-table::
   :header-rows: 1

   * - Name
     - Class
     - Use-case
   * - Mean Square Error (MSE)
     - :class:`~volsegtools.MSE`
     - The most common error evaluation function.
   * - Mean Absolute Error (MAE)
     - :class:`~volsegtools.MAE`
     - Alternative to MSE that is not so sensitive to outliers.
   * - Root Mean Square Error (RMSE)
     - :class:`~volsegtools.RMSE`
     - Alternative to MSE that is using the units of the measured data.
   * - High-Frequency Error Norm
     - :class:`~volsegtools.HFEN`
     - Great for detection of destruction of high-frequency signals.
   * - Peak Signal-to-Noise Ratio (PSNR)
     - :class:`~volsegtools.PSNR`
     - Standardized evalution metric in signal processing.
   * - Structural Similarity Index Measure (SSIM)
     - :class:`~volsegtools.SSIM`
     - Great for evaluation of surfaces.

From our measurements for molecular data it seems that the
:class:`~volsegtools.HFEN` is the most significant metric.

.. warning:: The HFEN is based on calculation is similar to smoothing the data.
             Thus, if the used downsampling method is destroying the data via
             smoothing, HFEN won't be able to detect it.

The evaluation process is as follows: (1) we upscale the downsampled data into
the original resolution (but the signal is still distorted) and then (2) we
evaluate the target metric.

.. warning:: As the data has to be interpolated into higher resolution this
             operation might be very expensive and time-consuming (especially
             for huge datasets).

After that, you can simply add this step into your pipeline:

.. code-block:: python

    err_funcs = [ vst.HFEN(), vst.MAE() ]
 
    builder = vst.create_builder()
    (
        # setting of other parts is omitted
        .add_processing_step(vst.ErrorEvaluationStep(err_funcs))
    )

.. caution::
   The order of processing steps is important! If you want to apply some additional
   processing steps to the data **before** evaluating the error you have to add
   the error processing step as last!

After you will get following output on the ``stdout``:

.. code-block:: text

    --------------------------------------------------------------
    Error Evalution Report
    --------------------------------------------------------------
    - id: EMD-53130
      resolution: 1
      kind: volume
      channel_id: 0
      timestamp: '2026-10-26 14:11:01.139530'
      label:
      error_method: HFEN
      error: 0.5853609442710876
    - id: EMD-53130
      resolution: 1
      kind: volume
      channel_id: 0
      timestamp: '2026-10-26 14:11:01.153363'
      label:
      error_method: MAE
      error: 0.002249457873404026


It is also possible to add a custom label to run (it might indicate which
method was used, etc.) and reporting mechanism. This is especially useful if
you want to serialize the error evaluation results, for example in JSON:

.. code-block:: python

    err_funcs = [ vst.HFEN(), vst.MAE() ]
 
    builder = vst.create_builder()
    (
        # setting of other parts is omitted
        .add_processing_step(vst.ErrorEvaluationStep(
            err_funcs,
            reporter=vst.JSONErrorReporter("erorr_report.json"),
            label="some label",
        ))
    )

And then if you would open the ``error_report.json`` you should see something
similar to this:

.. code-block:: json

    [
      {
        "id": "EMD-53130",
        "resolution": 1,
        "kind": "volume",
        "channel_id": 0,
        "timestamp": "2026-10-26 14:16:11.808410",
        "label": "some label",
        "error_method": "HFEN",
        "error": 0.5853609442710876
      },
      {
        "id": "EMD-53130",
        "resolution": 1,
        "kind": "volume",
        "channel_id": 0,
        "timestamp": "2026-10-26 14:16:11.821515",
        "label": "some label",
        "error_method": "MAE",
        "error": 0.002249457873404026
      },
    ]

These design concepts are reflected in the design of the CLI:

.. code-block:: bash

   volsegtools process emd_53130.map \
     --error-func mae \
     --error-func hfen \
     --error-report-file error_report.json
