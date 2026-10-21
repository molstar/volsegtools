import pytest

import volsegtools as vst


@pytest.mark.parametrize("extension", ["txt", "csv", "npy", "npz"])
def test_valid_extensions(extension):
    assert extension in vst.NumpyConverter().supported_suffixes
    assert vst.NumpyConverter().is_suffix_supported(extension)


def test_compression_support():
    assert not vst.NumpyConverter().supports_compression
