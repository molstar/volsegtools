from pathlib import Path

import re

import pydantic

from volsegtools._storage.channel import Channel
from volsegtools._storage.mesh import Mesh


def create_file_name(data: Channel | Mesh, suffix: str = ".bcif") -> str:
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
    data_set: str
    resolution: int
    time_frame: int
    channel: int
    suffix: str
    file_path: Path


def info_from_file_path(file_path: Path) -> FileNameInfo:
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
