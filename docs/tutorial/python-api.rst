Creating your first pipeline
============================

In the previous tutorial you have used a provided CLI application. This time,
you will define the pipeline with the same goal from scratch.

**Expected result:** A script defining a processing pipeline that is able to
create a downsampled MVSX archive of volumetric data encoded as MRC.

You should have installed the library. More about this can be found in the
:doc:`installation` section.

The format of this tutorial is as follows: (1) you will download a testing
dataset, (2) we will show you a complete implementation of the script, and (3)
we will explain each line to you as we will compose the script line-by-line.

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

Resulting Script
----------------

The resulting script of this tutorial is the ``process.py`` that contains the
following code:

.. code-block:: python
 
    import volsegtools as vst
    import sys

    builder = vst.create_builder()
    (
       .add_volume_converter(vst.MRCConverter())
       .set_downsampling_strategy(vst.TricubicInterpolation())
       .set_serializer(vst.DataKind.VOLUME, vst.BCIFSerializer())
       .set_bundler(vst.MVSXBundler())
       .set_output_dir("out")
    )
 
    pipeline = builder.build()
    pipeline.sync_run(sys.argv[1])

That you can run via the ``python`` executable:

.. code-block:: bash

   python process.py

After you ran the script you will find the resolution hierarchy encoded both as
BinaryCIF and MVSX in the ``out/`` directory.

----

Understanding each line
-----------------------

Now, we will describe what each important line of the script does, so that you
have the basic understanding of the library.

**1. Create the builder**

Defining the pipeline from scratch takes too much work and you have to check
many things. Therefore, we have provided you with the builder class that has
more invating syntax and does all the important checks.

.. code-block:: python

   vst.create_builder()

Returns a fresh instance of :class:`~volsegtools.ProcessingPipelineBuilder`.
Every subsequent call of methods of this instance is returning a reference to
itself, therefore, you can use method chaining while constructing the pipeline.

**2. Adding the converter**


