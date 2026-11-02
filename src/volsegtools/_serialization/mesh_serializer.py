from collections.abc import Callable
from pathlib import Path

import logging

from volsegtools._model.pipeline_state import PipelineContext
from volsegtools._processing import MeshBackend
from volsegtools._storage import DataSet, create_file_name
from volsegtools.abc import Serializer
from volsegtools.typing import MeshType

vst_logger = logging.getLogger("volsegtools")


type MeshSerializationFunction = Callable[[Path, str, MeshType], str]

# TODO: all of the files below have similar code, I could make private generator
# for them to create closures in the specialized classes...


def _serialize_mesh(suffix: str) -> MeshSerializationFunction:
    def _serialize(output_path: Path, filename: str, mesh: MeshType) -> str:
        file_path = f"{output_path}/{filename}.{suffix}"
        mesh.export(file_path, suffix)
        return file_path

    return _serialize


class MeshSerializer(Serializer):
    """Serializes mesh formats to files."""

    def __init__(self, mesh_serialization_fn: MeshSerializationFunction):
        """Inits the MeshSerializer.

        Parameters
        ----------
        mesh_serializer_fn
            Function that shall be used for serialization of meshes.
        """
        self.serialization_fn = mesh_serialization_fn

    async def serialize(
        self,
        data_set: DataSet,
        output_path: Path,
        context: PipelineContext,
    ) -> list[Path]:
        output_files = []

        for mesh in data_set.flat_mesh_iter():
            mesh_data = mesh.handle.get_mesh(MeshBackend)

            # We need empty extension, because it is going to be filled in by a
            # particular serialization function.
            file_name = create_file_name(mesh, "")

            output = self.serialization_fn(
                output_path,
                file_name,
                mesh_data,
            )
            vst_logger.info(f"... serialized into {output}")
            output_files.append(output)

        return output_files


class OBJSerializer(MeshSerializer):
    def __init__(self):
        super().__init__(_serialize_mesh("obj"))


class PLYSerializer(MeshSerializer):
    def __init__(self):
        super().__init__(_serialize_mesh("ply"))


class STLSerializer(MeshSerializer):
    def __init__(self):
        super().__init__(_serialize_mesh("stl"))
