import datetime
from pydantic import BaseModel, UUID4
from pydantic.class_validators import Optional
from pydantic.validators import IntEnum


class WorkerStatus(IntEnum):
    IDLE = 0
    BUSY = 1
    DEAD = 2


class TaskRequest(BaseModel):
    payload: str


class TaskStatus(IntEnum):
    CREATED = 0
    IN_PROGRESS = 1
    DONE = 2
    ERROR = 3


class Task(BaseModel):
    uuid: UUID4
    date: Optional[datetime.datetime]
    result: Optional[float]
    payload: str
    status: TaskStatus
