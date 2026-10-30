from pathlib import Path

import re

import pydantic

from volsegtools._storage.channel import Channel
from volsegtools._storage.mesh import Mesh


def create_file_name(data: Channel | Mesh, suffix: str = ".bcif") -> str:
    """Creates a standardized name of a file for serialization.

    The format of the name is **expected** by the rest of the pipeline.

    Parameters
    ----------
    data
        The data that should be held by the file.
        We are distinguishing between channels and meshes.
    suffix
        What should be the suffix of the filename.
    Returns
    -------
    str
        standardized name of the file.
    """
    base_name = (
        f"{data.data_set.metadata.id}"
        f"_r{data.resolution.metadata.id}"
        f"_tf{data.time_frame.metadata.id}"
    )

    if isinstance(data, Channel):
        base_name += f"_ch{data.metadata.id}{suffix}"
    else:
        base_name += f"_mesh{data.metadata.id}{suffix}"

    return base_name


class FileNameInfo(pydantic.BaseModel):
    """Basic information about a file from a its name."""

    data_set: str
    """Name of the dataset associated with this file."""
    resolution: int
    """ID of the resolution in this file."""
    time_frame: int
    """ID of the frame in this file."""
    channel: int
    """ID of the channel in this file."""
    suffix: str
    """Suffix of the file."""
    file_path: Path
    """Path to the file."""


def info_from_file_path(file_path: Path) -> FileNameInfo:
    """Produces a file info from given path.

    Paramters
    ---------
    file_path
        Path to the file that should be analysed.

    Raises
    ------
    RuntimeError
        If the file path is not of the standard format expected by the library.

    Returns
    -------
    FileNameInfo
        Information about the provided file from its name.
    """
    file_name = file_path.name
    if file_name == "":
        raise RuntimeError(f"Encountered empty file name from: '{file_path}'")

    file_name_re = re.compile(
        r"(?P<set_id>.*)"
        r"_r(?P<resolution>\d+)"
        r"_tf(?P<time_frame>\d+)"
        r"_(?:ch|mesh)(?P<channel>\d+)"
        r"\.(?P<suffix>.*)$"
    )

    match = re.match(file_name_re, file_name)
    if match is None:
        raise RuntimeError("File name does not satisfy format!")

    return FileNameInfo(
        data_set=match.group("set_id"),
        resolution=int(match.group("resolution")),
        time_frame=int(match.group("time_frame")),
        channel=int(match.group("channel")),
        suffix=match.group("suffix"),
        file_path=file_path,
    )
