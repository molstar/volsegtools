import pytest

import volsegtools as vst


def test_descriptive_statistics_default_values():
    stats = vst.DescriptiveStatistics()
    assert stats.mean == pytest.approx(0.0)
    assert stats.std == pytest.approx(0.0)
    assert stats.max == pytest.approx(0.0)
    assert stats.min == pytest.approx(0.0)


def test_channel_metadata_default_values():
    info = vst.ChannelMetadata()
    assert info.id == -1
    assert info.statistics.mean == pytest.approx(0.0)
    assert info.statistics.std == pytest.approx(0.0)
    assert info.statistics.max == pytest.approx(0.0)
    assert info.statistics.min == pytest.approx(0.0)


def test_mesh_metadata_default_values():
    info = vst.MeshMetadata()
    assert info.id == -1


def test_dataset_metadata_default_values():
    info = vst.DataSetMetadata()
    assert info.filename == "Unknown File"
    assert info.axis_order == vst.AxisValues(0, 0, 0)
    assert info.origin == vst.AxisValues(0, 0, 0)
    assert info.id == "Unknown"
    assert info.filename == "Unknown File"
    assert info.kind == vst.DataKind.VOLUME
    assert info.unit == vst.UnitKind.UNKNOWN


def test_resolution_metadata_default_values():
    info = vst.ResolutionMetadata()
    assert info.id == -1
    assert info.cell_size == vst.AxisValues(0, 0, 0)
    assert info.lattice_shape == vst.AxisValues(0, 0, 0)


def test_time_frame_metadata():
    info = vst.TimeFrameMetadata()
    assert info.id == -1


# I have been burned by not understanding the default implementation of
# pydantic models, so I am adding tests so that I am sure that I catch early
# any issues with them.


def test_descriptive_stastistics_construction():
    info = vst.DescriptiveStatistics(
        mean=1.0,
        std=2.0,
        max=3.0,
        min=4.0,
    )
    assert info.mean == pytest.approx(1.0)
    assert info.std == pytest.approx(2.0)
    assert info.max == pytest.approx(3.0)
    assert info.min == pytest.approx(4.0)


def test_channel_metadata_construction():
    info = vst.ChannelMetadata(
        id=42,
        statistics=vst.DescriptiveStatistics(
            mean=1.0,
            std=2.0,
            max=3.0,
            min=4.0,
        ),
    )
    assert info.id == 42
    assert info.statistics.mean == pytest.approx(1.0)
    assert info.statistics.std == pytest.approx(2.0)
    assert info.statistics.max == pytest.approx(3.0)
    assert info.statistics.min == pytest.approx(4.0)


def test_mesh_metadata_construction():
    info = vst.MeshMetadata(id=42)
    assert info.id == 42


def test_time_frame_metadata_construction():
    info = vst.TimeFrameMetadata(id=42)
    assert info.id == 42


def test_resolution_metadata_construction():
    info = vst.ResolutionMetadata(
        id=42,
        cell_size=vst.AxisValues(1, 2, 3),
        lattice_shape=vst.AxisValues(4, 5, 6),
    )
    assert info.id == 42
    assert info.cell_size == vst.AxisValues(1, 2, 3)
    assert info.lattice_shape == vst.AxisValues(4, 5, 6)


def test_dataset_metadata_construction():
    info = vst.DataSetMetadata(
        id="Testing",
        axis_order=vst.AxisValues(0, 1, 2),
        origin=vst.AxisValues(1, 2, 3),
        filename="/path/to/file",
        kind=vst.DataKind.SEGMENTATION_VOLUME,
        unit=vst.UnitKind.ANGSTROM,
    )
    assert info.id == "Testing"
    assert info.axis_order == vst.AxisValues(0, 1, 2)
    assert info.origin == vst.AxisValues(1, 2, 3)
    assert info.filename == "/path/to/file"
    assert info.kind == vst.DataKind.SEGMENTATION_VOLUME
    assert info.unit == vst.UnitKind.ANGSTROM
