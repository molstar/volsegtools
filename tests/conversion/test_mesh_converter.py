import pytest

import volsegtools as vst


@pytest.mark.parametrize("extension", ["ply", "obj", "stl"])
def test_valid_extensions(extension):
    assert extension in vst.MeshConverter().supported_suffixes
    assert vst.MeshConverter().is_suffix_supported(extension)


def test_compression_support():
    assert not vst.MeshConverter().supports_compression
