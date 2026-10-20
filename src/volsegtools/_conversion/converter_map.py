from pathlib import Path

import logging

from volsegtools.abc.converter import Converter

vst_logger = logging.getLogger("volsegtools")


class UnsupportedCompressionError(Exception):
    def __init__(self):
        super().__init__("Unsupported compression for this file type")


class ConverterMap:
    COMPRESSION_FILE_EXT = [
        "br",
        "bz2",
        "gz",
        "lz",
        "lz4",
        "rz",
        "xz",
    ]

    def __init__(self) -> None:
        self._suffix_to_converter_map: dict[str, Converter] = {}

    def _add_compression(self, suffix: str, converter: Converter) -> None:
        for ext in ConverterMap.COMPRESSION_FILE_EXT:
            self._suffix_to_converter_map[suffix + "." + ext] = converter

    def add_converter(self, converter: Converter) -> None:
        if len(converter.supported_suffixes) == 0:
            raise RuntimeError("Converter does not support any extensions")

        for suffix in converter.supported_suffixes:
            self.map_converter(converter, suffix)
            # self._suffix_to_converter_map[suffix] = converter
            # if converter.supports_compression:
            #     self._add_compression(suffix, converter)

    def map_converter(self, converter: Converter, suffix: str) -> None:
        if len(suffix) == 0:
            raise RuntimeError("Missing suffix for converter")

        self._suffix_to_converter_map[suffix] = converter

        if converter.supports_compression:
            self._add_compression(suffix, converter)

    def __getitem__(self, key: str | Path) -> Converter:
        # Conversion to filename for each input type
        filename = Path(str(key)).name.lower().lstrip(".")

        parts = filename.split(".")

        if len(parts) <= 1:
            return self._suffix_to_converter_map[filename]

        compression_ext = ConverterMap.COMPRESSION_FILE_EXT
        if parts[-1] in compression_ext:
            try:
                return self._suffix_to_converter_map[".".join(parts[-2:])]
            except KeyError as err:
                if parts[-2] not in self._suffix_to_converter_map:
                    raise err
                raise UnsupportedCompressionError() from None

        return self._suffix_to_converter_map[parts[-1]]

    def is_empty(self) -> bool:
        return len(self._suffix_to_converter_map.values()) == 0

    def __str__(self) -> str:
        return f"ConverterMap({self._suffix_to_converter_map!s})"


# class ConverterMap:
#     """"""
#
#     def __init__(self) -> None:
#         self._suffix_to_converter_map: dict[str, Converter] = {}
#
#     def set_converter(
#         self,
#         converter,
#         suffixes: list[str] | str | None = None,
#         force=False,
#     ) -> None:
#         for suffix in self.split_suffixes(suffixes):
#             if suffix in self._suffix_to_converter_map and not force:
#                 warnings.warn(
#                     f"Overwriting converter for suffix: {suffix}",
#                     RuntimeWarning,
#                     stacklevel=2,
#                 )
#             self._suffix_to_converter_map[suffix] = converter
#
#             if converter.supports_compression:
#                 self._suffix_to_converter_map[suffix + ".gz"] = converter
#                 self._suffix_to_converter_map[suffix + ".bz2"] = converter
#
#         if not suffixes:
#             if len(converter.supported_suffixes) == 0:
#                 raise RuntimeError("Converter does not have any supported suffixes!")
#             self.set_converter(converter, converter.supported_suffixes)
#
#     def is_empty(self) -> bool:
#         return len(self._suffix_to_converter_map.values()) == 0
#
#     def split_suffixes(self, suffixes):
#         if isinstance(suffixes, str):
#             return suffixes.split("|")
#         return suffixes
#
#     def get_converter(self, suffix) -> Converter:
#         # we are graceful for suffixes that start with a dot.
#         suffix = suffix.strip(".")
#         try:
#             return self._suffix_to_converter_map[suffix]
#         except KeyError:
#             if suffix.endswith(("gz", "bz2")):
#                 raise UnsupportedCompressionError() from None
#             raise
#
#     COMPRESSION_FILE_EXT = [
#         "br",
#         "bz2",
#         "gz",
#         "lz",
#         "lz4",
#         "rz",
#         "xz",
#     ]
#
#     def from_filepath(self, filepath: Path) -> Converter:
#         vst_logger.debug(f"Finding converter for '{filepath}'")
#         suffixes = filepath.suffixes
#         if len(suffixes) < 1:
#             raise RuntimeError("Cannot determine converter without file extension")
#
#         file_ext = suffixes[-1]
#
#         if len(suffixes) > 1:
#             vst_logger.debug(f"'{filepath}' probably is compressed.")
#             supported_ext = ConverterMap.COMPRESSION_FILE_EXT
#
#             if not suffixes[-1] in supported_ext:
#                 raise RuntimeError(
#                     f"Unknown compression type, known are: {supported_ext}"
#                 )
#
#             # The file extension is located before the compression type
#             file_ext = suffixes[-2]
#
#         return self.get_converter(file_ext)
#
#
#     def __getitem__(self, suffix) -> Converter:
#         return self.get_converter(suffix)
#
#     def __str__(self):
#         return str(self._suffix_to_converter_map)
