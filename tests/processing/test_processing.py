from pathlib import Path

from tests.mocks import (
    MockConverter,
    MockPostProcessingStep,
    MockSerializer,
)

import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "kind",
    [
        vst.DataKind.VOLUME,
        vst.DataKind.SEGMENTATION_VOLUME,
        vst.DataKind.SEGMENTATION_MESH,
        vst.DataKind.SEGMENTATION_MASK,
    ],
)
def test_pipeline_throws_if_converter_for_data_kind_not_present(
    tmp_path,
    kind,
):
    builder = vst.ProcessingPipelineBuilder()

    converter = MockConverter()
    serializer = MockSerializer()

    (builder.set_serializer(kind, serializer).set_local_store_path(Path(tmp_path)))

    if kind.is_segmentation():
        builder.add_segmentation_converter(converter)
    else:
        builder.add_volume_converter(converter)

    pipeline = builder.build()

    with pytest.raises(RuntimeError):
        pipeline.sync_process(
            volume_files=[] if kind.is_volume() else [Path("data.mock")],
            segmentation_files=[] if kind.is_segmentation() else [Path("data.mock")],
        )


def test_converter_is_called_once_per_file(tmp_path):
    builder = vst.ProcessingPipelineBuilder()

    volume_converter = MockConverter()
    segmentation_converter = MockConverter()
    serializer = MockSerializer()

    (
        builder.add_volume_converter(volume_converter)
        .add_segmentation_converter(segmentation_converter)
        .set_serializer(vst.DataKind.VOLUME, serializer)
        .set_local_store_path(Path(tmp_path))
    )

    pipeline = builder.build()
    pipeline.sync_process(
        volume_files=[Path("mock_vol_1.mock"), Path("mock_vol_2.mock")],
        segmentation_files=[Path("mock_seg_1.mock"), Path("mock_seg_2.mock")],
    )

    assert volume_converter.called_method_n("convert_volume", count=2)
    assert volume_converter.called_method_n("convert_segmentation", count=0)
    assert segmentation_converter.called_method_n("convert_volume", count=0)
    assert segmentation_converter.called_method_n("convert_segmentation", count=2)


def test_processing_step_is_called(tmp_path):
    builder = vst.ProcessingPipelineBuilder()

    converter = MockConverter()
    processing_step = MockPostProcessingStep()
    serializer = MockSerializer()

    (
        builder.add_volume_converter(converter)
        .add_post_process_step(processing_step)
        .set_serializer(vst.DataKind.VOLUME, serializer)
        .set_local_store_path(Path(tmp_path))
    )

    pipeline = builder.build()
    pipeline.sync_process(
        volume_files=[Path("mock_volume.mock")],
        segmentation_files=[],
    )

    assert processing_step.called_method("execute")


class StubMetadata:
    def __init__(self, kind):
        self.kind = kind
        self.id = "stub"
        self.resolution = 0

    def model_copy(self, deep):
        return self


class StubChannel:
    def __init__(self, parent):
        self.parent = parent


class StubDataset:
    def __init__(self, kind):
        self.metadata = StubMetadata(kind)
        self.shape = (1, 1, 1)

    def flat_channel_iter(self):
        return [StubChannel(self)]
