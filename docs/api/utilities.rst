Utilities
=========

.. currentmodule:: volsegtools

Units, sizes, timing and other helpers.

.. autosummary::
   :toctree: generated
   :nosignatures:

   AxisValues
   Bytes
   ChunkingMode
   UnitKind
   Gaussian3DKernel
   WorkingStore
   Timer
   TimerReporter
   JSONTimerReporter
   to_angstrom
   to_micrometer
   unit_from_str 


Bytes
-----

``Bytes`` represents a number of bytes with convenient support for
human-readable suffixes for increased brevity.

Suffix multipliers
------------------

It is possible to define the number of bytes using commonly known suffixes,
e.g. "10kib" is going to resulting into 10240 bytes. It does not matter whether
the suffix is in lower or upper case.

All supported suffixes are documented below:

.. list-table::
   :header-rows: 1

   * - Suffix
     - Multiplier
   * - B
     - 1
   * - KB
     - 10\ :sup:`3`
   * - MB
     - 10\ :sup:`6`
   * - GB
     - 10\ :sup:`9`
   * - TB
     - 10\ :sup:`12`
   * - KiB
     - 1024
   * - MiB
     - 1024\ :sup:`2`
   * - GiB
     - 1024\ :sup:`3`
   * - TiB
     - 1024\ :sup:`4`
