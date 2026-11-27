import pydantic
import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "kind, expected",
    [
        (vst.DataKind.VOLUME, True),
        (vst.DataKind.SEGMENTATION_MASK, False),
        (vst.DataKind.SEGMENTATION_MESH, False),
        (vst.DataKind.SEGMENTATION_VOLUME, False),
    ],
)
def test_is_volume(kind, expected):
    assert kind.is_volume() == expected


@pytest.mark.parametrize(
    "kind, expected",
    [
        (vst.DataKind.VOLUME, False),
        (vst.DataKind.SEGMENTATION_MASK, True),
        (vst.DataKind.SEGMENTATION_MESH, True),
        (vst.DataKind.SEGMENTATION_VOLUME, True),
    ],
)
def test_is_segmentation(kind, expected):
    assert kind.is_segmentation() == expected


@pytest.mark.parametrize(
    "kind, serialized",
    [
        (vst.DataKind.VOLUME, "volume"),
        (vst.DataKind.SEGMENTATION_MASK, "segmentation_mask"),
        (vst.DataKind.SEGMENTATION_MESH, "segmentation_mesh"),
        (vst.DataKind.SEGMENTATION_VOLUME, "segmentation_volume"),
    ],
)
def test_serialization(kind, serialized):
    adapter = pydantic.TypeAdapter(vst.SerializableDataKind)
    assert adapter.dump_python(kind, mode="python") == serialized
