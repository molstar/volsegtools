from tests.stubs import StubChannel

import numpy as np
import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "level",
    [
        vst.CompressionLevel.LOSSLESS,
        vst.CompressionLevel.LOW,
        vst.CompressionLevel.MEDIUM,
        vst.CompressionLevel.HIGH,
        vst.CompressionLevel.MAXIMUM,
    ],
)
def test_setting_compression_levels(level):
    serializer = vst.BCIFSerializer(level)
    assert serializer.level == level


@pytest.mark.parametrize(
    "dtype",
    [
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
        np.float16,
        np.float32,
        np.float64,
    ],
)
def test_calling_the_right_function(dtype, mocker):
    continuous_encoder = mocker.patch(
        "volsegtools.BCIFSerializer._continuous_volume_encoder"
    )
    discrete_encoder = mocker.patch("volsegtools.BCIFSerializer._discrete_volume_encoder")

    channel = StubChannel(dtype=dtype)
    vst.BCIFSerializer._choose_encoder(vst.CompressionLevel.LOSSLESS, channel)

    if np.issubdtype(dtype, np.integer):
        continuous_encoder.assert_not_called()
        discrete_encoder.assert_called_once()
    else:
        continuous_encoder.assert_called_once()
        discrete_encoder.assert_not_called()


def _info_values(axis_order, lattice_shape, origin):
    from types import SimpleNamespace

    from volsegtools._serialization.bcif_serializer import _VolumeData3DInfoDesc

    channel = SimpleNamespace(
        data_set=SimpleNamespace(
            metadata=SimpleNamespace(
                id="test",
                axis_order=vst.AxisValues(*axis_order),
                origin=vst.AxisValues(*origin),
            )
        ),
        resolution=SimpleNamespace(
            metadata=SimpleNamespace(
                id=0,
                lattice_shape=vst.AxisValues(*lattice_shape),
                cell_size=vst.AxisValues(1.0, 1.0, 1.0),
            )
        ),
        metadata=SimpleNamespace(
            statistics=SimpleNamespace(mean=0.0, std=1.0, min=-1.0, max=1.0)
        ),
    )
    fields = {f.name: f for f in _VolumeData3DInfoDesc.get_field_descriptors(channel)}
    return {name: field.value(None, 0) for name, field in fields.items()}


@pytest.mark.parametrize(
    ("axis_order", "expected_count", "expected_origin"),
    [
        ((0, 1, 2), (256, 360, 125), (1, 2, 3)),
        ((2, 1, 0), (125, 360, 256), (3, 2, 1)),
        ((1, 2, 0), (360, 125, 256), (2, 3, 1)),
    ],
)
def test_sample_count_and_origin_follow_axis_order(
    axis_order, expected_count, expected_origin
):
    """Mol* reads these in "axis order" (fast-to-slow), not in x, y, z order."""
    values = _info_values(axis_order, (256, 360, 125), (1, 2, 3))

    assert tuple(values[f"axis_order[{i}]"] for i in range(3)) == axis_order
    assert tuple(values[f"sample_count[{i}]"] for i in range(3)) == expected_count
    assert tuple(values[f"origin[{i}]"] for i in range(3)) == expected_origin
