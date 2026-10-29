import itertools

from tests.mocks import MockConverter, MockSerializer

import pytest
import zarr.storage

import volsegtools as vst


def generate_data_kind_permutations():
    data_kinds = [
        vst.DataKind.VOLUME,
        vst.DataKind.SEGMENTATION_MASK,
        vst.DataKind.SEGMENTATION_MESH,
        vst.DataKind.SEGMENTATION_VOLUME,
    ]

    results = []
    results += itertools.combinations(data_kinds, 1)
    results += itertools.combinations(data_kinds, 2)
    results += itertools.combinations(data_kinds, 3)
    results += itertools.combinations(data_kinds, 4)
    return results


@pytest.mark.parametrize(
    "data_kinds",
    [*generate_data_kind_permutations()],
    ids=lambda x: f"data_kinds={x}",
)
def test_valid_construction_with_serializer(data_kinds):
    builder = vst.ProcessingPipelineBuilder()
    builder.add_volume_converter(MockConverter())
    for kind in data_kinds:
        builder.set_serializer(MockSerializer(), kind)

    pipeline = builder.build()
    for kind in data_kinds:
        assert isinstance(pipeline._serializer_map[kind], MockSerializer)


# Downsampler Setting


@pytest.mark.parametrize(
    "data_kinds",
    [*generate_data_kind_permutations()],
    ids=lambda x: f"data_kinds={x}",
)
def test_it_is_possible_to_set_strategy_for_data_kind(valid_builder, data_kinds):
    for kind in data_kinds:
        valid_builder.set_downsampling_strategy(vst.NearestNeighbor(), kind)

    pipeline = valid_builder.build()

    for kind in data_kinds:
        assert isinstance(pipeline._downsampler_map[kind], vst.NearestNeighbor)


# Working store related tests


def test_default_building_should_use_memory_store(valid_builder):
    pipeline = valid_builder.build()
    assert isinstance(pipeline.working_store.data_store, zarr.storage.MemoryStore)


def test_using_default_local_store(valid_builder, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    valid_builder.use_local_store()

    expected_path = vst.ProcessingPipelineBuilder.DEFAULT_LOCAL_STORE_PATH

    assert not expected_path.exists()
    valid_builder.build()
    assert expected_path.exists()


def test_explicit_store_path_definition(valid_builder, tmp_path):
    local_store_path = tmp_path / "testing_working_store"

    valid_builder.set_local_store_path(local_store_path)

    assert not local_store_path.exists()

    valid_builder.build()

    assert local_store_path.is_dir()


def test_set_use_local_store_should_not_override_set_path(
    valid_builder, tmp_path, monkeypatch
):
    # We have to be located in temporary testing directory, otherwise it would
    # change the test outcome.
    monkeypatch.chdir(tmp_path)

    local_store_path = tmp_path / "testing_working_store"

    valid_builder.set_local_store_path(local_store_path)

    assert not local_store_path.exists()

    valid_builder.use_local_store()
    valid_builder.build()

    assert local_store_path.exists()
    assert not vst.ProcessingPipelineBuilder.DEFAULT_LOCAL_STORE_PATH.exists()


def test_explicit_store_path_should_override_default(
    valid_builder, tmp_path, monkeypatch
):
    # We have to be located in temporary testing directory, otherwise it would
    # change the test outcome.
    monkeypatch.chdir(tmp_path)

    local_store_path = tmp_path / "testing_working_store"

    valid_builder.use_local_store()
    valid_builder.set_local_store_path(local_store_path)
    valid_builder.build()

    assert local_store_path.exists()
    assert not vst.ProcessingPipelineBuilder.DEFAULT_LOCAL_STORE_PATH.exists()
