How to Control the Number of Resolutions
----------------------------------------

The main purpose of downsampling is to generate hierarchical resolution
pyramids that can be use further in visualization or processing workflows.

The library provides an approach to influence the number of resolutions that
will be generated.

Basically, the user has to set so-called ``size limit`` that serves as
lower-bound threshold for stopping methods. Each method is generating
resolutions that are smaller than the previous resolution using the ``factor``
(more about his can be found in :doc:`other how-tos </how-to/choose-method>`).

So if you would like to accept all resolutions bigger than let's say 2MB, then
you would construct a pipeline like this:

.. code-block:: python
 
    builder = vst.create_builder()
    (
        # setting of other parts is omitted
        .set_downsampling_size_threshold(vst.Bytes("2MB"))
    )

Particular parameters of the method can be found in :doc:`API reference
</api/pipeline>`.

However, this approach is not really ergonomic, because the user of the library
would then have to know how big each resolution is going to be. For this reason
you can builtin functions found in the :doc:`downsampling reference section
</api/downsampling>`.

So let's say that you would want to generate 4 resolution levels, then you
would write:

.. code-block:: python
 
    file_size = # ... caclulate size of the target file

    threshold = vst.calculate_threshold_for_resolution(file_size, 4)

    builder = vst.create_builder()
    (
        # setting of other parts is omitted
        .set_downsampling_size_threshold(threshold
    )


This design is reflected the in CLI and you can use either the ``--threshold``
or ``--resolutions`` flags:

.. caution::
   CLI flags ``--threshold`` and ``--resolutions`` are mutually exclusive! You
   have to choose only one, otherwise they processing run will fail with an
   error.

.. code-block:: bash

   volsegtools process --threshold 2MB emd_53130.map
   volsegtools process --resolutions 4 emd_53130.map
