import asyncio
import logging
import uuid
import sys

from pydantic.annotated_types import Dict

from models import TaskRequest, Task, WorkerStatus, TaskStatus
from utils import simulate_computation

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger = logging.getLogger("Worker")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Worker:
    _tasks: Dict[str, Task]
    _active_connection_num: int

    def __init__(self):
        self._tasks = {}
        self._active_connection_num = 0

    @property
    def tasks(self):
        return self._tasks

    async def compute(self, task_request: TaskRequest) -> Task:
        self._active_connection_num += 1
        logger.info(f"Active connections: {self._active_connection_num}.")

        task = Task(uuid=uuid.uuid4(),
                    payload=task_request.payload,
                    status=TaskStatus.CREATED)
        self._tasks[str(task.uuid)] = task

        logger.info(f"Computation for task {task.uuid} started!")
        await simulate_computation(task)
        logger.info(f"Computation for task {task.uuid} done!")

        self._active_connection_num -= 1
        logger.info(f"Active connections: {self._active_connection_num}.")

        return task

    @property
    def status(self):
        if self._active_connection_num > 0:
            return WorkerStatus.BUSY
        else:
            return WorkerStatus.IDLE

    async def periodically_log_connections(self, period: int):
        logger.info(f"[Scheduled Message] Periodically logging connections every {period} seconds.")
        while True:
            await asyncio.sleep(period)
            logger.info(f"[Scheduled Message] Active connections: {self._active_connection_num}.")
