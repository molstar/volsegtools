Processing your first volume
============================

In this tutorial you will learn how to use the provide CLI for processing of
volumetric datasets.

**Expected result:** A downsampled `MVSX <https://molstar.org/mol-view-spec-docs/#mvsx>`_ archive from a real cryo-EM map,
ready to drag-and-drop into `Mol* Viewer <https://molstar.org/viewer/>`_.

You should have installed the library. More about this can be found in the
:doc:`installation` section.

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

Inspect the input
-----------------

It is always good idea to start with some inspection that will tell us more
about the data that we have at our disposal. Therefore, we run:

.. code-block:: bash

    volsegtools inspect ./EMD-53130.map

And we should get this result:

.. code-block:: yaml

    path: /home/user/workdir/EMD-53130.map
    size_in_mb: 160.006752
    possible_kind:
    - volume
    - segmentation_mask
    - segmentation_volume
    frames: 1
    data:
    - size_in_mb: 160.006752
      dimensions:
        x: 342
        y: 342
        z: 342
      origin:
        x: 0.0
        y: 0.0
        z: 0.0
      cell_size:
        x: 283.8599853515625
        y: 283.8599853515625
        z: 283.8599853515625
      units: unknown
      dtype: float32

Now we have some basic information about our dataset, we know its size,
possible kinds of data it might hold and its dimensions.

After that we can proceed to the processing

Run the processor
-----------------

The most important command is probably the processing one. It enables use to
generate resolution hierarchies for our data.

Run this command to generate two additional resolutions of the dataset:

.. code-block:: bash

   volsegtools process --resolutions 2 --bundle mvsx emd_53130.map

We are using the ``--resolutions N`` flag for telling the CLI application how
many resolutions of the data we want and ``--bundle mvsx`` to: (1) enabled
bundling in general and (2) say the want the data to be archived as `MVSX <https://molstar.org/mol-view-spec-docs/#mvsx>`_. 

Additionally, you might add the ``--verbose`` flag to be more informed about
the processing progress.

You can choose between various downsampling methods, to explore the possible
options you might run this command:

.. code-block:: bash

   volsegtools list-methods

Inspect the output
------------------

After the processing is finished the results are by default stored in the
working directory. Therefore, you should be able to following files:

* ``EMD-53130_r1_tf0_ch0.mrc``
* ``EMD-53130_r2_tf0_ch0.mrc``
* ``EMD-53130_r1.mvsx``
* ``EMD-53130_r2.mvsx``

Visualize the result
--------------------

Now, each of the files that are now at your disposal are dropable to the 
into the `Mol* Viewer <https://molstar.org/viewer/>`_.

Your results should look similarly to this (the default iso-value is set to 2,
it has to be adjusted for dataset manually).

.. grid:: 2

   .. grid-item::

      .. figure:: ../_static/emd_53130_original_iso.png
         :width: 100%

         EMD-53130 in Resolution 1

   .. grid-item::

      .. figure:: ../_static/emd_53130_adjusted_iso.png
         :width: 100%

         EMD-53130 in Resolution 1 with adjusted iso-value
