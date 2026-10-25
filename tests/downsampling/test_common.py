import pytest

import volsegtools as vst


class HandleStub:
    def __init__(self, nbytes):
        self.nbytes = nbytes


class ChannelStub(vst.Channel):
    def __init__(self, nbytes):
        self.handle = HandleStub(nbytes)


@pytest.mark.parametrize("channel", [ChannelStub(64_000), 64_000])
def test_calculate_approx_downsampled_sizes(channel):
    assert vst.calculate_approx_downsampled_sizes(channel, 10, 2) == [
        8_000,
        1_000,
        125,
        15.625,
    ]


@pytest.mark.parametrize("channel", [ChannelStub(64_000), 64_000])
def test_calculate_steps(channel):
    assert vst.calculate_steps(channel, 10, 2) == 4


@pytest.mark.parametrize("channel", [64_000, ChannelStub(64_000)])
@pytest.mark.parametrize(
    "threshold,expected_levels",
    [
        (10, [8000, 1000, 125, 15.625]),
        (100, [8000, 1000, 125]),
        (1_000, [8000, 1000]),
        (10_000, []),
    ],
)
def test_effect_of_threshold_on_sizes(channel, threshold, expected_levels):
    assert (
        vst.calculate_approx_downsampled_sizes(channel, threshold, 2)
        == expected_levels
    )


@pytest.mark.parametrize("channel", [64_000, ChannelStub(64_000)])
@pytest.mark.parametrize(
    "threshold,expected_levels",
    [
        (10, 4),
        (100, 3),
        (1_000, 2),
        (10_000, 0),
    ],
)
def test_effect_of_threshold_on_steps(channel, threshold, expected_levels):
    assert vst.calculate_steps(channel, threshold, 2) == expected_levels


@pytest.mark.parametrize("channel", [0, ChannelStub(0)])
@pytest.mark.parametrize("factor", [0, 1, -1])
def test_invalid_factor_in_sizes(channel, factor):
    with pytest.raises(RuntimeError):
        vst.calculate_approx_downsampled_sizes(channel, 1024, factor)


@pytest.mark.parametrize("channel", [0, ChannelStub(0)])
@pytest.mark.parametrize("factor", [0, 1, -1])
def test_invalid_factor_in_steps(channel, factor):
    with pytest.raises(RuntimeError):
        vst.calculate_steps(channel, 1024, factor)


@pytest.mark.parametrize("channel", [0, ChannelStub(0)])
@pytest.mark.parametrize("threshold", [0, -1])
def test_invalid_threshold_in_sizes(channel, threshold):
    with pytest.raises(RuntimeError):
        vst.calculate_approx_downsampled_sizes(channel, threshold, 2)


@pytest.mark.parametrize("channel", [0, ChannelStub(0)])
@pytest.mark.parametrize("threshold", [0, -1])
def test_invalid_threshold_in_steps(channel, threshold):
    with pytest.raises(RuntimeError):
        vst.calculate_steps(channel, threshold, 2)
