from __future__ import annotations

from pathlib import Path

import numpy as np
import numpy.typing as npt
import pytest

from tests.stubs import (
    StubBundler,
    StubChannel,
    StubConverter,
    StubDataset,
    StubDownsamplingStrategy,
    StubHandle,
    StubMesh,
    StubMetadata,
    StubPostConversionStep,
    StubPostProcessingStep,
    StubResolution,
    StubSerializer,
    StubTimeFrame,
    StubWorkingStore,
)


@pytest.fixture(scope="session")
def datasets() -> dict[str, Path]:
    root = Path(__file__).resolve().parent / "data"
    return {path.name: path for path in root.iterdir()}


@pytest.fixture(scope="session")
def expected_volume_data(datasets) -> npt.ArrayLike:
    return np.load(datasets["expected_volume_data.npy"])


@pytest.fixture(scope="session")
def expected_segmentation_data(datasets) -> npt.ArrayLike:
    return np.load(datasets["expected_segmentation_data.npy"])


@pytest.fixture
def stub_pipeline_context(tmp_path):
    """Isolated workspace with a threshold that produces one downsampling level."""
    from volsegtools import Bytes, Timer, WorkingStore
    from volsegtools._model import (
        PipelineContext,
        PipelineStageKind,
        PipelineState,
        PipelineStateManager,
    )

    state = PipelineStateManager(
        None,
        PipelineState(stage=PipelineStageKind.NOT_STARTED, msg=None),
    )
    return PipelineContext(
        timer=Timer(),
        working_store=WorkingStore(tmp_path / "working"),
        output_dir=tmp_path,
        state=state,
        size_threshold=Bytes(1024),
    )


"""
Factory fixture for stub classes.

This way we do not have to manually import the types to our tests and we can
centralize their creation (without affecting constructors).

"""


@pytest.fixture
def make_converter() -> type[StubConverter]:
    return StubConverter


@pytest.fixture
def make_serializer() -> type[StubSerializer]:
    return StubSerializer


@pytest.fixture
def make_bundler() -> type[StubBundler]:
    return StubBundler


@pytest.fixture
def make_downsampling_strategy() -> type[StubDownsamplingStrategy]:
    return StubDownsamplingStrategy


@pytest.fixture
def make_post_processing_step() -> type[StubPostProcessingStep]:
    return StubPostProcessingStep


@pytest.fixture
def make_post_conversion_step() -> type[StubPostConversionStep]:
    return StubPostConversionStep


@pytest.fixture
def make_metadata() -> type[StubMetadata]:
    return StubMetadata


@pytest.fixture
def make_channel() -> type[StubChannel]:
    return StubChannel


@pytest.fixture
def make_dataset() -> type[StubDataset]:
    return StubDataset


@pytest.fixture
def make_handle() -> type[StubHandle]:
    return StubHandle


@pytest.fixture
def make_resolution() -> type[StubResolution]:
    return StubResolution


@pytest.fixture
def make_time_frame() -> type[StubTimeFrame]:
    return StubTimeFrame


@pytest.fixture
def make_mesh() -> type[StubMesh]:
    return StubMesh


@pytest.fixture
def make_working_store() -> type[StubWorkingStore]:
    return StubWorkingStore
