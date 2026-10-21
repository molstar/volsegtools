from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


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


class MockConverter(Spy):
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


class MockSerializer(Spy):
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


class MockBundler(Spy):
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


class MockDownsamplingStrategy(Spy):
    def __init__(self, results: Iterable[Any] = ()):
        super().__init__()
        self.results = list(results)

    def execute(self, data, context):
        self._record("execute", data, context)

        yield from self.results


class MockPostProcessingStep(Spy):
    def __init__(self, result=None):
        super().__init__()
        self.result = result

    async def execute(self, data_sets, context):
        self._record(
            "execute",
            data_sets,
            context,
        )

        if self.result is not None:
            return self.result

        return data_sets

    async def __call__(self, data_sets, context):
        return await self.execute(data_sets, context)


class MockPostConversionStep(Spy):
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
