from pathlib import Path

import logging

import zarr
import zarr.storage

from volsegtools._core.data_kind import DataKind

vst_logger = logging.getLogger("volsegtools")


class WorkingStore:
    """Provides a temporary zarr storage for volume and segmentation data."""

    def __init__(self, store_path: Path | None = None):
        if store_path:
            vst_logger.debug(f"Creating a local store at: {store_path}")
            self.data_store = zarr.storage.LocalStore(root=store_path)
        else:
            self.data_store = zarr.storage.MemoryStore()
            vst_logger.debug(f"Creating a memory store as: {self.data_store}")

        self.root_group = zarr.open_group(store=self.data_store, mode="a")

    @property
    def volume_data_group(self) -> zarr.Group:
        """Returns the zarr group holding the volume data."""
        return self.root_group.require_group("volume_data")

    @property
    def segmentation_data_group(self) -> zarr.Group:
        """Returns the zarr group holding the segmentation data."""
        return self.root_group.require_group("segmentation_data")

    def get_data_group(self, lattice_kind: DataKind) -> zarr.Group:
        """Return the zarr group associated with a data kind.

        Parameters
        ----------
        lattice_kind : DataKind
            Kind of data for which the group should be returned.

        Returns
        -------
        zarr.Group
            ``volume_data_group`` for volume data and
            ``segmentation_data_group`` for every segmentation kind.
        """

        if lattice_kind.is_volume():
            return self.volume_data_group
        return self.segmentation_data_group
