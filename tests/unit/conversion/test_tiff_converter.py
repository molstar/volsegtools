import pytest

import volsegtools as vst


@pytest.mark.parametrize("extension", ["ome.tiff", "tiff", "tif", "ome.tif"])
def test_valid_extensions(extension):
    assert extension in vst.TIFFConverter().supported_suffixes
    assert vst.TIFFConverter().is_suffix_supported(extension)


def test_compression_support():
    assert not vst.TIFFConverter().supports_compression
