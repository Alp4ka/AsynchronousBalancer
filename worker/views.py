from fastapi import FastAPI, Depends
from pydantic import UUID4
from pydantic.class_validators import Optional, List

from responses import BaseWorkerResponse, StatusResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from models import TaskRequest, Task
from worker import Worker

app = FastAPI()
router = InferringRouter()
worker = Worker()


def get_worker() -> Worker:
    return worker


@cbv(router)
class WorkerView:
    _worker: Worker = Depends(get_worker)

    @router.get("/ping")
    async def ping(self) -> BaseWorkerResponse:
        return BaseWorkerResponse(message="pong")

    @router.post("/compute")
    async def compute(self, task_request: TaskRequest) -> Task:
        result = await self._worker.compute(task_request)
        return result

    @router.get("/task/{task_uuid}/")
    async def get_task(self, task_uuid: UUID4) -> Optional[Task]:
        return self._worker.tasks.get(str(task_uuid), None)

    @router.get("/task/")
    async def get_tasks(self) -> List[Task]:
        return list(self._worker.tasks.values())

    @router.get("/status")
    async def status(self) -> StatusResponse:
        return StatusResponse(status=self._worker.status)


app.include_router(router)
