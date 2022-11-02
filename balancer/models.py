import datetime
from pydantic import BaseModel, UUID4
from pydantic.class_validators import Optional
from pydantic.validators import IntEnum


class WorkerStatus(IntEnum):
    """
    Статус воркера.
    """
    IDLE = 0,  # IDLE
    BUSY = 1,  # BUSY
    DEAD = 2  # DEAD


class TaskRequest(BaseModel):
    """
    Запрос на расчет.

    Attributes
    ----------
    payload: str
        Какая-то информация, нужная для расчета
    """
    payload: str


class TaskStatus(IntEnum):
    """
    Статус таски.
    """
    CREATED = 0,  # CREATED
    IN_PROGRESS = 1,  # IN_PROGRESS
    DONE = 2,  # DONE
    ERROR = 3  # ERROR


class Task(BaseModel):
    """
    Запрос на расчет.

    Attributes
    ----------
    uuid: UUID4
        Идентификатор таски
    date: Optional[datetime.datetime]
        Дата решения таски
    result: Optional[float]
        Результат решения таски
    payload: str
        Информация для решения таски
    status: TaskStatus
        Статус таски
    """
    uuid: UUID4
    date: Optional[datetime.datetime]
    result: Optional[float]
    payload: str
    status: TaskStatus
