from tests.mocks import MockConverter, MockSerializer

import pytest

import volsegtools as vst


@pytest.fixture
def valid_builder():
    builder = vst.ProcessingPipelineBuilder()
    builder.add_volume_converter(MockConverter())
    builder.set_serializer(vst.DataKind.VOLUME, MockSerializer())
    return builder
