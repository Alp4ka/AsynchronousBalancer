import asyncio

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from balancer import Balancer
from models import TaskRequest, Task
from responses import BaseBalancerResponse, WorkersLoadResponse, WorkerLoadResponse

app = FastAPI()
router = InferringRouter()
balancer = Balancer()


def get_balancer():
    return balancer


@cbv(router)
class BalancerView:
    _balancer: Balancer = Depends(get_balancer)

    @router.get("/ping")
    async def ping(self) -> BaseBalancerResponse:
        """
        Обработчик для пингов (тестовая ручка, заодно кубер хелсчек смог бы пробросить c:)
        :return:
        """
        return BaseBalancerResponse(message="pong")

    @router.post("/compute")
    async def compute(self, task_request: TaskRequest) -> Task:
        """
        Обработчик запроса расчета.
        :param task_request: TaskRequest
        :return: Task
        """
        task = await self._balancer.compute(task_request)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Task was failed due to internal server error!',
            )
        return task

    @router.get("/workers")
    async def workers_info(self) -> WorkersLoadResponse:
        """
        Получить информацию о загруженности воркеров.
        :return: WorkersLoadResponse
        """
        gathered = [asyncio.create_task(WorkerLoadResponse.from_worker(worker)) for worker in self._balancer.workers]
        workers_loads_results = await asyncio.gather(*gathered)
        return WorkersLoadResponse(workers=list(workers_loads_results))


app.include_router(router)
