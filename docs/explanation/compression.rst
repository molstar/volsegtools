Compression of Output files
===========================

The library is supporting serialization with several levels of compression
(if given serializer supports it).

The effects on the resulting data is dependent on the data, downsampling method
and the chosen level of compression. It is not possible to guess the resulting
effect on the size beforehand.

To give an example, these are the effects on size of the `EMD-53130
<https://www.ebi.ac.uk/emdb/EMD-53130>`_ downsampled via the tricubic method
and serialized as BinaryCIF (in this case the HIGH = MAXIMUM level):

.. list-table::
   :header-rows: 1

   * - Level
     - Resulting Size (MB)
   * - LOSSLESS
     - 20
   * - LOW
     - 5
   * - MEDIUM
     - 1.1
   * - HIGH / MAXIMUM
     - 0.106

We can see that the difference in size does not necesarrily be too visible in
the overall quality of the image on the figures below (showing the 1st
resolution of the dataset):

.. grid:: 1 2 3 4
   :gutter: 2

   .. grid-item::

      .. figure:: ../_static/emd_53130_lossless.png
         :width: 100%

         Lossless

   .. grid-item::

      .. figure:: ../_static/emd_53130_low.png
         :width: 100%

         Low

   .. grid-item::

      .. figure:: ../_static/emd_53130_medium.png
         :width: 100%

         Medium

   .. grid-item::

      .. figure:: ../_static/emd_53130_maximum.png
         :width: 100%

         High/Maximum

There is slight noticeable difference between lossless and low/medium. However,
the difference between low and medium is basically not noticeable while the
medium compression is producing almost 5x times smaller data! After that the
quality further deteriorates.
