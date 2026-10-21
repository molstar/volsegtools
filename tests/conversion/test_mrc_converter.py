import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "extension",
    [
        "mrc",
        "map",
        "ccp4",
    ],
)
def test_valid_extensions(extension):
    assert extension in vst.MRCConverter().supported_suffixes
    assert vst.MRCConverter().is_suffix_supported(extension)


def test_compression_support():
    assert vst.MRCConverter().supports_compression
