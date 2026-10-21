User Guide
===========

.. grid:: 3

   .. grid-item::

      .. figure:: ../_static/emd_53130_r0.png
         :width: 100%

         Original Resolution (160MB)

   .. grid-item::

      .. figure:: ../_static/emd_53130_r1.png
         :width: 100%

         First level of downsampling (20MB)

   .. grid-item::

      .. figure:: ../_static/emd_53130_r2.png
         :width: 100%

         Second level of downsampling (2.5MB)

Installation
------------

Downsampling Break-Case
-----------------------

The main goal of a downsampling pipeline is to create several resolutions of
the input dataset.

Conversion Pipeline
-------------------

.. image:: ../_static/pipeline_light.svg
   :class: only-light
   :align: center
   :alt: Pipeline Diagram

.. image:: ../_static/pipeline_dark.svg
   :class: only-dark
   :align: center
   :alt: Pipeline Diagram

Thanks to the fact that only the Conversion and Serialization stage are
required you might define a pipeline like this:

.. code-block:: python

   builder = vst.create_builder()
   (
       builder.set_converter(vst.MRCConverter())
       builder.set_serializer(vst.BCIFSerializer())
   )
   pipeline = builder.build()

Which effectively creates a pipeline that converts data from the MRC/CCP4
format to BinaryCIF.

So the library does not work only for preprocessing in terms of downsampling,
but it also can work as a conversion library.

Therefore, if you would implement your own serializer or converter for your
particular format you can use volsegtools to convert various formats into your
own format.

Resolution Error Checking
-------------------------

Each additional downsampling is introducing some degree of error. It is
possible to use the built-in class ErrorCheck for estimating how high is that
error.

I

.. toctree::
   :maxdepth: 2

   pipeline.rst
   state_change.rst
   error_evaluation.rst
   logging.rst
   timing.rst
