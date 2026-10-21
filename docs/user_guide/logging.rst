Logging
========

Internally the ``volsegtools`` is using its own logger. Therefore, it is
possible to have fine-grained control over it.

So you might change the default level using:

.. code-block:: python

   import logging
   import volsegtools as vst

   vst.logger.setLevel(level=logging.INFO)

You can also introduce new handlers or formatters.
