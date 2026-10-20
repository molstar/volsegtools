import itertools

from tests.mocks import MockConverter

import pytest

import volsegtools as vst


def test_empty_converter():
    converter_map = vst.ConverterMap()
    assert converter_map.is_empty()


def test_non_empty_converter():
    converter_map = vst.ConverterMap()
    converter_map.add_converter(MockConverter())
    assert not converter_map.is_empty()


def test_str_empty_converter():
    converter_map = vst.ConverterMap()
    assert str(converter_map) == "ConverterMap({})"


def test_str_converter():
    converter_map = vst.ConverterMap()
    converter = MockConverter()
    converter_map.add_converter(converter)
    test_dict = {"mock": converter}
    assert str(converter_map) == f"ConverterMap({test_dict})"


@pytest.mark.parametrize(
    "extensions,converter",
    [
        (["mock"], MockConverter()),
        (["abc", "def"], MockConverter(suffixes=["abc", "def"])),
    ],
)
def test_adding_converters(extensions, converter):
    converter_map = vst.ConverterMap()
    converter_map.add_converter(converter)
    for ext in extensions:
        assert converter_map[ext] == converter


@pytest.mark.parametrize(
    "extensions,converter",
    [
        (["mock"], MockConverter(compression=True)),
        (["abc", "def"], MockConverter(suffixes=["abc", "def"], compression=True)),
    ],
)
def test_adding_converters_with_compression_support(extensions, converter):
    converter_map = vst.ConverterMap()
    converter_map.add_converter(converter)
    compressed_extensions = [
        ext + "." + compression
        for ext, compression in itertools.product(
            extensions, vst.ConverterMap.COMPRESSION_FILE_EXT
        )
    ]
    for ext in compressed_extensions:
        assert converter_map[ext] == converter


def test_adding_converter_without_suffix():
    converter_map = vst.ConverterMap()
    with pytest.raises(RuntimeError):
        converter_map.add_converter(MockConverter(suffixes=[]))


def test_mapping_converter():
    converter_map = vst.ConverterMap()
    converter = MockConverter(suffixes=["abc", "def"])
    converter_map.add_converter(converter)
    converter_map.map_converter(converter, "ghi")
    for ext in ["abc", "def", "ghi"]:
        assert converter_map[ext] == converter


def test_mapping_converter_with_empty_suffix():
    converter_map = vst.ConverterMap()
    with pytest.raises(RuntimeError):
        converter_map.map_converter(MockConverter(), "")


@pytest.mark.parametrize(
    "compression",
    vst.ConverterMap.COMPRESSION_FILE_EXT,
)
def test_unsupported_compression_for_converter(compression):
    converter_map = vst.ConverterMap()
    converter_map.add_converter(MockConverter())
    with pytest.raises(vst.UnsupportedCompressionError):
        converter_map["mock." + compression]


@pytest.mark.parametrize(
    "input",
    [
        "mock",
        ".mock",
        "some.mock",
        "some.path.mock",
        "double..mock",
        ".complex..hidden.path.mock",
        *["mock." + c for c in vst.ConverterMap.COMPRESSION_FILE_EXT],
        *["some.path.mock." + c for c in vst.ConverterMap.COMPRESSION_FILE_EXT],
        *["double..mock." + c for c in vst.ConverterMap.COMPRESSION_FILE_EXT],
    ],
)
def test_converter_map_with_valid_inputs(input):
    converter_map = vst.ConverterMap()
    converter = MockConverter(compression=True)
    converter_map.add_converter(converter)
    assert converter_map[input] == converter


@pytest.mark.parametrize(
    "input",
    [
        "",
        ".",
        "mock.error",
        *["mock.error." + c for c in vst.ConverterMap.COMPRESSION_FILE_EXT],
    ],
)
def test_converter_map_with_invalid_inputs(input):
    converter_map = vst.ConverterMap()
    converter = MockConverter(compression=True)
    converter_map.add_converter(converter)
    with pytest.raises(KeyError):
        converter_map[input]


def test_map_overwrites_converter():
    converter_map = vst.ConverterMap()
    converter1 = MockConverter()
    converter2 = MockConverter()

    converter_map.add_converter(converter1)
    assert converter_map["mock"] == converter1

    converter_map.map_converter(converter2, "mock")
    assert converter_map["mock"] == converter2


def test_add_overwrites_converter():
    converter_map = vst.ConverterMap()
    converter1 = MockConverter()
    converter2 = MockConverter()

    converter_map.map_converter(converter1, "mock")
    assert converter_map["mock"] == converter1

    converter_map.add_converter(converter2)
    assert converter_map["mock"] == converter2
