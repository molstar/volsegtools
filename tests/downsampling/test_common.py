import pytest

import volsegtools as vst


class HandleStub:
    def __init__(self, nbytes, shape):
        self.nbytes = nbytes
        self.shape = shape


class ChannelStub(vst.Channel):
    def __init__(self, nbytes, shape=()):
        self.handle = HandleStub(nbytes, shape)


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


@pytest.mark.parametrize("channel", [64_000, ChannelStub(64_000)])
@pytest.mark.parametrize(
    "factor, resolution, threshold",
    [
        (2, 2, 1000),
        (2, 3, 125),
        (2, 4, 15),
        (2, 5, 1),
        (3, 2, 87),
        (3, 3, 3),
    ],
)
def test_threshold_for_resolution(channel, factor, resolution, threshold):
    assert (
        vst.calculate_threshold_for_resolution(channel, resolution, factor) == threshold
    )


@pytest.mark.parametrize("channel", [0, ChannelStub(0)])
@pytest.mark.parametrize("resolution", [0, 1, -1])
def test_invalid_resolution_count_in_resolution_threshold(channel, resolution):
    with pytest.raises(RuntimeError):
        vst.calculate_threshold_for_resolution(channel, resolution)


@pytest.mark.parametrize("channel", [0, ChannelStub(0)])
@pytest.mark.parametrize("factor", [0, 1, -1])
def test_invalid_factor_in_resolution_threshold(channel, factor):
    with pytest.raises(RuntimeError):
        vst.calculate_threshold_for_resolution(channel, 2, factor)


@pytest.mark.parametrize("channel", [64_000, ChannelStub(64_000)])
@pytest.mark.parametrize(
    "factor, resolution_cnt",
    [
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 2),
        (3, 3),
    ],
)
def test_threshold_leads_to_correct_level_cnt(channel, factor, resolution_cnt):
    threshold = vst.calculate_threshold_for_resolution(channel, resolution_cnt, factor)
    sizes = vst.calculate_steps(channel, threshold, factor)
    assert resolution_cnt == sizes


@pytest.mark.parametrize("input", [(40, 40, 40), ChannelStub(64_000, (40, 40, 40))])
@pytest.mark.parametrize(
    "factor, dimensions",
    [
        (2, [(20, 20, 20), (10, 10, 10), (5, 5, 5), (2, 2, 2), (1, 1, 1)]),
        (3, [(13, 13, 13), (4, 4, 4), (1, 1, 1)]),
    ],
)
def test_calculation_of_dimensions(input, factor, dimensions):
    assert vst.calculate_dimensions(input, factor) == dimensions


@pytest.mark.parametrize("input", [(40, 40, 0), ChannelStub(64_000, (40, 40, 0))])
def test_calculation_of_dimensions_0_dimensions_returns_empty(input):
    assert vst.calculate_dimensions(input) == []


@pytest.mark.parametrize("channel", [0, ChannelStub(0)])
@pytest.mark.parametrize("factor", [0, 1, -1])
def test_invalid_factor_in_dimensions_calculation(channel, factor):
    with pytest.raises(RuntimeError):
        vst.calculate_dimensions(channel, factor)
