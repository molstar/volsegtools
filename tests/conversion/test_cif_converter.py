import pytest

import volsegtools as vst


@pytest.mark.parametrize("extension", ["bcif", "cif"])
def test_valid_extensions(extension):
    assert extension in vst.CIFConverter().supported_suffixes
    assert vst.CIFConverter().is_suffix_supported(extension)


def test_compression_support():
    assert not vst.CIFConverter().supports_compression
