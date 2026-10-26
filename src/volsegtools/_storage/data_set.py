from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Self

from volsegtools._core import AxisValues
from volsegtools._model import DataSetMetadata, ResolutionMetadata
from volsegtools._storage.resolution import Resolution

if TYPE_CHECKING:
    from collections.abc import Iterator

    from volsegtools._core.working_store import WorkingStore
    from volsegtools._storage.channel import Channel
    from volsegtools._storage.mesh import Mesh


class DataSet:
    def __init__(self, store: WorkingStore, metadata: DataSetMetadata | None = None):
        self.store = store
        if metadata:
            self._metadata_is_set = True
            self.metadata = metadata
        else:
            self._metadata_is_set = False
            self.metadata = DataSetMetadata()
        self.resolutions: list[Resolution] = []

    def __iter__(self) -> Iterator[Resolution]:
        yield from self.resolutions

    def __getitem__(self, idx: int) -> Resolution:
        return self.resolutions[idx]

    @property
    def zarr_path(self) -> Path:
        root = Path(self.store.get_data_group(self.metadata.kind).path)
        return root / self.metadata.id

    def flat_channel_iter(self) -> Iterator[Channel]:
        """Iterator for all channels in each resolution."""
        for resolution in self.resolutions:
            yield from resolution.flat_channel_iter()

    def flat_mesh_iter(self) -> Iterator[Mesh]:
        """Iterator for all meshes in each resolution."""
        for resolution in self.resolutions:
            yield from resolution.flat_mesh_iter()

    def add_resolution(self, metadata: ResolutionMetadata) -> Resolution:
        """Adds a new resolution to the dataset.

        Parameters
        ----------
        metadata
            The metadata used for creation of a new resolution.

        Returns
        -------
        Resolution
            Reference to the newly created resolution stored in the dataset.
        """
        new_idx = len(self.resolutions)
        metadata.id = new_idx
        self.resolutions.append(Resolution(parent=self, metadata=metadata))
        return self.resolutions[-1]

    def get_resolution(self, idx: int) -> tuple[Resolution, bool]:
        try:
            return self[idx], False
        except IndexError:
            return self.add_resolution(
                ResolutionMetadata(
                    cell_size=AxisValues(0, 0, 0),
                    lattice_shape=AxisValues(0, 0, 0),
                )
            ), True

    def update_metadata(self, other: Self) -> None:
        """Updates missing parts of metadata from other data set.

        Generally, the other data set should contain the same data, but in
        different resolution.

        Only the metadata of the dataset are copied. The metadata for lower
        level structures (resolutions, time frames, etc.) are not shared
        between datasets and will **not** be copied.
        """
        if not self._metadata_is_set:
            self.metadata = other.metadata.model_copy(deep=True)
            self._metadata_is_set = True

    def __str__(self) -> str:
        return f"DataSet({self.metadata}, {self.resolutions})"

    def __repr__(self) -> str:
        return self.__str__()
