from pathlib import Path

import numpy as np
import pytest
import zarr
import zarr.storage

import volsegtools as vst


def test_local_store_uses_temporary_path(
    working_store: vst.WorkingStore, working_store_path: Path
) -> None:
    assert isinstance(working_store.data_store, zarr.storage.LocalStore)
    assert Path(working_store.data_store.root).resolve() == working_store_path.resolve()
    assert working_store_path.is_dir()


def test_memory_store_is_used_when_path_is_omitted(
    memory_working_store: vst.WorkingStore,
) -> None:
    assert isinstance(memory_working_store.data_store, zarr.storage.MemoryStore)


def test_root_and_data_groups_are_created(working_store: vst.WorkingStore) -> None:
    assert working_store.root_group.path == ""
    assert working_store.volume_data_group.path == "volume_data"
    assert working_store.segmentation_data_group.path == "segmentation_data"


@pytest.mark.parametrize("store_type_fixture", ["working_store", "memory_working_store"])
@pytest.mark.parametrize(
    ("kind", "group"),
    [
        (vst.DataKind.VOLUME, "volume_data"),
        (vst.DataKind.SEGMENTATION_VOLUME, "segmentation_data"),
        (vst.DataKind.SEGMENTATION_MASK, "segmentation_data"),
        (vst.DataKind.SEGMENTATION_MESH, "segmentation_data"),
    ],
)
def test_get_data_group(store_type_fixture, kind, group, request):
    store = request.getfixturevalue(store_type_fixture)
    assert store.get_data_group(kind).basename == group


def test_data_from_store_should_persist(working_store_path: Path) -> None:
    expected = np.arange(8, dtype=np.float32).reshape(2, 2, 2)
    first_store = vst.WorkingStore(working_store_path)
    group = first_store.volume_data_group.require_group(
        "dataset/resolution_0/time_frame_0"
    )
    group.create_array("channel_0", data=expected)

    reopened_store = vst.WorkingStore(working_store_path)
    reopened_group = reopened_store.volume_data_group.require_group(
        "dataset/resolution_0/time_frame_0"
    )

    np.testing.assert_array_equal(reopened_group["channel_0"][:], expected)
