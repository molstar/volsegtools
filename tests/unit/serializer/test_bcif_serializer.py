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
