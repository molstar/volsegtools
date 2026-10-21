Measuring Time
==============

Volsegtools is equiped with internal time measuring system. Thank to that it
is possible to find out how much time was spent in a single stage and which
events occured during each stage.

It is also possible to use this system in users' own implementation like this:

.. code-block:: python

   import logging
   import volsegtools as vst

   vst.logger.setLevel(level=logging.INFO)

But that applies only for the reuse of the timer for some arbitrary logic. Each
pipeline holds its own instance of the ``Timer`` class in its
``PipelineContext`` which is passed to each stage as defined in interfaces
found in the ``volsegtools.abc`` submodule.

.. note:: Each pipeline has its own timer for taking measurements.

Therefore, if you would be implementing some new stage you can use this
internal timer to mark events and stages:

.. code-block:: python

   import logging
   import volsegtools as vst

   vst.logger.setLevel(level=logging.INFO)
