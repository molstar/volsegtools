import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "extension", ["mnc", "nii", "PAR", "rst", "dcm", "HEAD", "tck", "trk"]
)
def test_valid_extensions(extension):
    assert extension in vst.NiiConverter().supported_suffixes
    assert vst.NiiConverter().is_suffix_supported(extension)


def test_compression_support():
    assert not vst.NiiConverter().supports_compression
