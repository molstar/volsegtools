from tests.stubs import StubDataset, StubResolution

import pytest

import volsegtools as vst


@pytest.fixture
def valid_time_frame():
    return vst.TimeFrame(StubResolution(StubDataset()), 0)


@pytest.mark.parametrize("channel_id", [-1, 0, 1])
def test_valid_channel_addition(valid_time_frame, channel_id):
    channel = valid_time_frame.add_channel(channel_id)
    assert channel.metadata.id == channel_id


def test_adding_channels_without_id(valid_time_frame):
    channel = valid_time_frame.add_channel()
    assert channel.metadata.id == 0
    channel = valid_time_frame.add_channel()
    assert channel.metadata.id == 1
    channel = valid_time_frame.add_channel()
    assert channel.metadata.id == 2


def test_adding_already_present_channel_id_is_error(valid_time_frame):
    valid_time_frame.add_channel()
    with pytest.raises(RuntimeError):
        valid_time_frame.add_channel(0)
