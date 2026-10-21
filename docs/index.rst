.. .. image:: ../images/banner.svg
..    :align: center

.. toctree::
   :maxdepth: 2
   :hidden:

   tutorial/index
   how-to/index
   api/index
   explanation/index

Welcome to VolsegTools documentation!
=====================================

**VolsegTools** is a Python library for building processing pipelines for
volumetric and segmentation data.

Its main goal is to create multi-resolution files so that the data can be
visualized in the browser (e.g., in the `Mol* Viewer <https://molstar.org/viewer/>`_)

Its main advantages are:

* Reading of: BinaryCIF, MRC/CCP4/MAP, OME-TIFF, OME-NGFF, Imaris, NIfTI and common mesh formats (OBJ, PLY, STL).

* Serialization into: MRC/CCP4/MAP, BinaryCIF, common mesh formats (OBJ, PLY, STL).

* Optional bundling into: MVSX, Zip or several Zip files per resolution.

.. grid:: 1 1 2 2
   :gutter: 3
 
   .. grid-item-card:: :octicon:`mortar-board` Tutorials
      :link: tutorial/index
      :link-type: doc
 
      New to VolsegTools? Install it and process your first volume
      step by step.
 
   .. grid-item-card:: :octicon:`tools` How-to guides
      :link: how-to/index
      :link-type: doc
 
      Recipes for specific tasks: other input formats, segmentations,
      choosing a downsampling strategy, measuring error.
 
   .. grid-item-card:: :octicon:`light-bulb` Explanation
      :link: explanation/index
      :link-type: doc
 
      How the pipeline works and why: stages, data model, and the
      trade-offs between downsampling strategies.
 
   .. grid-item-card:: :octicon:`code` API reference
      :link: api/index
      :link-type: doc
 
      Every public class and function, with parameters, return types
      and exceptions.

Quick-Start
-----------

.. code-block:: bash
 
   pip install volsegtools

After that you can use the builtin CLI application (in these examples we are
using the `EMD-53130 dataset from EMDB <https://www.ebi.ac.uk/emdb/EMD-53130>`_):

.. code-block:: bash

   molstar-preprocessor --vs EMD-53130.map --strategy tricubic --bundle mvsx --output-path out

Or you can write your own processing application using our Python API:
 
.. code-block:: python
 
   from pathlib import Path
   import volsegtools as vst
 
   pipeline = (
       vst.create_builder()
       .add_volume_converter(vst.MRCConverter())
       .set_downsampling_strategy(vst.TricubicInterpolation())
       .set_serializer(vst.DataKind.VOLUME, vst.BCIFSerializer())
       .set_bundler(vst.MVSXBundler())
       .set_output_dir(Path("out/"))
       .build()
   )
   pipeline.run(Path("emd_53130.map"))

.. note::

   This project is under active development.
