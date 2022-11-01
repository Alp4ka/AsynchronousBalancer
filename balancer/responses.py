from pydantic import BaseModel
from pydantic.class_validators import List

from balancer import Worker
from models import WorkerStatus


class BaseBalancerResponse(BaseModel):
    """
    Базовый ответ балансера.

    Attributes
    ----------
    message: str
        Сообщение балансера
    """
    message: str


class WorkerLoadResponse(BaseModel):
    """
    Информация о загруженности воркера.

    Attributes
    ----------
    address : str
        Адрес endpoint'а
    number_of_connections: int
        Число единовременных подключений
    status: WorkerStatus
        Статус воркера

    Methods
    -------
    from_worker(worker:Worker) -> WorkerLoadResponse
        возвращает WorkerLoadResponse, используя экземпляр воркера.
    """
    address: str
    number_of_connections: int
    status: WorkerStatus

    @staticmethod
    async def from_worker(worker: Worker) -> 'WorkerLoadResponse':
        """
        Возвращает WorkerLoadResponse, используя данные экземпляра воркера.
        :param worker: Worker, воркер
        :return: WorkerLoadResponse
        """
        return WorkerLoadResponse(address=worker.address,
                                  number_of_connections=worker.number_of_connections,
                                  status=(await worker.status()))


class WorkersLoadResponse(BaseModel):
    """
    Информация о загруженности воркеров.

    Attributes
    ----------
    workers: List[WorkerLoadResponse]
        Список WorkerLoadResponse для всех воркеров
    """
    workers: List[WorkerLoadResponse]


