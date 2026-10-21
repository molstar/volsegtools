from __future__ import annotations

from pathlib import Path

import numpy as np
import numpy.typing as npt
import pytest


@pytest.fixture(scope="session")
def datasets() -> dict[str, Path]:
    root = Path(__file__).resolve().parent / "data" / "data"
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
