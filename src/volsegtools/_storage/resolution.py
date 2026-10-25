from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from volsegtools._model import ResolutionMetadata
from volsegtools._storage.time_frame import TimeFrame

if TYPE_CHECKING:
    from collections.abc import Iterator

    from volsegtools._storage.channel import Channel
    from volsegtools._storage.data_set import DataSet
    from volsegtools._storage.mesh import Mesh


class Resolution:
    """A single resolution of a dataset.

    A dataset consists of resolutions (it is assumed that the input dataset
    is at the original resolution). Each resolution then contains its own set
    of time frames, each with its own channels and meshes.

    This means that datasets effectively are holding a resolution hierarchy.
    """

    def __init__(self, parent: DataSet, metadata: ResolutionMetadata | None = None):
        self.parent = parent
        self.metadata = metadata if metadata is not None else ResolutionMetadata()
        self.time_frames: list[TimeFrame] = []
        self._last_time_frame_num = 0

    @property
    def data_set(self) -> DataSet:
        return self.parent

    @property
    def zarr_path(self) -> Path:
        if self.data_set.metadata.kind.is_segmentation():
            root = Path("segmentation_data")
        else:
            root = Path("volume_data")
        return root / self.data_set.metadata.id / f"resolution_{self.metadata.id}"

    def __iter__(self) -> Iterator[TimeFrame]:
        yield from self.time_frames

    def flat_channel_iter(self) -> Iterator[Channel]:
        for frame in self.time_frames:
            yield from frame

    def flat_mesh_iter(self) -> Iterator[Mesh]:
        for frame in self.time_frames:
            yield from frame.meshes

    def add_time_frame(self, id: int = -1) -> TimeFrame:
        if id == -1:
            id = self._last_time_frame_num
            self._last_time_frame_num += 1

        # TODO: check that id is not present

        self.time_frames.append(TimeFrame(self, id))
        return self.time_frames[-1]

    def get_time_frame(self, id: int) -> tuple[TimeFrame, bool]:
        try:
            return self.time_frames[id], False
        except IndexError:
            return self.add_time_frame(id), True

    def __str__(self) -> str:
        return f"Resolution({self.metadata}, {self.time_frames})"

    def __repr__(self) -> str:
        return self.__str__()
