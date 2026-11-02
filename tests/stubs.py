from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


@dataclass
class Call:
    method: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class Spy:
    def __init__(self):
        self.calls: list[Call] = []

    def _record(self, method: str, *args, **kwargs):
        self.calls.append(Call(method, args, kwargs))

    @property
    def called(self) -> bool:
        return bool(self.calls)

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def last_call(self) -> Call | None:
        return self.calls[-1] if self.calls else None

    def calls_to(self, method: str) -> list[Call]:
        return [call for call in self.calls if call.method == method]

    def called_method(self, method: str) -> bool:
        return len(self.calls_to(method)) != 0

    def called_method_n(self, method: str, count: int = 1) -> bool:
        return bool(len(self.calls_to(method)) == count)

    def assert_called(self, method: str):
        assert self.called_method(method), f"{method!r} was not called"

    def assert_called_once(self, method: str):
        calls = self.calls_to(method)
        assert len(calls) == 1, f"Expected {method!r} once, got {len(calls)}"


class StubConverter(Spy):
    def __init__(
        self,
        *,
        volumes=None,
        segmentations=None,
        metadata=None,
        annotations=None,
        suffixes=None,
        compression=False,
    ):
        if suffixes is None:
            suffixes = ["mock"]
        super().__init__()

        self.volumes = volumes or []
        self.segmentations = segmentations or []
        self.metadata = metadata or []
        self.annotations = annotations or []
        self.suffixes = suffixes or []
        self.compression = compression

    @property
    def supported_suffixes(self):
        return self.suffixes

    def is_suffix_supported(self, suffix: str) -> bool:
        return suffix in self.supported_suffixes

    @property
    def supports_compression(self):
        return self.compression

    async def convert_volume(self, input_path, context):
        self._record("convert_volume", input_path, context)
        return self.volumes

    async def convert_segmentation(self, input_path, context):
        self._record("convert_segmentation", input_path, context)
        return self.segmentations

    async def collect_metadata(self, input_path, context):
        self._record("collect_metadata", input_path, context)
        return self.metadata

    async def collect_annotations(self, input_path, context):
        self._record("collect_annotations", input_path, context)
        return self.annotations


class StubSerializer(Spy):
    def __init__(self, filename="serialized.mock"):
        super().__init__()
        self.filename = filename

    async def serialize(self, data_set, output_path, context):
        self._record(
            "serialize",
            data_set,
            output_path,
            context,
        )

        output_path.mkdir(parents=True, exist_ok=True)

        result = output_path / self.filename
        result.write_text("mock serialized data")

        return [result]


class StubBundler(Spy):
    def __init__(self, filename="bundle.mock"):
        super().__init__()
        self.filename = filename

    def bundle(self, data_paths, output_path, context):
        self._record(
            "bundle",
            data_paths,
            output_path,
            context,
        )

        output_path.mkdir(parents=True, exist_ok=True)

        result = output_path / self.filename
        result.write_text("mock bundle")

        return [result]


class StubDownsamplingStrategy(Spy):
    def __init__(self, results: Iterable[Any] = ()):
        super().__init__()
        self.results = list(results)

    def execute(self, data, context):
        self._record("execute", data, context)

        yield from self.results


class StubPostProcessingStep(Spy):
    def __init__(self, result=None):
        super().__init__()
        self.result = result

    async def execute(self, datasets, context):
        self._record(
            "execute",
            datasets,
            context,
        )

        if self.result is not None:
            return self.result

        return datasets

    async def __call__(self, datasets, context):
        return await self.execute(datasets, context)


class StubPostConversionStep(Spy):
    def __init__(self, result=None):
        super().__init__()
        self.result = result

    async def execute(
        self,
        volumes,
        segmentations,
        metadata,
        annotations,
        context,
    ):
        self._record(
            "execute",
            volumes,
            segmentations,
            metadata,
            annotations,
            context,
        )

        if self.result is not None:
            return self.result

        # Reasonable no-op default
        return volumes + segmentations

    async def __call__(
        self,
        volumes,
        segmentations,
        metadata,
        annotations,
        context,
    ):
        return await self.execute(
            volumes,
            segmentations,
            metadata,
            annotations,
            context,
        )


class StubHandle:
    def __init__(
        self,
        nbytes: int = 0,
        data: npt.ArrayLike | None = None,
        zarr_object: Any | None = None,
    ):
        self.data = data
        self.zarr_object = zarr_object
        self.nbytes = int(np.asarray(data).nbytes) if data is not None else nbytes

    def get_lattice(self, backend=None) -> npt.ArrayLike:
        if self.data is None:
            raise RuntimeError("Stub handle does not contain any data")
        return self.data

    def calculate_statistics(self, backend=None):
        from volsegtools import DescriptiveStatistics

        if self.data is None:
            return DescriptiveStatistics()

        data = np.asarray(self.data)
        return DescriptiveStatistics(
            mean=float(np.mean(data)),
            std=float(np.std(data)),
            max=float(np.max(data)),
            min=float(np.min(data)),
        )


class StubMetadata:
    def __init__(self, kind=None, id="stub", resolution=0):
        self.kind = kind
        self.id = id
        self.resolution = resolution

    def model_copy(self, deep=False):
        return StubMetadata(
            kind=self.kind,
            id=self.id,
            resolution=self.resolution,
        )


class StubChannel:
    def __init__(
        self,
        parent=None,
        nbytes: int = 0,
        id: int = 0,
        data: npt.ArrayLike | None = None,
    ):
        self.parent = parent
        self.metadata = SimpleNamespace(id=id)
        self.handle = StubHandle(nbytes, data=data)

    @property
    def resolution(self):
        return self.parent.resolution if self.parent is not None else None

    @property
    def time_frame(self):
        return self.parent

    @property
    def data_set(self):
        return self.parent.data_set if self.parent is not None else None


class StubMesh:
    def __init__(self, parent=None, id: int = 0, data: Any | None = None):
        self.parent = parent
        self.metadata = SimpleNamespace(id=id)
        self.handle = StubHandle(data=data)

    @property
    def resolution(self):
        return self.parent.resolution if self.parent is not None else None

    @property
    def time_frame(self):
        return self.parent

    @property
    def data_set(self):
        return self.parent.data_set if self.parent is not None else None


class StubTimeFrame:
    def __init__(self, parent=None, id: int = 0):
        self.parent = parent
        self.metadata = SimpleNamespace(id=id)
        self.channels: list[StubChannel] = []
        self.meshes: list[StubMesh] = []

    def add_channel(self, id: int = -1) -> StubChannel:
        if id == -1:
            id = len(self.channels)
        channel = StubChannel(parent=self, id=id)
        self.channels.append(channel)
        return channel

    def add_mesh(self, id: int = -1) -> StubMesh:
        if id == -1:
            id = len(self.meshes)
        mesh = StubMesh(parent=self, id=id)
        self.meshes.append(mesh)
        return mesh

    @property
    def resolution(self):
        return self.parent

    @property
    def data_set(self):
        return self.parent.data_set if self.parent is not None else None

    def __iter__(self):
        yield from self.channels


class StubResolution:
    def __init__(self, parent=None, id: int = 0):
        self.parent = parent
        self.metadata = SimpleNamespace(id=id)
        self.time_frames: list[StubTimeFrame] = []

    def add_time_frame(self, id: int = -1) -> StubTimeFrame:
        if id == -1:
            id = len(self.time_frames)
        time_frame = StubTimeFrame(parent=self, id=id)
        self.time_frames.append(time_frame)
        return time_frame

    def flat_channel_iter(self):
        for time_frame in self.time_frames:
            yield from time_frame.channels

    def flat_mesh_iter(self):
        for time_frame in self.time_frames:
            yield from time_frame.meshes

    @property
    def data_set(self):
        return self.parent

    def __iter__(self):
        yield from self.time_frames


class StubDataset:
    def __init__(self, kind=None, nbytes: int = 0):
        self.metadata = StubMetadata(kind)
        self.resolutions: list[StubResolution] = []
        self.shape = (1, 1, 1)
        self._nbytes = nbytes

    def add_resolution(self, metadata=None) -> StubResolution:
        resolution = StubResolution(parent=self, id=len(self.resolutions))
        if metadata is not None:
            resolution.metadata = metadata
        self.resolutions.append(resolution)
        return resolution

    def flat_channel_iter(self):
        if not self.resolutions:
            yield StubChannel(parent=self, nbytes=self._nbytes)
            return

        for resolution in self.resolutions:
            yield from resolution.flat_channel_iter()

    def flat_mesh_iter(self):
        for resolution in self.resolutions:
            yield from resolution.flat_mesh_iter()

    def __iter__(self):
        yield from self.resolutions


class StubWorkingStore:
    def __init__(self, root: Path | None = None):
        self.root = root
