from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Self

import re

import pydantic

from volsegtools._core import AxisValues
from volsegtools._model import DataSetInfo, ResolutionInfo
from volsegtools._storage.resolution import Resolution

if TYPE_CHECKING:
    from collections.abc import Iterator

    from volsegtools._core.working_store import WorkingStore
    from volsegtools._storage.channel import Channel
    from volsegtools._storage.mesh import Mesh


class DataSet:
    def __init__(self, store: WorkingStore, metadata: DataSetInfo | None = None):
        self.store = store
        if metadata:
            self._metadata_is_set = True
            self.metadata = metadata
        else:
            self._metadata_is_set = False
            self.metadata = DataSetInfo()
        self.resolutions: list[Resolution] = []

    def __iter__(self) -> Iterator[Resolution]:
        yield from self.resolutions

    def __getitem__(self, idx: int) -> Resolution:
        return self.resolutions[idx]

    @property
    def zarr_path(self) -> Path:
        if self.metadata.kind.is_segmentation():
            root = Path("segmentation_data")
        else:
            root = Path("volume_data")
        return root / self.metadata.id

    def flat_channel_iter(self) -> Iterator[Channel]:
        """Iterator for all channels in each resolution."""
        for resolution in self.resolutions:
            yield from resolution.flat_channel_iter()

    def flat_mesh_iter(self) -> Iterator[Mesh]:
        """Iterator for all meshes in each resolution."""
        for resolution in self.resolutions:
            yield from resolution.flat_mesh_iter()

    def add_resolution(self, metadata: ResolutionInfo) -> Resolution:
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
                ResolutionInfo(
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


def create_file_name(data: Channel | Mesh, suffix: str = ".bcif") -> str:
    base_name = (
        f"{data.data_set.metadata.id}"
        f"_r{data.resolution.metadata.id}"
        f"_tf{data.time_frame.metadata.id}"
    )

    base_name += f"_{data.metadata.id}{suffix}"

    return base_name


class FileNameInfo(pydantic.BaseModel):
    data_set: str
    resolution: int
    time_frame: int
    channel: int
    suffix: str
    file_path: Path


def info_from_file_path(file_path: Path) -> FileNameInfo:
    file_name = file_path.name
    if file_name == "":
        raise RuntimeError(f"Encountered empty file name from: '{file_path}'")

    file_name_re = re.compile(
        r"(?P<set_id>.*)"
        r"_r(?P<resolution>\d+)"
        r"_tf(?P<time_frame>\d+)"
        r"_(?:ch|mesh)(?P<channel>\d+)"
        r"\.(?P<suffix>.*)$"
    )

    match = re.match(file_name_re, file_name)
    if match is None:
        raise RuntimeError("File name does not satisfy format!")

    return FileNameInfo(
        data_set=match.group("set_id"),
        resolution=int(match.group("resolution")),
        time_frame=int(match.group("time_frame")),
        channel=int(match.group("channel")),
        suffix=match.group("suffix"),
        file_path=file_path,
    )
