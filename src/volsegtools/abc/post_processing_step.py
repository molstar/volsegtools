from typing import Protocol

from volsegtools._model import PipelineContext
from volsegtools._storage import DataSet


class PostProcessingStep(Protocol):
    async def execute(
        self,
        datasets: list[DataSet],
        context: PipelineContext,
    ) -> list[DataSet]: ...

    async def __call__(
        self,
        datasets: list[DataSet],
        context: PipelineContext,
    ) -> list[DataSet]:
        return await self.execute(datasets, context)
