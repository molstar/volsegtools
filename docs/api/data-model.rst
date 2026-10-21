Data model
==========

.. currentmodule:: volsegtools

Types that hold data and metadata as they move through the pipeline.

.. toctree::
   :maxdepth: 1

   metadata

.. autosummary::
   :toctree: generated
   :nosignatures:

   DataSet
   Resolution
   Channel
   TimeFrame
   Mesh
   DataHandle
   PipelineContext
   PipelineStageKind
   DataKind
   create_file_name
   info_from_file_path
   FileNameInfo

Backends
--------

In order to create the data in structured way, you have to either implement
a :class:`~volsegtools.abc.ComputationBackend`, or you can use one of the
builtin variants:

.. autosummary::
   :toctree: generated
   :nosignatures:

   DaskBackend
   NumPyBackend
   MeshBackend
