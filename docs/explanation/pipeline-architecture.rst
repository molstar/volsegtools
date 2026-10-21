Pipeline Architecture
=====================

.. warning::

   This section of the documentation is under recent development

On this page you will learn what is the base architecture of the library and
how you can reason about it.

The whole library is based on a **pipeline architecture pattern**, where we
break the workflow into several stages. Each stage is independent from others
and its communication with the rest of the pipeline is based on its inputs and
outputs.

In volsegtools we take semi-structured approach to this: we have defined set of
stages that have well-defined interfaces and the user might provide their own
implementation of each stage, if they would deem it important. But the execution
is handled as a pipeline class that serves as an orchestrar for the workflow
execution.

The processing pipeline in volsegtools can be seen in the next figure:

.. image:: ../_static/pipeline_light.svg
   :class: only-light
   :align: center
   :alt: Pipeline Diagram

.. image:: ../_static/pipeline_dark.svg
   :class: only-dark
   :align: center
   :alt: Pipeline Diagram
