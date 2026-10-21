import asyncio
import math

import pytest

import volsegtools as vst

volume_converter_cases = [
    ("mrc", vst.MRCConverter()),
    ("ccp4", vst.MRCConverter()),
    ("map", vst.MRCConverter()),
    ("mrc.gz", vst.MRCConverter()),
    ("ccp4.gz", vst.MRCConverter()),
    ("map.gz", vst.MRCConverter()),
    ("mrc.bz2", vst.MRCConverter()),
    ("ccp4.bz2", vst.MRCConverter()),
    ("map.bz2", vst.MRCConverter()),
    ("ims", vst.ImarisConverter()),
    ("ome.zarr", vst.NGFFConverter()),
]


@pytest.mark.parametrize(
    "extension, converter",
    volume_converter_cases,
    ids=[f"{f}-{type(c).__name__}" for (f, c) in volume_converter_cases],
)
def test_volume_conversion(datasets, stub_pipeline_context, extension, converter):
    result = asyncio.run(
        converter.convert_volume(datasets[f"volume.{extension}"], stub_pipeline_context)
    )
    dataset = result[0]
    assert dataset.metadata.filename == str(datasets[f"volume.{extension}"].resolve())
    assert len(dataset.resolutions) == 1
    assert dataset.resolutions[0].metadata.id == 0

    assert math.isclose(dataset.metadata.axis_order.x, 2.0)
    assert math.isclose(dataset.metadata.axis_order.y, 1.0)
    assert math.isclose(dataset.metadata.axis_order.z, 0.0)

    # For some formats the type of the floating number is changing, so we have
    # to increase the tolerance to create more sensible checking.
    assert math.isclose(dataset.resolutions[0].metadata.cell_size.x, 25.2, rel_tol=1e-05)
    assert math.isclose(dataset.resolutions[0].metadata.cell_size.y, 24.7, rel_tol=1e-05)
    assert math.isclose(dataset.resolutions[0].metadata.cell_size.z, 23.8, rel_tol=1e-05)

    assert math.isclose(dataset.metadata.origin.x, 1.0)
    assert math.isclose(dataset.metadata.origin.y, 2.0)
    assert math.isclose(dataset.metadata.origin.z, 3.0)

    assert dataset.metadata.id == "volume"

    assert dataset.metadata.kind == vst.DataKind.VOLUME

    assert math.isclose(dataset.resolutions[0].metadata.lattice_shape.x, 21.0)
    assert math.isclose(dataset.resolutions[0].metadata.lattice_shape.y, 19.0)
    assert math.isclose(dataset.resolutions[0].metadata.lattice_shape.z, 17.0)

    assert len(dataset.resolutions[0].time_frames) == 1
    time_frame = dataset.resolutions[0].time_frames[0]
    assert time_frame.metadata.id == 0

    assert len(time_frame.channels) == 1
    channel = time_frame.channels[0]
    assert channel.metadata.id == 0

    assert channel.metadata.statistics.mean == 0.22923025488853455
    assert channel.metadata.statistics.std == 0.2006988227367401
    assert channel.metadata.statistics.max == 1.0620758533477783
    assert channel.metadata.statistics.min == -0.1349763572216034


def test_numpy_volume_conversion(datasets, stub_pipeline_context, expected_volume_data):
    result = asyncio.run(
        vst.NumpyConverter().convert_volume(
            input_path=datasets["volume.npy"],
            context=stub_pipeline_context,
        )
    )
    dataset = result[0]
    handle = next(dataset.flat_channel_iter()).handle
    data = handle.get_lattice(vst.DaskBackend).compute()

    assert dataset.metadata.kind == vst.DataKind.VOLUME
    assert (data == expected_volume_data).all()


# TODO: Create "stubs" fixture that is just dictionary for different types
def test_numpy_segmentation_conversion(
    datasets, stub_pipeline_context, expected_segmentation_data
):
    result = asyncio.run(
        vst.NumpyConverter().convert_segmentation(
            input_path=datasets["segmentation.npy"],
            context=stub_pipeline_context,
        )
    )
    dataset = result[0]
    handle = next(dataset.flat_channel_iter()).handle
    data = handle.get_lattice(vst.DaskBackend).compute()

    assert dataset.metadata.kind == vst.DataKind.SEGMENTATION_VOLUME
    assert (data == expected_segmentation_data).all()


@pytest.mark.parametrize("extension", ["stl", "obj", "ply"])
def test_mesh_conversion(datasets, stub_pipeline_context, extension):
    result = asyncio.run(
        vst.MeshConverter().convert_segmentation(
            datasets[f"segmentation.{extension}"], stub_pipeline_context
        )
    )
    assert len(result) == 1
    assert result[0].metadata.kind == vst.DataKind.SEGMENTATION_MESH

    mesh = result[0].resolutions[0].time_frames[0].meshes[0]
    assert isinstance(mesh, vst.Mesh)

    stored = mesh.handle.zarr_object
    assert stored["vertices"].shape[1] == 3
    assert stored["faces"].shape[1] == 3
    assert stored["faces"].shape[0] > 0
