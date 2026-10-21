import pytest

import volsegtools as vst


@pytest.mark.parametrize("extension", ["sff", "hff"])
def test_valid_extensions(extension):
    assert extension in vst.SFFConverter().supported_suffixes
    assert vst.SFFConverter().is_suffix_supported(extension)


def test_compression_support():
    assert not vst.SFFConverter().supports_compression
