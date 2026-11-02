import pytest

import volsegtools as vst


@pytest.fixture
def valid_builder(make_converter, make_serializer):
    builder = vst.ProcessingPipelineBuilder()
    builder.add_volume_converter(make_converter())
    builder.set_serializer(make_serializer(), vst.DataKind.VOLUME)
    return builder
