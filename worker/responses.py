from pydantic import BaseModel

from models import WorkerStatus


class BaseWorkerResponse(BaseModel):
    """
    Базовый ответ воркера

    Attributes
    ----------
    message: str
        Сообщение воркера.
    """
    message: str


class StatusResponse(BaseModel):
    """
    Ответ со статусом от воркера

    Attributes
    ----------
    status: WorkerStatus
        Статус воркера
    """
    status: WorkerStatus
