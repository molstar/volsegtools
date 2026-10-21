Converting between formats
==========================

In this tutorial you will learn how to use the volsegtools not only for
generation of resolution pyramids but also for conversion between formats.

Simply put, if there is implemeted working converter for format A and
serializer for format B, you can create a pipeline that is converting from A to
B.

**Expected result:** The EMD-53130 dataset in BinaryCIF format ready to be
visualized by `Mol* Viewer <https://molstar.org/viewer/>`_.

You should have installed the library. More about this can be found in the
:doc:`installation` section and possiblity the :doc:`quickstart` tutorial.

----

Download a sample dataset
-------------------------

We will use the `EMD-53130 <https://www.ebi.ac.uk/emdb/EMD-53130>`_, which is
cryo-EM density map from `EMDB <https://www.ebi.ac.uk/emdb/>`_.

Either manually download the archive with the `.map` file or you can use these
commands:

.. code-block:: bash

   wget https://ftp.ebi.ac.uk/pub/databases/emdb/structures/EMD-53130/map/emd_53130.map.gz
   gunzip emd_53130.map.gz

At the end of this step you should have the ``emd_53130.map`` file in your
working directory.

Run the converter
-----------------

Run this command to convert from the original MRC density map file to the
BinaryCIF.

.. code-block:: bash

   volsegtools convert emd_53130.map emd_53130.bcif

The CLI can automatically detect the target format from the file extension.
However, in situations where the format is supported, but you might want some
different extension you can call the command like this, specifying the
conversion format:

.. code-block:: bash

   volsegtools convert --force-format bcif emd_53130.map emd_53130.custom

Either way you should have the ``emd_53130.bcif`` or ``emd_53130.custom`` in
your working directory.
