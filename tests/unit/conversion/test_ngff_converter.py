import pytest

import volsegtools as vst


@pytest.mark.parametrize("extension", ["zarr", "ome.zarr"])
def test_valid_extensions(extension):
    assert extension in vst.NGFFConverter().supported_suffixes
    assert vst.NGFFConverter().is_suffix_supported(extension)


def test_compression_support():
    assert not vst.NGFFConverter().supports_compression
