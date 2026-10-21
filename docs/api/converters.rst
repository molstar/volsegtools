Converters
==========

.. currentmodule:: volsegtools

Converters read an input format into the internal representation. Register them
with :meth:`ProcessingPipelineBuilder.add_volume_converter` or
:meth:`ProcessingPipelineBuilder.add_segmentation_converter`.

.. autosummary::
   :toctree: generated
   :nosignatures:

   MRCConverter
   TIFFConverter
   NGFFConverter
   ImarisConverter
   NiiConverter
   CIFConverter
   SFFConverter
   MeshConverter
   VRMLConverter
   ConverterMap
   UnsupportedCompressionError
